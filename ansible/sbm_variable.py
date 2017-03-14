#!/usr/bin/python
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
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
    vr = requests.get(api_url)
    vr.raise_for_status()
    return vr.json()


def _get(data):
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['key'] + '/')
    vr = requests.get(api_url)
    vr.raise_for_status()
    return vr.json()


def _remove(data):
    retval = {'failed': True, 'changed': False}
    api_url = urljoin(data['sbm_uri'], API_BASE)
    api_url = urljoin(api_url, data['key'] + '/')
    dr = requests.delete(api_url)
    try:
        resp = dr.json()
        if 'status' not in resp.keys() or resp['status'] != 'ok':
            retval['msg'] = "Failed to remove variable"
        else:
            retval['changed'] = True
            retval['failed'] = False
            retval['msg'] = "Successfully removed variable"
    except:
        retval['msg'] = "API did not respond with JSON"
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
    try:
        var = _get(data)
    except HTTPError:
        retval['msg'] = 'API Error on _get'
        retval['failed'] = True
        return retval
    new_var = {}
    for key in VARIABLE_KEYS:
        new_var[key] = data[key]
    retval['msg'] = 'Successfully confirmed variable'
    if not _compare(var, new_var):
        retval['msg'] = 'Successfully updated variable'
        retval['changed'] = True
        if not check:
            resp = requests.post(api_url, json=new_var)
            if resp.status_code != 200:
                retval['msg'] = 'API Error on post'
                retval['failed'] = True
            else:
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
    if resp.status_code != 200:
        retval['msg'] = 'API Error on put'
        retval['failed'] = True
        return retval
    retval['msg'] = "Successfully added variable"
    retval['changed'] = True
    if var['key'] in resp.json():
        try:
            new_var = _get(data)
        except HTTPError:
            retval['msg'] = 'API Error on _get'
            retval['failed'] = True
        else:
            if not _compare(var, new_var):
                retval['failed'] = True
                retval['msg'] = "Adding variable failed"
    else:
        retval['failed'] = True
        retval['msg'] = "Adding variable failed"
    return retval


def _present(data, check):
    retval = {'failed': True, 'changed': False}
    try:
        variables = _get_variables(data['sbm_uri'])
    except (HTTPError, ConnectionError):
        retval['msg'] = 'API Failure, is SBM running at the specified URI?'
        return retval
    if data['key'] in variables:
        retval.update(_update(data, check))
    else:
        if check:
            retval['changed'] = True
            retval['failed'] = False
        else:
            retval.update(_add(data))
    return retval


def _absent(data, check):
    retval = {'failed': True, 'changed': False}
    try:
        variables = _get_variables(data['sbm_uri'])
    except (HTTPError, ConnectionError):
        retval['msg'] = 'API Failure, is SBM running at the specifed URI?'
        return retval
    if data['key'] in variables:
        if check:
            retval['changed'] = True
            retval['failed'] = False
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
