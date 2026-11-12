"""Tools chỉ đọc dữ liệu status. Live và snapshot có cùng contract."""
import datetime
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
HOSTS = {'github': 'https://www.githubstatus.com', 'cloudflare': 'https://www.cloudflarestatus.com'}


def schema(name, description, properties, required):
    return {'type': 'function', 'function': {'name': name, 'description': description,
        'parameters': {'type': 'object', 'properties': properties, 'required': required, 'additionalProperties': False}}}

SCHEMAS = [
    schema('get_status', 'Check provider status and list recent incident titles and IDs. A historical incident is not necessarily active. Component is an optional search hint.',
           {'provider': {'type': 'string', 'enum': list(HOSTS)}, 'component': {'type': 'string', 'description': 'Optional product or component name'}}, ['provider']),
    schema('get_incident_details', 'Read an incident by ID from a provider. Inspect updates for scope and timestamps; do not infer causation.',
           {'provider': {'type': 'string', 'enum': list(HOSTS)}, 'incident_id': {'type': 'string'}}, ['provider', 'incident_id'])]


class StatusTools:
    def __init__(self, mode='snapshot', fail=False):
        if mode not in ('snapshot', 'live'):
            raise ValueError('mode phải là snapshot hoặc live')
        self.mode, self.fail, self.cache = mode, fail, {}

    def _load(self, provider):
        if provider not in HOSTS:
            raise ValueError('provider phải là github hoặc cloudflare')
        if self.fail:
            raise TimeoutError('Không thể lấy dữ liệu status (timeout giả lập).')
        if provider in self.cache:
            return self.cache[provider]
        if self.mode == 'snapshot':
            data = json.loads((ROOT / 'fixtures' / f'{provider}.json').read_text(encoding='utf-8'))
        else:
            data = {'captured_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source': HOSTS[provider], 'data': {}}
            for endpoint in ('summary', 'incidents'):
                req = urllib.request.Request(f'{HOSTS[provider]}/api/v2/{endpoint}.json', headers={'User-Agent': os.getenv('STATUS_USER_AGENT', 'StatusAgentLab/1.0 (educational classroom)')})
                with urllib.request.urlopen(req, timeout=15) as response:
                    data['data'][endpoint] = json.load(response)
        self.cache[provider] = data
        return data

    def get_status(self, provider, component=''):
        data = self._load(provider)
        summary = data['data']['summary']
        incidents = data['data']['incidents']['incidents']
        query = component.casefold().strip()
        components = [c for c in summary.get('components', []) if query and query in c.get('name', '').casefold()]
        # Match title, component and updates: a number of real incidents have empty components.
        def relevant(i):
            if not query:
                return True
            text = ' '.join([i.get('name', '')] + [c.get('name', '') for c in i.get('components', [])] + [u.get('body', '') for u in i.get('incident_updates', [])])
            return query in text.casefold()
        matches = [i for i in incidents if relevant(i)]
        entries = [{'id': i['id'], 'name': i['name'], 'status': i['status'], 'updated_at': i['updated_at']} for i in matches[:5]]
        return {'provider': provider, 'captured_at': data['captured_at'], 'overall': summary.get('status'),
                'components': [{'name': c['name'], 'status': c['status']} for c in components[:5]],
                'incidents': entries, 'matching_incidents_in_last_50': len(matches),
                'note': 'Chỉ tìm theo chuỗi trong 50 incident gần nhất; không tìm thấy không chứng minh không có sự cố.',
                'source': HOSTS[provider]}

    def get_incident_details(self, provider, incident_id):
        data = self._load(provider)
        incidents = data['data']['incidents']['incidents']
        incident = next((i for i in incidents if i['id'] == incident_id), None)
        if not incident:
            return {'ok': False, 'error': 'INCIDENT_NOT_FOUND', 'message': 'Không tìm thấy ID trong 50 incident gần nhất.'}
        updates = incident.get('incident_updates', [])
        # Most APIs return newest first; explicitly sort instead of relying on order.
        updates = sorted(updates, key=lambda u: u.get('created_at', ''), reverse=True)
        chosen = updates[:2]
        if len(updates) > 2:
            chosen.append(updates[-1])
        return {'ok': True, 'provider': provider, 'captured_at': data['captured_at'], 'id': incident['id'],
                'name': incident['name'], 'status': incident['status'], 'created_at': incident['created_at'],
                'updated_at': incident['updated_at'], 'components': [c['name'] for c in incident.get('components', [])],
                'updates': [{'status': u['status'], 'created_at': u['created_at'], 'body': u.get('body', '')[:900],
                             'truncated': len(u.get('body', '')) > 900} for u in chosen],
                'updates_total': len(updates), 'url': incident.get('shortlink') or f"{HOSTS[provider]}/incidents/{incident['id']}"}

    def execute(self, name, args):
        if name not in ('get_status', 'get_incident_details'):
            return {'ok': False, 'error': 'UNKNOWN_TOOL', 'message': f'Tool không tồn tại: {name}'}
        try:
            if not isinstance(args, dict):
                raise ValueError('Arguments phải là JSON object.')
            return getattr(self, name)(**args)
        except (ValueError, TypeError, TimeoutError, urllib.error.URLError, OSError) as exc:
            return {'ok': False, 'error': type(exc).__name__, 'message': str(exc)[:200]}
