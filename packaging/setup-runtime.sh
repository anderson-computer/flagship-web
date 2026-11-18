#!/bin/bash
set -euo pipefail
umask 022
python3 -m venv /opt/flagship-web/venv
/opt/flagship-web/venv/bin/pip install --no-index --only-binary=:all: --find-links=/opt/flagship-web/wheels -r /opt/flagship-web/requirements.lock
/opt/flagship-web/venv/bin/pip check
install -d -m 0750 -o root -g flagship-web /etc/flagship-web
install -d -m 0700 -o flagship-web -g flagship-web /var/lib/flagship-web /var/lib/flagship-web/journals
/opt/flagship-web/venv/bin/python - <<'PY'
import json,os,pwd,secrets
from pathlib import Path
from werkzeug.security import generate_password_hash
account=pwd.getpwnam('flagship-web')
def create(path,text,mode,group):
    try:fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
    except FileExistsError:return
    with os.fdopen(fd,'w') as out:out.write(text)
    os.chown(path,0,group)
create('/etc/flagship-web/session.key',secrets.token_hex(32)+'\n',0o640,account.pw_gid)
if not Path('/etc/flagship-web/auth.json').exists():
    password=secrets.token_urlsafe(24)
    create('/etc/flagship-web/auth.json',json.dumps(dict(username='admin',password_hash=generate_password_hash(password)),indent=2)+'\n',0o640,account.pw_gid)
    create('/var/lib/flagship-web/admin.password',password+'\n',0o600,0)
PY
echo 'Flagship Web installed. Privately read /var/lib/flagship-web/admin.password as root. Follow INSTALL.md to start the service and SSH tunnel.'
