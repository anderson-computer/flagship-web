import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from werkzeug.security import generate_password_hash
from flagship_web.app import create_app
from flagship_web.backend import PoolConnection, public_record
from flagship_web.vendor.flagship.api import Client, Transport, wire_value
from flagship_web.vendor.flagship.tls import TrustPolicy, CertificateChanged
from flagship_web.vendor.flagship.journal import OperationJournal, JournalError


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'session.key').write_text('x'*64)
        (self.root/'auth.json').write_text(json.dumps(dict(username='admin', password_hash=generate_password_hash('test-only'))))
        self.factory = Mock()
        self.app = create_app(self.root, self.root, self.factory)
        self.client = self.app.test_client()
        self.client.get('/')
        with self.client.session_transaction() as s:
            self.csrf = s['csrf']

    def tearDown(self):
        self.app.extensions['flagship_stop'].set()
        for user in self.app.extensions['flagship_sessions'].values():
            user.close()
        self.temp.cleanup()

    def post(self, path, data, client=None, token=None):
        return (client or self.client).post('/api'+path, json=data, headers={'X-CSRF-Token':token or self.csrf})

    def login(self):
        r=self.post('/login',dict(username='admin',password='test-only'))
        self.assertEqual(r.status_code,200)
        self.csrf=r.json['csrf']

    def demo(self):
        self.login()
        return self.post('/pools',{'demo':True}).json['id']

    def test_auth_csrf_origin_and_security_headers(self):
        self.assertEqual(self.client.get('/api/state').status_code,401)
        self.assertEqual(self.client.post('/api/login',json={}).status_code,403)
        self.assertEqual(self.client.post('/api/login',json={},headers={'X-CSRF-Token':self.csrf,'Origin':'https://evil.example'}).status_code,403)
        self.assertEqual(self.client.get('/health',headers={'Host':'evil.example'}).status_code,400)
        self.assertIn("frame-ancestors 'none'",self.client.get('/').headers['Content-Security-Policy'])
        self.assertEqual(self.client.get('/').headers['Cache-Control'],'no-store')

    def test_login_limit_and_rotation(self):
        for _ in range(10):
            self.assertEqual(self.post('/login',dict(username='admin',password='wrong')).status_code,401)
        self.assertEqual(self.post('/login',dict(username='admin',password='test-only')).status_code,429)

    def test_demo_power_isolated_confirmation_and_states(self):
        key=self.demo()
        body=dict(ref='OpaqueRef:demo-vm',action='start',confirm='wrong')
        self.assertEqual(self.post('/pools/'+key+'/actions',body).status_code,400)
        body['confirm']='Training Rocky'
        self.assertEqual(self.post('/pools/'+key+'/actions',body).status_code,200)
        self.assertEqual(self.client.get('/api/pools/'+key+'/inventory').json['records']['VM'][0]['power_state'],'Running')
        self.assertEqual(self.post('/pools/'+key+'/actions',body).status_code,400)
        body['action']='destroy'
        self.assertEqual(self.post('/pools/'+key+'/actions',body).status_code,400)
        self.factory.assert_not_called()

    def test_pool_scope_logout_and_no_plaintext_credentials(self):
        self.login()
        result=self.post('/pools',dict(name='Lab',endpoint='https://192.0.2.1',username='root',password='secret-never-save',fingerprint=''))
        key=result.json['id']
        state=self.client.get('/api/state')
        self.assertNotIn('secret-never-save',state.text)
        other=self.app.test_client()
        self.assertEqual(other.get('/api/pools/'+key+'/inventory').status_code,401)
        self.post('/logout',{})
        self.factory.return_value.close.assert_called_once()
        self.assertEqual(self.client.get('/api/state').status_code,401)
        self.assertNotIn('secret-never-save',''.join(p.read_text() for p in self.root.glob('*') if p.is_file()))

    def test_expiry_closes_remote_session(self):
        self.login()
        self.post('/pools',dict(name='Lab',endpoint='https://192.0.2.1',username='root',password='secret',fingerprint=''))
        for s in self.app.extensions['flagship_sessions'].values():
            s.touched-=1801
        self.assertEqual(self.client.get('/api/state').status_code,401)
        self.factory.return_value.close.assert_called_once()

    def test_reject_unsafe_endpoint_and_session_capacity(self):
        self.login()
        for endpoint in ('http://192.0.2.1','https://root:pw@192.0.2.1','https://192.0.2.1/path'):
            self.assertEqual(self.post('/pools',dict(name='Lab',endpoint=endpoint,password='pw',username='root')).status_code,400)
        self.factory.assert_not_called()
        for _ in range(4):
            self.assertEqual(self.post('/pools',{'demo':True}).status_code,200)
        self.assertEqual(self.post('/pools',{'demo':True}).status_code,400)

    def test_help_embedded_no_external_resources(self):
        self.login()
        articles=self.client.get('/api/help').json['articles']
        self.assertGreaterEqual(len(articles),10)
        html=self.client.get('/').text
        self.assertNotIn('https://cdn',html)


class BackendTests(unittest.TestCase):
    def test_record_allowlist_redacts_secrets(self):
        record=public_record('VM','OpaqueRef:x',dict(name_label='<script>x</script>',password='secret',other_config={'password':'secret','folder':'Lab'},tags=['one']))
        self.assertNotIn('password',json.dumps(record))
        self.assertEqual(record['folder'],'Lab')

    def test_tls_pin_checked_before_request(self):
        pin='ab'*32
        policy=TrustPolicy(pins={'lab:443':pin})
        sock=Mock();sock.getpeercert.return_value=b'wrong'
        with self.assertRaises(CertificateChanged):
            policy.check(sock,'lab',443)
        self.assertEqual(policy.mode('lab',443),'pinned')
        self.assertEqual(TrustPolicy().mode('lab',443),'verified')

    def test_transport_does_not_retry(self):
        t=Transport(None);t.single_request=Mock(side_effect=ConnectionResetError)
        with self.assertRaises(ConnectionResetError):
            t.request('host','/',b'body')
        self.assertEqual(t.single_request.call_count,1)
        self.assertEqual(wire_value(2**40),str(2**40))

    def connection(self):
        p=PoolConnection.__new__(PoolConnection)
        p.client=Mock()
        p.client.call.return_value=dict(name_label='VM',power_state='Halted',other_config={'folder':'Old','keep':'yes'})
        return p

    def test_action_allowlist_and_system_vm_protection(self):
        p=self.connection()
        with self.assertRaises(ValueError):p.action('OpaqueRef:x','destroy','','VM')
        p.client.call.assert_not_called()
        p.client.call.return_value=dict(name_label='VM',is_control_domain=True)
        with self.assertRaises(ValueError):p.action('OpaqueRef:x','start','','VM')
        p.client.vm_action.assert_not_called()

    def test_start_arguments_and_folder_key_only(self):
        p=self.connection()
        p.action('OpaqueRef:x','start','','VM')
        p.client.vm_action.assert_called_once_with('OpaqueRef:x','start',False,False)
        p.action('OpaqueRef:x','folder','New','VM')
        self.assertEqual(p.client.call.call_args_list[-2].args,('VM.remove_from_other_config','OpaqueRef:x','folder'))
        self.assertEqual(p.client.call.call_args_list[-1].args,('VM.add_to_other_config','OpaqueRef:x','folder','New'))

    def test_clone_snapshot_rename_resume_argument_mapping(self):
        for action, api_action in [('clone','clone'),('snapshot','snapshot'),('rename','set_name_label')]:
            p=self.connection()
            p.action('OpaqueRef:x',action,'New VM','VM')
            p.client.vm_action.assert_called_once_with('OpaqueRef:x',api_action,'New VM')
        p=self.connection()
        p.client.call.return_value=dict(name_label='VM',power_state='Suspended')
        p.action('OpaqueRef:x','resume','','VM')
        p.client.vm_action.assert_called_once_with('OpaqueRef:x','resume',False,True)

    def test_journal_failure_blocks_rpc_and_records_unknown_without_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            blocker=root/'not-a-directory';blocker.write_text('blocked')
            client=Client('https://localhost',journal=OperationJournal(blocker/'journal'))
            client.session='secret-session'
            client._rpc=Mock()
            with self.assertRaises(JournalError):
                client.call('VM.set_name_label','OpaqueRef:x','private-name')
            client._rpc.assert_not_called()
            client.journal.close()
            journal=OperationJournal(root/'valid')
            client.journal=journal
            client._rpc=Mock(side_effect=ConnectionResetError('secret-session private-name'))
            with self.assertRaises(ConnectionResetError):
                client.call('VM.set_name_label','OpaqueRef:x','private-name')
            journal.close()
            text=''.join(p.read_text() for p in (root/'valid').glob('*.jsonl'))
            self.assertIn('unknown',text)
            self.assertNotIn('private-name',text)
            self.assertNotIn('secret-session',text)

if __name__=='__main__':unittest.main()
