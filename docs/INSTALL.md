# Installation — Rocky Linux 9 and 10

Supported target: Rocky Linux 9 or 10, x86_64. Download the matching `flagship-web-1.0.0-el9-x86_64-offline.tar.gz` or `flagship-web-1.0.0-el10-x86_64-offline.tar.gz` from the GitHub 1.0.0 release. Transfer the archive and SHA256SUMS through your approved offline process. Verify the outer archive checksum on the connected staging system and again after transfer.

On Rocky 9:
```
tar -xzf flagship-web-1.0.0-el9-x86_64-offline.tar.gz -C /path/to/empty-directory
cd /path/to/empty-directory
sudo bash install.sh
sudo cat /var/lib/flagship-web/admin.password
sudo systemctl enable --now flagship-web
```
Use the el10 archive on Rocky 10. The installer checks internal checksums, OS and architecture, then uses only the bundled local DNF repository and wheelhouse. It does not contact internet repositories. Rocky RPM dependency signatures are checked with the preinstalled Rocky key; the application RPM is unsigned. The service is not started automatically during installation.

Default console username: `admin`. Read the generated password privately; it is root-only. After recording it in your password manager, remove `/var/lib/flagship-web/admin.password`. The application checks its salted password hash in `/etc/flagship-web/auth.json`.

From Windows PowerShell (replace login and server):
```
ssh -N -o ExitOnForwardFailure=yes -L 18443:127.0.0.1:8443 login@rocky-server
```
Keep the window open, then browse to `http://127.0.0.1:18443`. The SSH tunnel encrypts traffic to the server. Local port 18443 and server loopback port 8443 are different. If 18443 is busy, choose another local port. Hypervisor connections use HTTPS independently of this tunnel.

The service listens on 127.0.0.1 only. Do not open a firewall port for this default deployment. For a managed HTTPS reverse proxy, follow Administration. The app is not a desktop GUI and does not install onto XCP-ng dom0.

The bare RPM requires Python, pip, systemd, util-linux, CA certificates and shadow-utils to be available. Use the full offline bundle for an air-gapped machine with missing dependencies. Ansible is not needed.
