# Specification sheet — Flagship Web 1.0.0

Product: Flagship Web. Toolkit: Cyber Chief. Repository/package/service: flagship-web. Predecessor repository: xcp-center-web. Browser console, not the desktop Flagship application.

Target: Rocky Linux 9 and 10 x86_64; Python 3.9 (EL9) / 3.12 (EL10), systemd. Suggested baseline: 2 CPU cores, 2 GiB RAM, 2 GiB free disk plus journal retention. These are deployment starting points, not benchmarked capacity guarantees. Modern browser with JavaScript and cookies. Internet not required after transferring the offline bundle.

Management: direct HTTPS XAPI XML-RPC; standalone XCP-ng host or pool coordinator. Inventory: pools, hosts, VMs, SRs, networks, tasks. Search: names/UUIDs/folders/tags. Changes: regular VM power, snapshot, clone, rename and folder. Requires exact-name confirmation and refuses templates/control domains. All changes use the connected XAPI account's permissions.

Connection model: one service worker, eight threads, at most 16 browser sessions and four host/pool connections per session. 30-minute idle and eight-hour absolute session lifetime. Credentials and connection definitions are transient. No scale/SLA guarantee is claimed.

Delivery: native EL9/EL10 x86_64 RPM, matching full offline tarball, source tarball, Python dependency source tarball, checksums and release notes. Embedded Help/About, install/operator/admin guides, ICD, this specification, security/build/troubleshooting/validation documentation.

Not included: VNC/browser shell, new VM wizard, automatic provisioning, migrations, VLAN creation, ISO attach, XVA import/export, HA/WLB, persistent host credential vault, SSO/MFA/RBAC, scheduler, automatic master discovery. Hypervisor platform support beyond the documented live test must be qualified locally.
