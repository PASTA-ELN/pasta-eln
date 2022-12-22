#!/usr/bin/python3
"""  Methods that check, repair, the local PASTA-ELN installation """
import os, platform, sys, json, shutil
import importlib.util
import urllib.request
from pathlib import Path

from globalDefinition import pasta
from fixedStrings import ontology
from backend import Pasta

def getOS():
  """
  Get operating system and python environment

  Returns:
    string: os + pythonEnvironment
  """
  os = platform.system()
  # Get base/real prefix, or sys.prefix if there is none
  get_base_prefix_compat = getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix
  in_virtualenv = get_base_prefix_compat != sys.prefix
  environment = sys.prefix if in_virtualenv else '_system_'
  return os+' '+environment


def gitAnnex(command='test'):
  """
  test git-annex installation or install it

  Args:
    command: 'test' or 'install'

  Returns:
    string: '' for success, filled with errors
  """
  if command == 'test':
    if shutil.which('git-annex') is None:
      return '**ERROR: git-annex not installed'
    # found = importlib.util.find_spec('datalad')
    #Has information if global or local installed
    # ModuleSpec(name='datalad', origin='/usr/local/lib/python3.8/dist-packages/datalad/__init__.py')
    return ''

  elif command == 'install':
    if platform.system()=='Linux':
      bashCommand = [
        'sudo wget -q http://neuro.debian.net/lists/focal.de-fzj.full -O /etc/apt/sources.list.d/neurodebian.sources.list',
        'sudo apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9',
        'sudo apt-get update',
        'sudo apt-get install -y git-annex-standalone',
        'echo "DONE installing git-annex"',
        'sleep 10000']
      os.system('xterm -e "'+'; '.join(bashCommand)+'"')
      return ''
    return '**ERROR: Unknown operating system '+platform.system()

  return '**ERROR: Unknown command'


def couchdb(command='test'):
  """
  test couchDB installation or install it

  Args:
    command: 'test' or 'install'

  Returns:
    string: '' for success, filled with errors
  """
  if command == 'test':
    with urllib.request.urlopen('http://127.0.0.1:5984') as package:
      contents = package.read()
      if json.loads(contents)['couchdb'] == 'Welcome':
        return ''
    return '**ERROR**'

  elif command == 'install':
    if platform.system()=='Linux':
      password = ''.join(random.choice(string.ascii_letters) for i in range(12))
      bashCommand = [
        'sudo snap install couchdb',
        'sudo snap set couchdb admin='+password,
        'sudo snap start couchdb',
        'sudo snap connect couchdb:mount-observe',
        'sudo snap connect couchdb:process-control',
        'sleep 5',
        'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_users',
        'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_replicator',
        'curl -X PUT http://admin:'+password+'@127.0.0.1:5984/_global_changes',
        'echo "DONE installing couchDB"',
        'sleep 10000']
      os.system('xterm -e "'+'; '.join(bashCommand)+'"')
      #create or adopt .pastaELN.json
      path = Path.home()/'.pastaELN.json'
      if path.exists():
        with open(path,'r', encoding='utf-8') as fConf:
          conf = json.load(fConf)
      else:
        conf = {}
        conf['default']     = 'research'
        conf['links']       = {'research':{\
                                'local':{'user':'admin', 'password':password, 'database':'research'},
                                'remote':{}  }}
        conf['version']     = 1
        conf['userID']      = os.getlogin()
        conf['extractors']  = {}
        conf['qrPrinter']   = {}
        conf['magicTags']   = ['P1','P2','P3','TODO','WAIT','DONE']
      with open(path,'w') as fConf:
        fConf.write(json.dumps(conf, indent=2) )
      return 'Password: '+password
    return '**ERROR: Unknown operating system '+platform.system()

  return '**ERROR: Unknown command'


def configuration(command='test'):
  """
  Check configuration file .pastaELN.json for consistencies

  Args:
    command: 'test' or 'repair'

  Returns:
    string: ''=success, else error messages
  """
  output = ''
  with open(Path.home()/'.pastaELN.json','r', encoding='utf-8') as fConf:
    conf = json.load(fConf)

  illegalNames = [key for key in conf if key.startswith('-')]
  if not 'softwareDir' in conf:
    if command == 'repair':
      conf['softwareDir'] = os.path.dirname(os.path.abspath(__file__))
    else:
      output += '**ERROR: No softwareDir in config file\n'
  if not 'userID' in conf:
    if command == 'repair':
      conf['userID'] = os.getlogin()
    else:
      output += '**ERROR: No userID in config file\n'
  if not 'magicTags' in conf:
    if command == 'repair':
      conf['magicTags'] = []
    else:
      output += '**ERROR: No magicTags in config file\n'
  if not 'qrPrinter' in conf:
    if command == 'repair':
      conf['qrPrinter'] = {}
    else:
      output += '**ERROR: No qrPrinter in config file\n'
  if not 'tableFormat' in conf:
    if command == 'repair':
      conf['tableFormat'] = {}
    else:
      output += '**ERROR: No tableFormat in config file\n'
  if not 'extractors' in conf:
    if command == 'repair':
      conf['extractors'] = {}
    else:
      output += '**ERROR: No extractors in config file\n'
  if not "version" in conf or conf['version']!=1:
    if command == 'repair':
      conf['version'] = 1
    else:
      output += '**ERROR: No or wrong version in config file\n'
  if not "links" in conf:
    output += '**ERROR: No links in config file; REPAIR MANUALLY\n'

  if not "default" in conf:
    if repair and len(illegalNames)==0:
      conf['default'] = list(conf['links'].keys())[0]
    else:
      output += '**ERROR: No default links in config file\n'
  else:
    if not conf['default'] in conf['links']:
      if command == 'repair':
        conf['default'] = list(conf['links'].keys())[0]
      else:
        output += '**ERROR: default entry '+conf['default']+' not in links\n'
  if len(illegalNames)>0:
    if command == 'repair':
      for key in illegalNames:
        del conf[key]
    else:
      output += '**ERROR: - type entries '+str(illegalNames)+' in config file\n'

  if command == 'repair':
    with open(Path.home()/'.pastaELN.json','w', encoding='utf-8') as f:
      f.write(json.dumps(conf,indent=2))
  return output


def ontology(command='test'):
  """
  Check configuration file .pastaELN.json for consistencies

  Args:
    command: 'test' or 'install'

  Returns:
    string: ''=success, else error messages
  """
  global pasta
  output = ''
  if pasta is None:
    pasta = Pasta()

  if command == 'test':
    output += 'database name:'+pasta.db.db.database_name+'\n'
    designDocuments = pasta.db.db.design_documents()
    output += 'Design documents'+'\n'
    for item in designDocuments:
      numViews = len(item['doc']['views']) if 'views' in item['doc'] else 0
      output += '  '+item['id']+'   Num. of views:'+str(numViews)+'\n'
    try:
      _ = pasta.db.getDoc('-ontology-')
      output += 'Ontology exists on server'+'\n'
    except:
      output += '**ERROR: Ontology does NOT exist on server'+'\n'
    return output

  elif command == 'install':
    doc = json.loads(ontology)
    print(doc)
    # _ = pasta.db.create_document(doc)
    return ''

  return '**ERROR: Unknown command'


if __name__ == '__main__':
  print('---- Test PASTA-ELN installation----')
  print('getOS        :', getOS())
  print('git-annex    :', gitAnnex())
  print('chouchDB     :', couchdb())
  print('configuration:', configuration())
  print('ontology     :\n'+ontology())

  if len(sys.argv)>1:
    print('---- Create PASTA-ELN installation----')
    print('install git-annex    :', gitAnnex('install'))
    print('install couchDB      :', couchdb('install'))
    print('repair  configuration:', configuration('repair'))
    print('install ontology     :', ontology('install'))