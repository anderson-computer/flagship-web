"""Authenticated, same-origin web console. XAPI sessions stay in server memory."""
import functools
import hmac
import json
import os
import re
import secrets
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit
from flask import Flask, abort, jsonify, render_template, request, session
from werkzeug.security import check_password_hash
from . import __version__
from .backend import DemoConnection, PoolConnection, clean_text


class BrowserSession:
    def __init__(self):
        self.created = self.touched = time.monotonic()
        self.connections = {}
        self.lock = threading.RLock()

    def close(self):
        with self.lock:
            for item in self.connections.values():
                item['client'].close()
            self.connections.clear()


def create_app(config_dir=None, data_dir=None, connection_factory=PoolConnection):
    config = Path(config_dir or os.environ.get('FLAGSHIP_WEB_CONFIG', '/etc/flagship-web'))
    data = Path(data_dir or os.environ.get('FLAGSHIP_WEB_DATA', '/var/lib/flagship-web'))
    app = Flask(__name__)
    app.config.update(SECRET_KEY=(config / 'session.key').read_text().strip(),
                      MAX_CONTENT_LENGTH=16384, SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE='Strict', SESSION_COOKIE_SECURE=os.environ.get('FLAGSHIP_WEB_HTTPS') == '1',
                      TRUSTED_HOSTS=os.environ.get('FLAGSHIP_WEB_HOSTS', 'localhost,127.0.0.1,[::1]').split(','))
    auth = json.loads((config / 'auth.json').read_text())
    sessions, failures = {}, {}
    guard = threading.RLock()
    stop = threading.Event()
    app.extensions['flagship_sessions'] = sessions
    app.extensions['flagship_stop'] = stop

    def reap():
        expired = []
        now = time.monotonic()
        with guard:
            for sid, user in list(sessions.items()):
                if now - user.touched > 1800 or now - user.created > 28800:
                    expired.append(sessions.pop(sid))
            for address, entry in list(failures.items()):
                if now - entry[0] > 900:
                    failures.pop(address)
        for user in expired:
            user.close()

    def sweeper():
        while not stop.wait(60):
            reap()
    threading.Thread(target=sweeper, daemon=True).start()

    def protected(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            reap()
            with guard:
                user = sessions.get(session.get('sid'))
            if user is None:
                abort(401)
            with user.lock:
                with guard:
                    if sessions.get(session.get('sid')) is not user:
                        abort(401)
                user.touched = time.monotonic()
                return fn(user, *args, **kwargs)
        return wrapped

    @app.before_request
    def csrf_guard():
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            origin = request.headers.get('Origin')
            if origin and origin.rstrip('/') != request.host_url.rstrip('/'):
                abort(403)
            expected = session.get('csrf', '')
            actual = request.headers.get('X-CSRF-Token', '')
            if not expected or not hmac.compare_digest(expected, actual):
                abort(403)
            if not request.is_json:
                abort(415)

    @app.after_request
    def headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    @app.errorhandler(Exception)
    def handle_error(exc):
        from werkzeug.exceptions import HTTPException
        from .vendor.flagship.api import APIError
        if isinstance(exc, HTTPException):
            return jsonify(error=exc.name), exc.code
        if isinstance(exc, ValueError):
            # Only locally generated validation text, never raw RPC fault bodies.
            return jsonify(error='Invalid input. Check the names, VM state, confirmation and certificate fingerprint.'), 400
        if isinstance(exc, APIError):
            code = str(exc)
            code = code if re.fullmatch(r'[A-Z][A-Z0-9_]{0,79}', code) else 'API_ERROR'
            return jsonify(error='XAPI rejected the request (' + code + '). Refresh and inspect the task before retrying.'), 502
        return jsonify(error='Connection or operation failed. Verify TLS trust and host availability; inspect server state before retrying a change.'), 502

    @app.get('/')
    def index():
        session.setdefault('csrf', secrets.token_urlsafe(32))
        return render_template('index.html', version=__version__, csrf=session['csrf'])

    @app.get('/health')
    def health():
        return jsonify(status='ok', version=__version__)

    @app.post('/api/login')
    def login():
        reap()
        body = request.get_json()
        address = request.remote_addr or 'unknown'
        with guard:
            first, count = failures.get(address, (time.monotonic(), 0))
            if count >= 10:
                abort(429)
        if not (isinstance(body, dict) and body.get('username') == auth['username'] and
                isinstance(body.get('password'), str) and check_password_hash(auth['password_hash'], body['password'])):
            with guard:
                failures[address] = (first, count + 1)
            abort(401)
        with guard:
            if len(sessions) >= 16:
                abort(503)
            old = sessions.pop(session.get('sid'), None)
            sid = secrets.token_urlsafe(32)
            sessions[sid] = BrowserSession()
            failures.pop(address, None)
        if old:
            old.close()
        session.clear()
        session.update(sid=sid, csrf=secrets.token_urlsafe(32))
        return jsonify(csrf=session['csrf'])

    @app.post('/api/logout')
    @protected
    def logout(user):
        with guard:
            sessions.pop(session.get('sid'), None)
        user.close()
        session.clear()
        return jsonify(ok=True)

    @app.get('/api/state')
    @protected
    def state(user):
        return jsonify(pools=[dict(id=key, name=item['name'], endpoint=item['endpoint'], demo=item['demo']) for key, item in user.connections.items()])

    @app.post('/api/pools')
    @protected
    def connect(user):
        body = request.get_json()
        if not isinstance(body, dict) or len(user.connections) >= 4:
            abort(400)
        demo = body.get('demo') is True
        name = 'Offline demo' if demo else clean_text(body.get('name'))
        if demo:
            client = DemoConnection()
            endpoint = 'offline'
        else:
            endpoint = body.get('endpoint', '')
            if not isinstance(endpoint, str) or len(endpoint) > 512:
                abort(400)
            parts = urlsplit(endpoint)
            if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment or parts.path not in ('', '/'):
                abort(400)
            if not isinstance(body.get('password'), str) or not body['password']:
                abort(400)
            username = clean_text(body.get('username'), 'Username')
            pin = body.get('fingerprint', '')
            if not isinstance(pin, str):
                abort(400)
            client = connection_factory(endpoint, username, body['password'], pin, data / 'journals')
        key = secrets.token_urlsafe(12)
        user.connections[key] = dict(client=client, name=name, endpoint=endpoint, demo=demo)
        return jsonify(id=key)

    def connection(user, key):
        if key not in user.connections:
            abort(404)
        return user.connections[key]['client']

    @app.delete('/api/pools/<key>')
    @protected
    def disconnect(user, key):
        connection(user, key).close()
        del user.connections[key]
        return jsonify(ok=True)

    @app.get('/api/pools/<key>/inventory')
    @protected
    def inventory(user, key):
        records, errors = connection(user, key).inventory()
        return jsonify(records=records, errors=errors)

    @app.post('/api/pools/<key>/actions')
    @protected
    def action(user, key):
        body = request.get_json()
        if not isinstance(body, dict):
            abort(400)
        result = connection(user, key).action(body.get('ref'), body.get('action'), body.get('value', ''), body.get('confirm'))
        return jsonify(result=result, message='Request returned. Refresh Tasks to confirm completion; changes are never retried automatically.')

    @app.get('/api/help')
    @protected
    def help_files(user):
        articles = []
        for path in sorted((Path(__file__).parent.parent / 'docs').glob('*.md')):
            articles.append(dict(title=path.stem.replace('_', ' ').replace('-', ' ').title(), content=path.read_text()))
        return jsonify(articles=articles)

    return app
