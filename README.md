# XCP Center Web

A browser-based management console for XCP-ng / XenServer pools. Talks directly to XAPI on the pool master (JSON-RPC, XML-RPC fallback). No Xen Orchestra dependency.

## Features (1.0)

- Connect one or more pools (master IP, credentials)
- Left tree with four views: Infrastructure, Folders, Objects, Tags
- Folders stored as `other_config.folder` (same metadata Windows XCP-ng Center uses)
- Power actions: start, shutdown, reboot, suspend, resume, force
- Snapshot, clone, rename, new VLAN network
- Storage and host overview
- Searchable offline help (14 articles, files on disk)
- Built-in offline demo pool for training with no hypervisor
- Configurable via `config.yaml` (name, org, port, TLS, demo, simple mode, feature flags, pre-seeded pools)

## Not in 1.0

Full New VM wizard, in-page VNC console, live migrate UI, ISO attach, XVA import/export, HA/WLB. Feature flags exist to hide these until implemented.

## Run on Rocky 9

```bash
sudo dnf install -y python3 python3-pip
cd /opt
sudo unzip xcp-center-web.zip   # or clone this repo
cd /opt/xcp-center-web
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt
sudo mkdir -p /etc/xcp-center
sudo cp config.example.yaml /etc/xcp-center/config.yaml
sudo cp systemd/xcp-center.service /etc/systemd/system/
sudo useradd -r -s /sbin/nologin xcpcenter || true
sudo chown -R xcpcenter:xcpcenter /opt/xcp-center-web
sudo systemctl enable --now xcp-center
```

Browse to `http://SERVER:8443`.

## Folder convention

- `VM.other_config["folder"]` = `/Prod/Web`
- `network.other_config["folder"]` = `/Prod/DMZ`
- Nested folders use path prefixes; search "contained in /Prod" = `folder.startswith("/Prod")`

## Config

See `config.example.yaml`. Pool passwords via `XCP_CENTER_POOL_<ID>_PASSWORD`.

## License

TBD
