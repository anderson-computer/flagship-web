# Administration

Service: `flagship-web.service`; runtime: `/opt/flagship-web`; configuration: `/etc/flagship-web`; data and journals: `/var/lib/flagship-web`. The unprivileged `flagship-web` system account owns data. Runtime/configuration are root-controlled. The loopback listener is port 8443, using HTTP inside the SSH tunnel.

Status and logs:
```
sudo systemctl status flagship-web
sudo journalctl -u flagship-web
```
Do not enable request-body or proxy debug logging: connection requests contain passwords. Operation journals store method/target identity/outcome, never RPC argument bodies. Protect and rotate journals as infrastructure metadata. Application journaling is fail-closed: a storage failure blocks subsequent mutations in the affected connection. Inspect pool state before reconnecting and retrying.

Reset the local password by stopping the service, running `/opt/flagship-web/venv/bin/python -m flagship_web.reset_admin` as root from `/opt/flagship-web`, then restarting. The password is entered interactively and stored only as a salted hash. Old browser sessions disappear after restart. Remove the initial bootstrap password file after recording the password privately.

For an HTTPS reverse proxy, keep the backend on loopback, terminate trusted TLS at the proxy, restrict proxy access and pass the original Host and Origin. Set `/etc/flagship-web/environment` (root-owned 0640) with `FLAGSHIP_WEB_HOSTS=your-hostname` and `FLAGSHIP_WEB_HTTPS=1`, then restart. Add `localhost,127.0.0.1` if you also need local access. The app does not trust forwarded headers or automatically configure TLS/proxy/firewall. Never expose the plain HTTP backend on the LAN.

Keep Gunicorn at exactly one worker with threads: sessions and pool handles are in process memory. Increasing worker count breaks session consistency. Default is eight threads and a 120-second worker timeout; XAPI transport timeout is 30 seconds per request. Six inventory classes are fetched serially; slow hosts may take longer. No automatic task retry is performed.

Upgrades preserve `/etc/flagship-web` and `/var/lib/flagship-web`. Existing connections are lost on restart. Uninstall with `sudo dnf remove flagship-web`; configuration/data and the system account remain for deliberate recovery/removal. Back up configuration and journals privately; there is no stored host credential vault to restore. Restoring the hash/key also restores access and must be treated as secret material.
