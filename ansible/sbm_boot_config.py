#!/usr/bin/python
import requests
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from ansible.module_utils.basic import *

API_BASE = '/api/v1/boot_config/'
BOOT_CONFIG_KEYS = [
    'title',
    'config'
]


def _get_boot_configs(uri):
    api_url = urljoin(uri, API_BASE)
    return requests.get(api_url).json()


def _get(data):
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['title'] + '/')
    return requests.get(api_url).json()


def _remove(data):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['title'] + '/')
    resp = requests.delete(api_url).json()
    if 'status' not in resp.keys() or resp['status'] != 'ok':
        retval['failed'] = True
        retval['msg'] = "Failed to remove boot_config"
    else:
        retval['changed'] = True
        retval['msg'] = "Successfully removed boot_config"
    return retval


def _compare(v1, v2):
    for key in BOOT_CONFIG_KEYS:
        if v1[key] != v2[key]:
            return False
    return True


def _update(data, check):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['title'] + '/')
    bc = _get(data)
    new_bc = {}
    for key in BOOT_CONFIG_KEYS:
        new_bc[key] = data[key]
    retval['msg'] = 'Successfully confirmed boot_config'
    if not _compare(bc, new_bc):
        retval['msg'] = 'Successfully updated boot_config'
        retval['changed'] = True
        if not check:
            resp = requests.post(api_url, json=new_bc)
            if not _compare(new_bc, resp.json()):
                retval['msg'] = 'Updated boot_config not as expected'
                retval['failed'] = True
    return retval


def _add(data):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    bc = {}
    for key in BOOT_CONFIG_KEYS:
        bc[key] = data[key]
    resp = requests.put(api_url, json=bc)
    retval['msg'] = "Successfully added boot_config"
    retval['changed'] = True
    if bc['title'] in resp.json():
        new_bc = _get(data)
        if not _compare(bc, new_bc):
            retval['failed'] = True
            retval['msg'] = "Adding boot_config failed"
    else:
        retval['failed'] = True
        retval['msg'] = "Adding boot_config failed"
    return retval


def _present(data, check):
    retval = {'failed': False, 'changed': False}
    boot_configs = _get_boot_configs(data['sbm_uri'])
    if data['title'] in boot_configs:
        retval.update(_update(data, check))
    else:
        if check:
            retval['changed'] = True
        else:
            retval.update(_add(data))
    return retval


def _absent(data, check):
    retval = {'failed': False, 'changed': False}
    boot_configs = _get_boot_configs(data['sbm_uri'])
    if data['title'] in boot_configs:
        if check:
            retval['changed'] = True
        else:
            retval.update(_remove(data))
    return retval


def main():
    fields = {
        'sbm_uri': {'required': True, "type": 'str'},
        'title': {'required': True, 'type': 'str'},
        'config': {'type': 'str'},
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
