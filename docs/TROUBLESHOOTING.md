# Troubleshooting

Connection refused in browser: check the SSH window remains open, the local tunnel port matches the browser URL, and systemctl reports flagship-web active. Local port already in use: choose another local SSH forwarding port; keep the remote port 8443. The backend intentionally is not reachable directly from another machine.

Console login failure: use the local Flagship Web admin account, not the hypervisor root account. Read the initial root-only password or reset it. Ten failed attempts block the loopback source for 15 minutes. Browser session expired: sign in again and reconnect to hosts.

Self-signed certificate: inspect `openssl x509 -in /etc/xensource/xapi-ssl.pem -noout -fingerprint -sha256` on the XCP-ng host console. Enter the independently verified SHA-256 value. Do not bypass verification. After a certificate renewal, verify the new fingerprint before reconnecting.

HOST_IS_SLAVE or pool coordinator error: enter the coordinator's HTTPS address directly. Permission/session errors: inspect account rights and reconnect; the app does not replay operations. Missing class inventory: inspect the class-level error and hypervisor version. A failed task is visible in Tasks; raw error_info is intentionally not exposed as it may contain sensitive arguments.

Timeout after a VM change: its outcome may be unknown. Inspect Tasks and actual VM state before retrying. Folder changes use two key-level calls and can partially complete. Journal write failure: correct ownership/disk space; reconnect only after reviewing pool state. Do not delete evidence merely to make a retry work.

Offline dependency failure: use the exact matching OS/architecture bundle, verify checksums and confirm the Rocky vendor key is installed. Do not mix EL9 and EL10 wheels or dependency repositories. Native systemd/SELinux policy varies by site and should be qualified on the destination machine.
