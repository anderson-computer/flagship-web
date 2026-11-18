# Security model

Use a dedicated, appropriately privileged XAPI account where the server supports one. The local console account can perform all exposed operations on connections opened in its own browser session. There is no multi-user RBAC, MFA or persistent credential vault in 1.0.0.

Local authentication uses a salted Werkzeug password hash. Session cookies are signed, HttpOnly and SameSite Strict. They contain an opaque browser session identifier and CSRF token, never XAPI credentials or handles. HTTPS proxy deployments must enable secure cookies. All modifying routes require JSON, a matching CSRF token and, when present, an Origin matching the request host. Unrecognized Host headers are refused.

XAPI connections require HTTPS with CA/hostname verification or an explicit independently verified SHA-256 pin. Insecure verification bypass is not exposed. Certificate changes are refused before request bytes. Connection credentials are used once for login; XAPI session handles stay in memory and are explicitly logged out when practical. A process crash may leave server-side sessions until server expiry.

Inventory uses a field allowlist instead of exposing full XAPI records. Browser rendering uses textContent and escaped templates. Error responses omit raw RPC fault details and credential-bearing arguments. The health endpoint reports only service status/version and is intentionally unauthenticated. Static files contain no secrets.

The service is unprivileged, loopback-only and systemd-hardened. It can reach administrator-specified HTTPS hosts; network-level egress policy remains the operator's responsibility. Host credentials authorize access to the chosen host. Sessions are limited to 16 browser sessions and four connections per browser. Ten failed logins per source address within 15 minutes block further attempts until that window expires. SSH tunnel users share the loopback source address.

Private fsync'd journals precede real mutations. Unknown network outcomes are not retried. Journals are not an immutable centralized audit system. Do not run concurrent administrators changing the same VM folder. Memory-only state limits credential persistence but does not protect against a compromised server/root account. Report vulnerabilities privately to the repository owner.
