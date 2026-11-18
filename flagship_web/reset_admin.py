"""Interactive root-only console password reset. Stop/restart service around use."""
import getpass
import json
import os
from pathlib import Path
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    if os.geteuid() != 0:
        raise SystemExit('Run as root after stopping flagship-web.service.')
    password=getpass.getpass('New console password (at least 12 characters): ')
    if len(password)<12 or password!=getpass.getpass('Confirm password: '):
        raise SystemExit('Password too short or confirmation did not match; nothing changed.')
    path=Path('/etc/flagship-web/auth.json')
    data=json.loads(path.read_text())
    data['password_hash']=generate_password_hash(password)
    temporary=path.with_name('.auth.json.new')
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o640)
    try:
        with os.fdopen(fd,'w') as out:
            json.dump(data,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
        os.chown(temporary,0,path.stat().st_gid)
        os.replace(temporary,path)
    finally:
        temporary.unlink(missing_ok=True)
    Path('/var/lib/flagship-web/admin.password').unlink(missing_ok=True)
    print('Password reset. Restart flagship-web.service.')
