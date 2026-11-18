# Third-party notices

Flagship Web contains unchanged transport, TLS, protocol, journal and redaction modules from [mike0615/flagship](https://github.com/mike0615/flagship), fetched November 17, 2026. Copyright 2026 Mike Anderson, BSD-2-Clause. The complete license is included in `flagship_web/vendor/flagship/LICENSE`. The web layer restricts the operations exposed by those modules. Its default connection policy does not expose their insecure TLS option.

Python runtime wheels include Flask (BSD-3-Clause), Werkzeug (BSD-3-Clause), Jinja2 (BSD-3-Clause), MarkupSafe (BSD-3-Clause), ItsDangerous (BSD-3-Clause), Click (BSD-3-Clause), Blinker (MIT), Gunicorn (MIT), Packaging (Apache-2.0 OR BSD-2-Clause), and Python-version-specific dependencies such as importlib-metadata and zipp (Apache-2.0 OR MIT and MIT respectively). Each wheel retains upstream metadata/license files. Exact installed versions appear in the per-OS `requirements.lock`.

Companion Python source archives retain exact upstream source distributions and SHA-256 checksums. Rocky dependency RPMs retain upstream licensing and vendor signatures. The application RPM is unsigned. No proprietary hypervisor binaries are redistributed.
