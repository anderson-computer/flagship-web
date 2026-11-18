#!/bin/bash
set -euo pipefail
major=$1
cd /opt/flagship-web
test "$(stat -c %a /var/lib/flagship-web/admin.password)" = 600
test "$(stat -c %U /var/lib/flagship-web/admin.password)" = root
test "$(stat -c %a /etc/flagship-web/auth.json)" = 640
test "$(stat -c %U /etc/flagship-web/auth.json)" = root
test "$(stat -c %a /var/lib/flagship-web/journals)" = 700
runuser -u flagship-web -- test ! -r /var/lib/flagship-web/admin.password
runuser -u flagship-web -- test ! -w /etc/flagship-web/auth.json
runuser -u flagship-web -- /usr/bin/flagship-web serve &
server=$!
trap 'kill "$server" 2>/dev/null || true; wait "$server" 2>/dev/null || true' EXIT
/opt/flagship-web/venv/bin/python - <<'PY'
import time,urllib.request,urllib.error,json,re,http.cookiejar
base='http://127.0.0.1:8443'
for attempt in range(60):
    try:
        assert json.load(urllib.request.urlopen(base+'/health'))['status']=='ok';break
    except OSError:time.sleep(.25)
else:raise SystemExit('HTTP service did not become healthy')
try:urllib.request.urlopen(base+'/api/state');raise AssertionError('Anonymous state allowed')
except urllib.error.HTTPError as e:assert e.code==401
jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
html=opener.open(base+'/').read().decode()
assert 'Flagship Web' in html and 'CYBER CHIEF TOOLKIT' in html
csrf=re.search(r'name="csrf-token" content="([^"]+)"',html).group(1)
password=open('/var/lib/flagship-web/admin.password').read().strip()
def post(path,body):
    request=urllib.request.Request(base+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-CSRF-Token':csrf})
    return json.load(opener.open(request))
csrf=post('/api/login',dict(username='admin',password=password))['csrf']
key=post('/api/pools',dict(demo=True))['id']
inventory=json.load(opener.open(base+'/api/pools/'+key+'/inventory'))
assert inventory['records']['VM'][0]['power_state']=='Halted'
post('/api/pools/'+key+'/actions',dict(ref='OpaqueRef:demo-vm',action='start',confirm='Training Rocky'))
assert json.load(opener.open(base+'/api/pools/'+key+'/inventory'))['records']['VM'][0]['power_state']=='Running'
assert len(json.load(opener.open(base+'/api/help'))['articles'])>=10
post('/api/logout',{})
print('Installed unprivileged HTTP/auth/demo/help: PASS')
PY
kill "$server"
wait "$server" || true
trap - EXIT
sha256sum /etc/flagship-web/auth.json /etc/flagship-web/session.key /var/lib/flagship-web/admin.password >/tmp/flagship-preserve.sha256
rpm -U --replacepkgs "/src/releases/1.0.0/el$major/rpms/flagship-web-1.0.0-1.el$major.x86_64.rpm"
sha256sum -c /tmp/flagship-preserve.sha256
echo retained >/var/lib/flagship-web/retain-test
rpm -e flagship-web
test -f /var/lib/flagship-web/retain-test
test -f /etc/flagship-web/auth.json
test ! -e /usr/bin/flagship-web
test ! -e /opt/flagship-web/flagship_web/app.py
test ! -e /opt/flagship-web/venv
echo "Rocky $major offline install/reinstall/remove: PASS"
