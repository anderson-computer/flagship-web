# Flagship Web

**Flagship Web 1.0.0** is the browser companion to Flagship, part of the **Cyber Chief toolkit**. It manages XCP-ng and XenServer through direct TLS-verified XAPI connections. Standalone hosts and pools are supported; Xen Orchestra and internet access are not required.

Previously named XCP Center Web. The previous repository was a scaffold; this release implements the application using Flagship's BSD-licensed XAPI transport.

## Install

Download the matching **Rocky Linux 9 or 10 x86_64 offline bundle** from [Releases](https://github.com/mike0615/flagship-web/releases/tag/v1.0.0). Extract it, review its checksums and run `sudo bash install.sh`. Full Python wheels and Rocky RPM dependencies are included. A standalone application RPM is also available for systems with dependencies already staged.

Read [installation and first sign-in](docs/INSTALL.md), [operator guide](docs/USER_GUIDE.md), [administration](docs/ADMINISTRATION.md), [security](docs/SECURITY.md), [ICD](docs/ICD.md), [specification](docs/SPECIFICATION.md), [validation](docs/VALIDATION.md), [release notes](RELEASE_NOTES.md) and [build guide](docs/BUILD.md).

## Included

- Local console authentication and per-browser, memory-only XAPI connections.
- Multiple connections, pool/host/VM/storage/network/task inventory.
- Confirmed start, shutdown, reboot, force shutdown/reboot, suspend/resume, snapshot, clone, rename and folder assignment for regular VMs.
- Offline demo, searchable embedded documentation and About page.
- Private operation journals; mutations are never retried automatically.
- Loopback-only service and native EL9/EL10 packages with network-disabled installation tests.

No new-VM wizard, VNC console, live migration, VLAN creation, XVA import/export, ISO attachment, HA/WLB, scheduled jobs or persistent pool credential vault is included. All browser scripts, styles, icons and Help content are local.

## Repository layout

`flagship_web/` runtime, templates and static assets; `docs/` embedded and standalone documentation; `tests/` security, transport, workflow and package lifecycle checks; `packaging/` RPM spec, service and build/test scripts; `.github/workflows/` CI/release automation; `releases/1.0.0/` locally generated artifacts (published as GitHub release assets, not committed).

Copyright © 2026 Mike Anderson. See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md). Public source availability does not grant an additional license to owner-controlled application code.
