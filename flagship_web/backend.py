"""Allowlisted XAPI operations and a completely isolated offline demonstration."""
import copy
import re
import uuid
from urllib.parse import urlsplit
from .vendor.flagship.api import Client, APIError
from .vendor.flagship.journal import OperationJournal
from .vendor.flagship.tls import host_key, normalize_fingerprint

KINDS = ('pool', 'host', 'VM', 'SR', 'network', 'task')
POWER = {'start': ('Halted',), 'clean_shutdown': ('Running',),
         'clean_reboot': ('Running',), 'hard_shutdown': ('Running', 'Paused', 'Suspended'),
         'hard_reboot': ('Running',), 'suspend': ('Running',), 'resume': ('Suspended',)}
ACTIONS = set(POWER) | {'snapshot', 'clone', 'rename', 'folder'}


def clean_text(value, field='Name'):
    if not isinstance(value, str) or not value.strip() or len(value) > 128 or any(ord(c) < 32 for c in value):
        raise ValueError(field + ' must contain 1–128 printable characters')
    return value.strip()


def public_record(kind, ref, record):
    # Never send arbitrary XAPI records (they may contain credentials) to a browser.
    fields = {'pool': ('name_label', 'uuid', 'master'),
              'host': ('name_label', 'uuid', 'address', 'enabled'),
              'VM': ('name_label', 'uuid', 'power_state', 'is_a_template', 'is_control_domain', 'resident_on'),
              'SR': ('name_label', 'uuid', 'type', 'physical_size', 'physical_utilisation'),
              'network': ('name_label', 'uuid', 'bridge'),
              'task': ('name_label', 'uuid', 'status', 'progress')}[kind]
    item = {key: record.get(key, '') for key in fields}
    item.update(ref=ref, kind=kind)
    if kind == 'VM':
        item['folder'] = str(record.get('other_config', {}).get('folder', ''))
        item['tags'] = list(record.get('tags', []))
    return item


class PoolConnection:
    def __init__(self, endpoint, username, password, pin, journal_dir):
        parsed = urlsplit(endpoint)
        pins = {host_key(parsed.hostname, parsed.port or 443): normalize_fingerprint(pin)} if pin else None
        self.journal = OperationJournal(journal_dir)
        self.client = Client(endpoint, journal=self.journal, pins=pins)
        try:
            self.client.login(username, password)
        except Exception:
            self.close()
            raise

    def close(self):
        try:
            self.client.logout()
        except Exception:
            pass
        self.journal.close()

    def inventory(self):
        records, errors = {}, {}
        for kind in KINDS:
            try:
                records[kind] = [public_record(kind, ref, rec) for ref, rec in self.client.call(kind + '.get_all_records').items()]
            except APIError as exc:
                if str(exc) == 'SESSION_INVALID':
                    raise
                records[kind] = []
                errors[kind] = str(exc)
        return records, errors

    def action(self, ref, action, value, confirm):
        if action not in ACTIONS or not isinstance(ref, str) or not re.fullmatch(r'OpaqueRef:[A-Za-z0-9-]{1,128}', ref):
            raise ValueError('Unsupported action or VM reference')
        vm = self.client.call('VM.get_record', ref)
        if vm.get('is_a_template') or vm.get('is_control_domain'):
            raise ValueError('Operations on templates and control domains are disabled')
        if confirm != vm.get('name_label'):
            raise ValueError('Type the current VM name to confirm this change')
        if action in POWER:
            if vm.get('power_state') not in POWER[action]:
                raise ValueError('The VM power state changed. Refresh before trying again.')
            args = [False, False] if action == 'start' else [False, True] if action == 'resume' else []
            return self.client.vm_action(ref, action, *args)
        if action in ('clone', 'snapshot'):
            return self.client.vm_action(ref, action, clean_text(value))
        if action == 'rename':
            return self.client.vm_action(ref, 'set_name_label', clean_text(value))
        folder = clean_text(value, 'Folder') if value else ''
        # Update the one key; never overwrite unrelated other_config entries.
        old = vm.get('other_config', {})
        if 'folder' in old:
            self.client.call('VM.remove_from_other_config', ref, 'folder')
        if folder:
            self.client.call('VM.add_to_other_config', ref, 'folder', folder)
        return None


DEMO = {
    'pool': [{'ref': 'OpaqueRef:demo-pool', 'kind': 'pool', 'name_label': 'Offline Training Pool', 'uuid': 'demo-pool', 'master': 'OpaqueRef:demo-host'}],
    'host': [{'ref': 'OpaqueRef:demo-host', 'kind': 'host', 'name_label': 'training-host', 'uuid': 'demo-host', 'address': '192.0.2.10', 'enabled': True}],
    'VM': [{'ref': 'OpaqueRef:demo-vm', 'kind': 'VM', 'name_label': 'Training Rocky', 'uuid': 'demo-vm', 'power_state': 'Halted', 'is_a_template': False, 'is_control_domain': False, 'folder': 'Training', 'tags': ['demo'], 'resident_on': 'OpaqueRef:demo-host'}],
    'SR': [{'ref': 'OpaqueRef:demo-sr', 'kind': 'SR', 'name_label': 'Training Storage', 'uuid': 'demo-sr', 'type': 'ext', 'physical_size': '107374182400', 'physical_utilisation': '21474836480'}],
    'network': [{'ref': 'OpaqueRef:demo-net', 'kind': 'network', 'name_label': 'Training LAN', 'uuid': 'demo-net', 'bridge': 'xenbr0'}], 'task': []}


class DemoConnection:
    def __init__(self):
        self.records = copy.deepcopy(DEMO)

    def close(self):
        pass

    def inventory(self):
        return copy.deepcopy(self.records), {}

    def action(self, ref, action, value, confirm):
        if action not in ACTIONS:
            raise ValueError('Unsupported action')
        vm = next((v for v in self.records['VM'] if v['ref'] == ref), None)
        if not vm or confirm != vm['name_label']:
            raise ValueError('Type the current VM name to confirm this change')
        if action in POWER:
            if vm['power_state'] not in POWER[action]:
                raise ValueError('Refresh the VM power state')
            vm['power_state'] = {'start': 'Running', 'clean_shutdown': 'Halted', 'hard_shutdown': 'Halted', 'suspend': 'Suspended', 'resume': 'Running'}.get(action, 'Running')
        elif action == 'folder':
            vm['folder'] = clean_text(value, 'Folder') if value else ''
        elif action == 'rename':
            vm['name_label'] = clean_text(value)
        elif action in ('clone', 'snapshot'):
            new = copy.deepcopy(vm)
            new.update(name_label=clean_text(value), uuid=str(uuid.uuid4()), power_state='Halted')
            new['ref'] = 'OpaqueRef:' + new['uuid']
            if action == 'snapshot':
                new['is_a_template'] = True
                new['tags'] = ['demo', 'snapshot']
            self.records['VM'].append(new)
        return 'demo-completed'
