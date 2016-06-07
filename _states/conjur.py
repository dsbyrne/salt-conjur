'''
Conjur
'''

import salt
import httplib
import json
import urllib
import yaml
import os
import netrc
import urlparse
import stat 

def _token_exchange(appliance_url, host_factory_token, host_id):
  appliance_netloc = urlparse.urlparse(appliance_url).netloc
  host_param = urllib.urlencode({'id': host_id})
  headers = {'Authorization': 'Token token="{}"'.format(host_factory_token)}
  conjur = httplib.HTTPSConnection(appliance_netloc)
  conjur.set_debuglevel(3)
  conjur.request('POST', '/api/host_factories/hosts?{}'.format(host_param), None, headers)

  response = conjur.getresponse()

  if response.status == 401:
    raise "The token was not accepted"
  elif response.status == 422:
    raise "Invalid arguments"
  elif response.status != 201:
    raise "Unknown error"

  return json.loads(response.read())

def _get_account(appliance_url):
  appliance_netloc = urlparse.urlparse(appliance_url).netloc
  conjur = httplib.HTTPSConnection(appliance_netloc)
  conjur.request('GET', '/api/info')

  response = conjur.getresponse()

  if response.status != 200:
    raise "Unable to retrieve info from server"

  return json.loads(response.read())['account']

def _write_file(path, data, perm):
  with open(path, 'w') as file:
    file.write(data)

  os.chmod(path, perm)
  os.chown(path, 0, 0)

def machine_identity(name, appliance_url, host_id, host_factory_token):
  '''
  Exchange a host factory token for a machine identity
  
  CLI Example::
    salt '*' conjur.machine_identity XXXXXXXXXXXXXXXXX
  '''
  ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

  try:
    identity = _token_exchange(appliance_url, host_factory_token, host_id)
    account = _get_account(appliance_url)
    
    ret['comment'] = 'Registered as "host/{}"'.format(identity['id'])

    conjur_conf = { 'account': account, 
                    'appliance_url': appliance_url, 
                    'cert_file': '/etc/conjur.pem',
                    'netrc_path': '/etc/conjur.identity' }

    conjur_identity = 'machine {}/authn\nlogin host/{}\npassword {}'.format(appliance_url, identity['id'], identity['api_key'])

    _write_file('/etc/conjur.conf', yaml.safe_dump(conjur_conf, default_flow_style=False), stat.S_IRUSR | stat.S_IWUSR)
    _write_file('/etc/conjur.identity', conjur_identity, stat.S_IRUSR | stat.S_IWUSR)
  except:
    ret['result'] = False

  return ret