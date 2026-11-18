# Interface Control Document — Flagship Web 1.0.0

## External interfaces

Browser → service: HTTP on 127.0.0.1:8443 through SSH, or managed HTTPS proxy. JSON UTF-8 API, signed HttpOnly/SameSite cookie, X-CSRF-Token on writes. No CORS allowance. GET / returns the local UI and CSRF bootstrap. GET /health returns status/version without login.

POST /api/login: username/password → renewed csrf token. POST /api/logout: empty object → ok. GET /api/state: connection ids, labels, endpoint and demo flag. POST /api/pools: name, endpoint, username, password, optional fingerprint; alternatively demo=true → opaque connection id. DELETE /api/pools/{id}: close session. GET /api/pools/{id}/inventory: records by class and class-level error codes. POST /api/pools/{id}/actions: ref, action, value, confirm → returned task/reference and completion warning. GET /api/help: local article title/content array. All /api routes except login require a valid live browser session.

HTTP outcomes: 200 success, 400 invalid input/Host, 401 unauthenticated, 403 Origin/CSRF, 404 unknown connection, 413 oversized request, 415 wrong media type, 429 login rate limit, 502 XAPI/transport/journal failure, 503 session capacity. Bodies never include raw password/session values.

Service → hypervisor: HTTPS TCP 443 by default, optional explicit endpoint port, XenAPI XML-RPC `/`. session.login_with_password(username,password,'1.0','flagship'); subsequent calls prepend the XAPI session. session.logout closes the session. CA/name validation or explicit host:port SHA-256 pin occurs before HTTP bytes. There is no JSON-RPC negotiation or automatic pool-master redirection.

Read classes: pool, host, VM, SR, network, task get_all_records; VM.get_record before mutation. Exposed writes: Async.VM.start(ref,false,false), clean_shutdown, clean_reboot, hard_shutdown, hard_reboot, suspend, resume(ref,false,true), snapshot(ref,name), clone(ref,name); VM.set_name_label; VM.remove_from_other_config/add_to_other_config for folder. No generic arbitrary-RPC endpoint exists.

## Files/process boundaries

/etc/flagship-web/auth.json: username and salted password_hash, 0640 root:flagship-web. session.key: 0640 root:flagship-web, random cookie signing key. /var/lib/flagship-web/admin.password: initial password, 0600 root. Journals: 0700 directory / 0600 JSONL files owned by service. Exact runtime dependencies: requirements.lock and wheels under /opt/flagship-web. No saved pool configurations/passwords.

systemd controls startup/shutdown and the unprivileged account. The installer calls DNF with only its local dependency repository enabled, then installs Python wheels with --no-index. Artifact manifests are SHA256SUMS; no installer network interface is required.
