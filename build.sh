#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
engine=${CONTAINER_ENGINE:-podman}
versions=("$@")
[[ ${#versions[@]} -gt 0 ]] || versions=(9 10)
mkdir -p releases/1.0.0
for major in "${versions[@]}"; do
  [[ $major == 9 || $major == 10 ]] || exit 2
  "$engine" run --rm --security-opt label=disable -v "$PWD:/src:rw" "docker.io/rockylinux/rockylinux:$major" bash /src/packaging/build-in-container.sh "$major"
done
(cd releases/1.0.0; find . -maxdepth 1 -name '*.tar.gz' -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum el*/rpms/flagship-web-*.rpm) > releases/1.0.0/SHA256SUMS
