%global debug_package %{nil}
%global __os_install_post %{nil}
Name: flagship-web
Version: 1.0.0
Release: 1%{?dist}
Summary: Flagship Web XCP-ng and XenServer management console
License: LicenseRef-Proprietary AND BSD-2-Clause AND BSD-3-Clause AND MIT
URL: https://github.com/mike0615/flagship-web
Source0: flagship-web-1.0.0.tar.gz
BuildArch: x86_64
Requires: python3
Requires: python3-pip
Requires: systemd
Requires: util-linux
Requires: ca-certificates
Requires(pre): shadow-utils

%description
Authenticated local web console using Flagship's TLS-verified XAPI transport.
Includes inventory, confirmed VM operations, offline demo, Help/About and an
offline Python runtime wheelhouse. Connect through an SSH tunnel by default.

%prep
%setup -q

%build
test -s requirements.lock

%install
install -d %{buildroot}/opt/flagship-web
cp -a flagship_web docs wheels requirements.lock README.md RELEASE_NOTES.md THIRD_PARTY_NOTICES.md LICENSE %{buildroot}/opt/flagship-web/
install -m 0755 packaging/setup-runtime.sh %{buildroot}/opt/flagship-web/setup-runtime.sh
install -D -m 0755 packaging/flagship-web %{buildroot}/usr/bin/flagship-web
install -D -m 0644 packaging/flagship-web.service %{buildroot}/usr/lib/systemd/system/flagship-web.service
find %{buildroot}/opt/flagship-web -type f -exec chmod 0644 {} +
chmod 0755 %{buildroot}/opt/flagship-web/setup-runtime.sh

%pre
getent group flagship-web >/dev/null || groupadd -r flagship-web
getent passwd flagship-web >/dev/null || useradd -r -g flagship-web -d /var/lib/flagship-web -s /sbin/nologin flagship-web

%post
/opt/flagship-web/setup-runtime.sh || exit 1
systemctl daemon-reload >/dev/null 2>&1 || :

%preun
if [ "$1" -eq 0 ]; then systemctl disable --now flagship-web >/dev/null 2>&1 || :; fi

%postun
if [ "$1" -eq 0 ]; then rm -rf -- /opt/flagship-web/venv; rmdir /opt/flagship-web >/dev/null 2>&1 || :; fi
systemctl daemon-reload >/dev/null 2>&1 || :
if [ "$1" -ge 1 ]; then systemctl try-restart flagship-web >/dev/null 2>&1 || :; fi

%files
/opt/flagship-web/
/usr/bin/flagship-web
/usr/lib/systemd/system/flagship-web.service

%changelog
* Wed Nov 18 2026 Mike Anderson - 1.0.0-1
- Implement Flagship Web from the XCP Center Web scaffold using Flagship XAPI
- Add local authentication, confirmed operations, Help/About and offline packages
