# Build and release

From Linux/WSL with Podman (or CONTAINER_ENGINE=docker), run `bash build.sh 9 10`, then `bash packaging/test-offline.sh 9` and `bash packaging/test-offline.sh 10`. Building downloads Rocky packages and Python wheels/sources; target installation uses no network.

Each native Rocky build resolves dependencies, installs a clean verification venv, runs unit/integration tests, retains requirements.lock and original Python sources, builds the RPM and assembles a local DNF repository. Each offline test starts a fresh container with networking disabled and verifies install, dependency consistency, unprivileged HTTP startup, authentication, reinstall preservation and removal retention.

GitHub checks repeat both OS builds and offline checks. The release workflow builds both targets and publishes only after successful checks. The publish job uses the workflow's scoped GitHub token; no deployment keys are committed. Local release files are excluded from source control and appear under releases/1.0.0 only after building.

Development: create a venv, `pip install -r requirements.txt`, `python -m unittest discover -s tests -v`. For live read-only qualification run `python -m tests.live_readonly` from the source root; enter the endpoint, independently verified fingerprint, username and password interactively. Never embed real credentials in fixtures or workflows. See Validation for the actual executed scope.
