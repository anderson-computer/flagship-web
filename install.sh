#!/bin/bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run sudo bash install.sh' >&2; exit 1; }
cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")"
# shellcheck disable=SC1091
source /etc/os-release
major=${VERSION_ID%%.*}
[[ ${ID:-} == rocky && ( $major == 9 || $major == 10 ) && $(uname -m) == x86_64 ]] || { echo 'Use the matching Rocky Linux 9/10 x86_64 bundle.' >&2; exit 1; }
sha256sum --check --strict SHA256SUMS
shopt -s nullglob
app=(rpms/flagship-web-*.el"$major".x86_64.rpm)
[[ ${#app[@]} == 1 && -f rpms/dependencies/repodata/repomd.xml ]] || { echo 'Wrong OS or incomplete bundle.' >&2; exit 1; }
dnf -y --disablerepo='*' --repofrompath="flagship-web-offline,file://$PWD/rpms/dependencies" --enablerepo=flagship-web-offline --setopt=flagship-web-offline.gpgcheck=1 --setopt="flagship-web-offline.gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-$major" --setopt=install_weak_deps=False install "${app[@]}"
/opt/flagship-web/venv/bin/pip check
flagship-web version
echo 'Installed. Service is inactive until enabled. Read INSTALL.md for sign-in and the SSH tunnel.'
