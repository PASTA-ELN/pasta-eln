#!/usr/bin/python3
"""  Methods that check, repair, the local PASTA-ELN installation """
import os, platform, sys, json, shutil, random, string
import importlib.util
import urllib.request
from pathlib import Path

from backend import Pasta
from fixedStrings import defaultOntology


def getOS():
  """
  Get operating system and python environment

  Returns:
    string: os + pythonEnvironment
  """
  operatingSys = platform.system()
  # Get base/real prefix, or sys.prefix if there is none
  get_base_prefix_compat = getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix
  in_virtualenv = get_base_prefix_compat != sys.prefix
  environment = sys.prefix if in_virtualenv else '_system_'
  return operatingSys+' '+environment



def gitAnnex(command='test'):
  """
  test git-annex installation or install it

  Args:
    command (string): 'test' or 'install'

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
    import webbrowser
    if platform.system()=='Linux':
      bashCommand = [
        'sudo wget -q http://neuro.debian.net/lists/focal.de-fzj.full -O /etc/apt/sources.list.d/neurodebian.sources.list',
        'sudo apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9',
        'sudo apt-get update',
        'sudo apt-get install -y git-annex-standalone',
        'echo DONE',
        'sleep 10000']
      os.system('xterm -e "'+'; '.join(bashCommand)+'"')
      return ''
    return '**ERROR: Unknown operating system '+platform.system()

  return '**ERROR: Unknown command'



def couchdb(command='test'):
  """
  test couchDB installation or install it

  Args:
    command (string): 'test' or 'install'

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
      pathPasta = Path.home()/'PASTA_ELN'
      if path.exists():
        with open(path,'r', encoding='utf-8') as fConf:
          conf = json.load(fConf)
      else:
        conf = {}

        conf['default']     = 'research'
        conf['links']       = {'research':{\
                                'local':{'user':'admin', 'password':password, 'database':'research', 'path':pathPasta},
                                'remote':{}  }}
        conf['version']     = 1
        conf['userID']      = os.getlogin()
        conf['extractors']  = {}
        conf['qrPrinter']   = {}
        conf['magicTags']   = ['P1','P2','P3','TODO','WAIT','DONE']
      with open(path,'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(conf, indent=2) )
      return 'Password: '+password
    return '**ERROR: Unknown operating system '+platform.system()

  return '**ERROR: Unknown command'



def configuration(command='test'):
  """
  Check configuration file .pastaELN.json for consistencies

  Args:
    command (string): 'test' or 'repair'

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
    if command == 'repair' and len(illegalNames)==0:
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
    command (string): 'test' or 'install'

  Returns:
    string: ''=success, else error messages
  """
  output = ''
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
    doc = json.loads(defaultOntology)
    print(doc)
    # _ = pasta.db.create_document(doc)
    return ''

  return '**ERROR: Unknown command'



def exampleData():
  """
  Create example data after installation
  """
  configName = 'research'
  pasta = Pasta(configName, initViews=True, initConfig=False)
  ### CREATE PROJECTS AND SHOW
  print('*** CREATE EXAMPLE PROJECT AND SHOW ***')
  pasta.addData('x0', {'-name': "PASTA's Example Project", 'objective': 'Test if everything is working as intended.', 'status': 'active', 'comment': '#tag Can be used as reference or deleted'})
  print(pasta.output('x0'))

  ### TEST PROJECT PLANING
  print('*** TEST PROJECT PLANING ***')
  viewProj = pasta.db.getView('viewDocType/x0')
  projID1  = [i['id'] for i in viewProj if 'PASTA' in i['value'][0]][0]
  pasta.changeHierarchy(projID1)
  pasta.addData('x1',    {'comment': 'This is hard! #TODO', '-name': 'This is an example task'})
  pasta.addData('x1',    {'comment': 'This will take a long time. #WAIT', '-name': 'This is another example task'})
  pasta.changeHierarchy(pasta.currentID)
  pasta.addData('x2',    {'-name': 'This is an example subtask',     'comment': 'Random comment 1'})
  pasta.addData('x2',    {'-name': 'This is another example subtask','comment': 'Random comment 2'})
  pasta.changeHierarchy(None)
  pasta.addData('x1',    {'-name': 'Data files'})
  semStepID = pasta.currentID
  pasta.changeHierarchy(semStepID)
  semDirName = pasta.basePath/pasta.cwd
  pasta.changeHierarchy(None)
  print(pasta.outputHierarchy())

  ### TEST PROCEDURES
  print('\n*** TEST PROCEDURES ***')
  sopDir = pasta.basePath/'StandardOperatingProcedures'
  os.makedirs(sopDir)
  with open(sopDir/'Example_SOP.md','w', encoding='utf-8') as fOut:
    fOut.write('# Put sample in instrument\n# Do something\nDo not forget to\n- not do anything wrong\n- **USE BOLD LETTERS**\n')
  pasta.addData('procedure', {'-name': 'StandardOperatingProcedures/Example_SOP.md', 'comment': '#v1'})
  print(pasta.output('procedure'))

  ### TEST SAMPLES
  print('*** TEST SAMPLES ***')
  pasta.addData('sample',    {'-name': 'Example sample', 'chemistry': 'A2B2C3', 'qrCode': '13214124 99698708', 'comment': 'can be used as example or removed'})
  print(pasta.output('sample'))
  print(pasta.outputQR())

  ###  TEST MEASUREMENTS AND SCANNING/CURATION
  print('*** TEST MEASUREMENTS AND SCANNING/CURATION ***')
  shutil.copy(pasta.softwarePath/'ExampleMeasurements/simple.png', semDirName)
  shutil.copy(pasta.softwarePath/'ExampleMeasurements/simple.csv', semDirName)
  pasta.scanTree()

  ### USE GLOBAL FILES
  print('*** USE GLOBAL FILES ***')
  pasta.changeHierarchy(semStepID)
  pasta.addData('measurement', {'-name': 'https://developers.google.com/search/mobile-sites/imgs/mobile-seo/separate-urls.png', \
    'comment':'remote image from google. Used for testing and reference. Can be deleted.'})
  print(pasta.output('measurement'))

  ### VERIFY DATABASE INTEGRITY
  print("\n*** VERIFY DATABASE INTEGRITY ***")
  print(pasta.checkDB(verbose=True))
  print('\n*** DONE WITH VERIFY ***')
  return


##############
# Main method for testing and installation without GUI
def main():
  """ Main method and entry point for commands """
  print('---- Test PASTA-ELN installation----')
  print('getOS        :', getOS())
  print('git-annex    :', gitAnnex())
  print('chouchDB     :', couchdb())
  print('configuration:', configuration())
  print('ontology     :\n'+ontology())
  print("Add any argument to install PASTA-ELN. Don't do it if PASTA-ELN is already installed.")

  if len(sys.argv)>1:
    print('---- Create PASTA-ELN installation----')
    print('install git-annex    :', gitAnnex('install'))
    print('install couchDB      :', couchdb('install'))
    print('repair  configuration:', configuration('repair'))
    print('install ontology     :', ontology('install'))
    print('create example data  :', exampleData())

if __name__ == '__main__':
  main()
