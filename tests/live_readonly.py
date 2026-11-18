"""Operator-driven live test: password via getpass only; no VM mutations."""
import getpass
import json
import tempfile
from flagship_web.backend import PoolConnection

host=input('HTTPS endpoint: ').strip()
pin=input('Independently verified SHA-256 fingerprint: ').strip()
username=input('XAPI username: ').strip()
password=getpass.getpass('XAPI password: ')
with tempfile.TemporaryDirectory() as journal:
    pool=PoolConnection(host,username,password,pin,journal)
    del password
    try:
        records,errors=pool.inventory()
        assert records['host'] and records['pool'], 'No hosts or singleton pool returned'
        assert not errors, errors
        print(json.dumps(dict(result='PASS',counts={k:len(v) for k,v in records.items()},tls=pool.client.tls_mode,mutations=0)))
    finally:
        pool.close()
