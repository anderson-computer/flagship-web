# Flagship Web 1.0.0

First implemented release of the former XCP Center Web scaffold, aligned with the Cyber Chief toolkit.

## Features

- Direct verified-HTTPS XAPI using Flagship's XML-RPC transport, including explicit SHA-256 pins for independently verified self-signed certificates.
- Local admin sign-in, same-origin/CSRF protection, session isolation, expiry and memory-only hypervisor credentials/session handles.
- Standalone host and pool connections, inventory, safe field allowlists, confirmed regular-VM operations and private operation journals.
- Dark toolkit interface, embedded searchable Help, About and offline demo.
- Rocky 9/10 x86_64 RPMs, full offline installers, Python source archives and checksums.

## Qualification and limits

See `docs/VALIDATION.md` for executed checks and live-host evidence. Real-host VM mutations are deliberately excluded from the qualification run. Physical systemd/SELinux deployment, pool-master failover and production scale remain site qualification items. Use a lab VM to qualify mutations before production use.

Application RPMs are unsigned. Verify release SHA-256 checksums through a trusted transfer path; this does not replace a package signature. No Ansible dependency is required for this XAPI application.

Credentials are not persisted in a local vault. Reconnect after sign-out, session expiry or service restart. New VM wizard, VNC, VLAN management, migration, ISO attach, XVA transfer and HA/WLB are outside 1.0.0. Pool coordinator addresses must be entered directly; automatic coordinator redirection is not implemented. Tasks refresh manually.
