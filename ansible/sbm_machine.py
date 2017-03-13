#!/usr/bin/python
import requests
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from ansible.module_utils.basic import *

API_BASE = '/api/v1/machine/'
MACHINE_KEYS = [
    'hostname',
    'default_boot',
    'alternate_boot',
    'switch_type',
    'time_between'
]


def _get_machines(uri):
    api_url = urljoin(uri, API_BASE)
    return requests.get(api_url).json()


def _get(data):
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['hostname'] + '/')
    return requests.get(api_url).json()


def _remove(data):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['hostname'] + '/')
    resp = requests.delete(api_url).json()
    if 'status' not in resp.keys() or resp['status'] != 'ok':
        retval['failed'] = True
        retval['msg'] = "Failed to remove host"
    else:
        retval['changed'] = True
        retval['msg'] = "Successfully removed host"
    return retval


def _compare(m1, m2):
    for key in MACHINE_KEYS:
        if m1[key] != m2[key]:
            return False
    return True


def _update(data, check):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['hostname'] + '/')
    mach = _get(data)
    new_mach = {}
    for key in MACHINE_KEYS:
        new_mach[key] = data[key]
    retval['msg'] = 'Successfully confirmed host'
    if not _compare(mach, new_mach):
        retval['msg'] = 'Successfully updated Host'
        retval['changed'] = True
        if not check:
            resp = requests.post(api_url, json=new_mach)
            if not _compare(new_mach, resp.json()):
                retval['msg'] = 'Updated data not as expected'
                retval['failed'] = True
    return retval


def _add(data):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    mach = {}
    for key in MACHINE_KEYS:
        mach[key] = data[key]
    resp = requests.put(api_url, json=mach)
    retval['msg'] = "Successfully added host"
    retval['changed'] = True
    if mach['hostname'] in resp.json():
        new_mach = _get(data)
        if not _compare(mach, new_mach):
            retval['failed'] = True
            retval['msg'] = "Adding host failed"
    else:
        retval['failed'] = True
        retval['msg'] = "Adding host failed"
    return retval


def _present(data, check):
    retval = {'failed': False, 'changed': False}
    machines = _get_machines(data['sbm_uri'])
    if data['hostname'] in machines:
        retval.update(_update(data, check))
    else:
        if check:
            retval['changed'] = True
        else:
            retval.update(_add(data))
    return retval


def _absent(data, check):
    retval = {'failed': False, 'changed': False}
    machines = _get_machines(data['sbm_uri'])
    if data['hostname'] in machines:
        if check:
            retval['changed'] = True
        else:
            retval.update(_remove(data))
    return retval


def main():
    fields = {
        'sbm_uri': {'required': True, "type": 'str'},
        'hostname': {'required': True, 'type': 'str'},
        'default_boot': {'type': 'str'},
        'alternate_boot': {'type': 'str'},
        'switch_type': {
            'choices': [
                'switched',
                'alternating',
                'timed'
            ],
            'default': 'switched'
        },
        'time_between': {'type': 'int', 'default': 600},
        'state': {
            'required': True,
            'choices': ['absent', 'present'],
            'default': None
        }
    }

    module = AnsibleModule(argument_spec=fields, supports_check_mode=True)
    if module.params['state'] == 'present':
        response = _present(module.params, module.check_mode)
    else:
        response = _absent(module.params, module.check_mode)
    if response['failed']:
        module.fail_json(**response)
    module.exit_json(**response)


if __name__ == '__main__':
    main()
