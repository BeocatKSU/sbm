#!/usr/bin/python
import requests

# Host uri
host = 'http://127.0.0.1:5000/'

# Testing Boot Configs
boot_config = {'title': 'testing', 'config': '#!ipxe\nkernel tftp://tyr.beocat.ksu.edu/kernels/dwarves\ninitrd tftp://tyr.beocat.ksu.edu/initrds/squashfs\n'}

# Testing Variables
var = {'key': 'testvar', 'value': '#!ipxe\n'}

# Testing Machines
machine_config = {'hostname': 'test', 'default_boot': 'testing', 'alternate_boot': 'testing', 'switch_type': 'switched', 'time_between': 600}

## Adding new boot_config
bc_put_url = host + 'api/v1/boot_config/'
tbc = boot_config
bca = requests.put(bc_put_url, json=tbc)
print(bca.json())

## Adding new variable
v_put_url = host + 'api/v1/variable/'
tvar = var
va = requests.put(v_put_url, json=tvar)
print(va.json())

## Adding new machine
mac_put_url = host + 'api/v1/machine/'
tmc = machine_config
mca = requests.put(mac_put_url, json=tmc)
print(mca.json())

## Updating existing boot_config
bc_post_url = host + 'api/v1/boot_config/' + boot_config['title'] + '/'
tbc['config'] += "boot\n"
bcu = requests.post(bc_post_url, json=tbc)
print(bcu.json())

## Updating existing variable
v_post_url = host + 'api/v1/variable/' + var['key'] + '/'
tvar['value'] = '#!ipxe\n#testing\n'
vu = requests.post(v_post_url, json=tvar)
print(vu.json())

## Updating existing machine
mac_post_url = host + 'api/v1/machine/' + tmc['hostname'] + '/'
tmc['switch_type'] = 'timed'
mcu = requests.post(mac_post_url, json=tmc)
print(mcu.json())

## Deleting existing boot_config
bc_delete_url = host + 'api/v1/boot_config/' + boot_config['title'] + '/'
bcd = requests.delete(bc_delete_url)
print(bcd.json())

## Deleting existing variable
v_delete_url = host + 'api/v1/variable/' + var['key'] + '/'
vd = requests.delete(v_delete_url)
print(vd.json())

## Deleting existing machine
mac_delete_url = host + 'api/v1/machine/' + tmc['hostname'] + '/'
mcd = requests.delete(mac_delete_url)
print(mcd.json())
