#!/usr/bin/python
import requests
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from ansible.module_utils.basic import *

API_BASE = '/api/v1/variable/'
VARIABLE_KEYS = [
    'key',
    'value'
]


def _get_variables(uri):
    api_url = urljoin(uri, API_BASE)
    return requests.get(api_url).json()


def _get(data):
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['key'] + '/')
    return requests.get(api_url).json()


def _remove(data):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['key'] + '/')
    resp = requests.delete(api_url).json()
    if 'status' not in resp.keys() or resp['status'] != 'ok':
        retval['failed'] = True
        retval['msg'] = "Failed to remove variable"
    else:
        retval['changed'] = True
        retval['msg'] = "Successfully removed variable"
    return retval


def _compare(v1, v2):
    for key in VARIABLE_KEYS:
        if v1[key] != v2[key]:
            return False
    return True


def _update(data, check):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['key'] + '/')
    var = _get(data)
    new_var = {}
    for key in VARIABLE_KEYS:
        new_var[key] = data[key]
    retval['msg'] = 'Successfully confirmed variable'
    if not _compare(var, new_var):
        retval['msg'] = 'Successfully updated variable'
        retval['changed'] = True
        if not check:
            resp = requests.post(api_url, json=new_var)
            if not _compare(new_var, resp.json()):
                retval['msg'] = 'Updated variable not as expected'
                retval['failed'] = True
    return retval


def _add(data):
    retval = {'failed': False, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    var = {}
    for key in VARIABLE_KEYS:
        var[key] = data[key]
    resp = requests.put(api_url, json=var)
    retval['msg'] = "Successfully added variable"
    retval['changed'] = True
    if var['key'] in resp.json():
        new_var = _get(data)
        if not _compare(var, new_var):
            retval['failed'] = True
            retval['msg'] = "Adding variable failed"
    else:
        retval['failed'] = True
        retval['msg'] = "Adding variable failed"
    return retval


def _present(data, check):
    retval = {'failed': False, 'changed': False}
    variables = _get_variables(data['sbm_uri'])
    if data['key'] in variables:
        retval.update(_update(data, check))
    else:
        if check:
            retval['changed'] = True
        else:
            retval.update(_add(data))
    return retval


def _absent(data, check):
    retval = {'failed': False, 'changed': False}
    variables = _get_variables(data['sbm_uri'])
    if data['key'] in variables:
        if check:
            retval['changed'] = True
        else:
            retval.update(_remove(data))
    return retval


def main():
    fields = {
        'sbm_uri': {'required': True, "type": 'str'},
        'key': {'required': True, 'type': 'str'},
        'value': {'type': 'str'},
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
