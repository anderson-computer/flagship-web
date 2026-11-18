# Operator guide

Sign in with the local Flagship Web account, then choose Connect host or pool. Enter a label, `https://host-or-coordinator`, XAPI username and password. A standalone XCP-ng host has a singleton pool and works the same way. Enter the pool coordinator directly for a multi-host pool.

The system CA store verifies TLS by default. For a self-signed certificate, independently inspect its SHA-256 fingerprint on the host console and paste it into the connection dialog. A different certificate fails before credentials are transmitted. Never copy an unverified fingerprint from an error message merely to dismiss an error.

Infrastructure summarizes the selected connection. Virtual machines, Hosts, Storage, Networks and Tasks show allowlisted records; search filters names, UUIDs, folders and tags. Use Refresh after a change. Control domains and templates cannot be mutated through this UI.

Choose a VM operation, enter the requested new name/folder if applicable, then type the current VM name exactly. Force actions can lose data. Start/resume and shutdown/reboot are checked against current server state. Snapshot and clone request a name and return an asynchronous task; inspect Tasks for completion. A returned task reference is not proof of success. Clone does not provision or start the clone automatically.

Folders use `VM.other_config.folder` and update that one key. Existing unrelated metadata is preserved. The remove/add sequence is not atomic; if interrupted, refresh and inspect the actual folder. Clearing the value removes the folder key.

The offline demo uses simulated objects only, never opens a network connection, and has its own in-memory state. Demo power controls, rename, folder, clone and snapshot can be explored without affecting hosts.

Disconnect closes that XAPI session. Sign-out closes all sessions for that browser. Idle sessions expire after 30 minutes and all sessions after eight hours; the sweeper checks once a minute. Restarting the service drops all connections. No host passwords or XAPI session handles are saved in the browser or on disk.
