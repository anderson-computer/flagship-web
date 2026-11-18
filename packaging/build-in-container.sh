#!/bin/bash
set -euo pipefail
major=$1
dnf -y install rpm-build python3 python3-pip dnf-plugins-core createrepo_c tar gzip
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
source="$work/flagship-web-1.0.0"
mkdir -p "$source"
for item in flagship_web docs packaging tests .github .gitignore build.sh install.sh requirements.txt README.md LICENSE RELEASE_NOTES.md THIRD_PARTY_NOTICES.md; do cp -a "/src/$item" "$source/"; done
find "$source" -name __pycache__ -type d -prune -exec rm -rf {} +
python3 -m venv "$work/buildenv"
pip="$work/buildenv/bin/pip"
"$pip" install --upgrade pip wheel setuptools
mkdir "$source/wheels"
"$pip" wheel --wheel-dir "$source/wheels" -r /src/requirements.txt
python3 -m venv "$work/verify"
"$work/verify/bin/pip" install --no-index --find-links="$source/wheels" -r /src/requirements.txt
"$work/verify/bin/pip" check
"$work/verify/bin/pip" freeze > "$source/requirements.lock"
cd "$source"
"$work/verify/bin/python" -m unittest discover -s tests -v
release="/src/releases/1.0.0/el$major"
mkdir -p "$release/rpms/dependencies" "$release/python-sources"
python3 /src/packaging/collect-sources.py "$source/requirements.lock" "$release/python-sources"
top="$work/rpmbuild"
mkdir -p "$top"/{SOURCES,SPECS,BUILD,BUILDROOT,RPMS,SRPMS}
tar -C "$work" -czf "$top/SOURCES/flagship-web-1.0.0.tar.gz" flagship-web-1.0.0
rpmbuild -bb --define "_topdir $top" --define "dist .el$major" "$source/packaging/flagship-web.spec"
cp "$top"/RPMS/x86_64/*.rpm "$release/rpms/"
dnf download -y --resolve --alldeps --destdir "$release/rpms/dependencies" python3 python3-pip systemd util-linux shadow-utils ca-certificates rpm-plugin-syslog
createrepo_c "$release/rpms/dependencies"
cp /src/install.sh /src/docs/INSTALL.md /src/RELEASE_NOTES.md "$source/requirements.lock" "$release/"
cp "$top/SOURCES/flagship-web-1.0.0.tar.gz" "/src/releases/1.0.0/flagship-web-1.0.0-el$major-source.tar.gz"
(cd "$release"; find rpms -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum install.sh INSTALL.md RELEASE_NOTES.md requirements.lock) > "$release/SHA256SUMS"
tar -C "$release" -czf "/src/releases/1.0.0/flagship-web-1.0.0-el$major-python-sources.tar.gz" python-sources
tar -C "$release" --exclude=python-sources -czf "/src/releases/1.0.0/flagship-web-1.0.0-el$major-x86_64-offline.tar.gz" .
