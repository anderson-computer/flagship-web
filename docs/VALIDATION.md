# Validation record — 1.0.0

Qualification date: November 18, 2026. Version 1.0.0, package build 1.

Application checks: 14 passing tests covering authentication/CSRF/Origin/Host boundaries, session isolation/expiry/connection cleanup, login rate limits, TLS pin enforcement, no transport retry, action allowlist and control-domain protection, power argument mapping/state checks, exact-name confirmation, key-only folder changes, clone/snapshot/rename/resume argument mapping, allowlisted inventory, embedded help and a failing journal that blocks RPC. Unknown operation outcomes are recorded without RPC secrets/arguments.

Native target checks: Rocky 9 (Python 3.9) and Rocky 10 (Python 3.12). Full dependency resolution and application tests run inside each native build. Fresh containers with networking disabled run the full offline installer, dependency checks and the test suite against installed application code. Lifecycle checks start the installed Gunicorn server as the service account, verify health/anonymous denial/login/demo start/help/logout, verify private configuration modes, reinstall without changing auth/key/bootstrap password, and uninstall while retaining configuration/data. The generated venv is removed. Service unit startup on a booted OS remains a separate site check.

Live standalone XCP-ng: operator-authorized read-only test against a user-confirmed SHA-256 certificate pin. Successfully logged in, read all six inventory classes and logged out: 1 singleton pool, 1 host, 63 VM records (including templates/control domain), 6 SRs, 9 networks, 0 tasks. No VM mutations were performed. Credentials were entered interactively and are absent from source, fixtures and release assets. Private IP/account details are not included in this public record.

Browser: successful console sign-in, offline demo power confirmation and Running state, live standalone host connection and host inventory, disconnect, searchable embedded Help, About and responsive toolkit layout. A live host's VM count is filtered to regular VMs on the overview; raw inventory record counts include templates/control domain. The browser test closed its real XAPI connection afterward.

The Rocky 10 offline run initially found an RPM rich-dependency gap (rpm-plugin-syslog); the local dependency collection now includes it and the rerun passed. Shell scripts pass ShellCheck. Release CI repeats both native builds and offline checks before publication; its run is available from the repository Actions tab.

Limitations to retain after these checks: no real VM power/storage mutations are authorized for qualification; no pool failover, production-scale, physical server systemd/SELinux or every-XenServer-version qualification is claimed. Container lifecycle tests exercise package behavior and an unprivileged server process, not a booted physical OS.
