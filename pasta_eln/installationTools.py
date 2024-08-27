'''  Methods that check, repair, the local PASTA-ELN installation: no Qt-here '''
import os, platform, sys, json, shutil, logging
from typing import Optional, Any, Callable
from pathlib import Path
from .backend import Backend
from .fixedStringsJson import defaultConfiguration, configurationGUI, CONF_FILE_NAME
from .miscTools import outputString, DummyProgressBar


def getOS() -> str:
  '''
  Get operating system and python environment

  Returns:
    string: os + pythonEnvironment
  '''
  operatingSys = platform.system()
  # Get base/real prefix, or sys.prefix if there is none
  get_base_prefix_compat = getattr(sys, 'base_prefix', None) or getattr(sys, 'real_prefix', None) or sys.prefix
  in_virtualenv = get_base_prefix_compat != sys.prefix
  environment = sys.prefix if in_virtualenv else '_system_'
  return f'{operatingSys} {environment}'


def createDefaultConfiguration(pathPasta:Optional[Path]=None) -> dict[str,Any]:
  '''
  Create base of configuration file
  - basic project group
  - defaultProjectGroup
  - userID

  Args:
    pathPasta (Path): place to store pasta data

  Returns:
    dict: dictionary of configuration
  '''
  if pathPasta is None:
    if platform.system()=='Windows':
      pathPasta = Path.home()/'Documents'/'PASTA_ELN'
    else:
      pathPasta = Path.home()/'PASTA_ELN'
  conf: dict[str, Any] = {
      'defaultProjectGroup': 'research',
      'projectGroups': {
          'research': {
              'local': {'database': 'research', 'path': str(pathPasta)},
              'remote': {},
          }}, 'version': 3}
  try:
    conf['userID']      = os.getlogin()
  except Exception:   #github action
    conf['userID']      = 'github_user'
  #create pastaDir if it does not exist
  if not pathPasta.is_dir():
    pathPasta.mkdir()
  return conf


def configuration(command:str, pathData:str) -> str:
  '''
  Check configuration file for consistencies

  Args:
    command (str): 'test' or 'repair'
    pathData (Path): path to use for data

  Returns:
    string: ''=success, else error messages
  '''
  logging.info('Configuration starting ...')
  output = ''
  if Path(pathData).is_dir():
    pathPasta = Path(pathData).absolute()
  else:
    pathPasta = Path.home()/pathData
    pathPasta.mkdir(exist_ok=True)
  try:
    with open(Path.home()/CONF_FILE_NAME,'r', encoding='utf-8') as fConf:
      conf = json.load(fConf)
  except Exception:
    output += '**INFO configuration file does not exist\n'
    conf = createDefaultConfiguration(pathPasta) if command == 'repair' else {}
  logging.info(json.dumps(conf, indent=2))

  #check normal items
  for k,v in defaultConfiguration.items():
    if k not in conf:
      if command == 'repair':
        if isinstance(v,str) and v.startswith('$') and v.startswith('$'):
          v = eval(v[1:-1]) # pylint: disable=eval-used
        conf[k] = v
      else:
        output += outputString('text','error', f'No {k} in config file')
  #GUI items
  if 'GUI' not in conf:
    if command == 'repair':
      conf['GUI'] = {}
    else:
      output += outputString('text','error', 'No GUI in config file')
  for _, items in configurationGUI.items():
    for k,v in items.items():
      if 'GUI' in conf and k not in conf['GUI']:
        if command == 'repair':
          conf['GUI'][k] = v[1]
        else:
          output += outputString('text','error', f'No {k} in GUI part of config file')
  if command == 'repair':
    with open(Path.home()/CONF_FILE_NAME,'w', encoding='utf-8') as f:
      f.write(json.dumps(conf,indent=2))
  logging.info('Configuration ending')
  return output


def exampleData(force:bool=False, callbackPercent:Optional[Callable[[int],None]]=None) -> str:
  '''
  Create example data after installation

  Args:
    force (bool): force creation by removing content before creation
    callbackPercent (function): callback function given to exampleData, such that exampleData can report progress back
  '''
  logging.info('Start example data creation')
  outputFormat = 'print'
  if callbackPercent is not None:
    callbackPercent(0)
  if force:
    backend = Backend(initConfig=False)
    dirName = backend.basePath
    shutil.rmtree(dirName)
    os.makedirs(dirName)
  if callbackPercent is not None:
    callbackPercent(1)
  backend = Backend(initViews=True, initConfig=False)
  if callbackPercent is not None:
    callbackPercent(2)
  ### CREATE PROJECTS AND SHOW
  outputString(outputFormat,'h2','CREATE EXAMPLE PROJECT AND SHOW')
  backend.addData('x0', {'name': 'PASTAs Example Project', '.objective': 'Test if everything is working as intended.',
                         '.status': 'active', 'comment': '#Important Can be used as reference or deleted'})
  if callbackPercent is not None:
    callbackPercent(3)
  outputString(outputFormat,'info', backend.output('x0'))
  if callbackPercent is not None:
    callbackPercent(4)
  logging.info('Finished creating example project')

  ### TEST PROJECT PLANING
  outputString(outputFormat,'h2','TEST PROJECT PLANING')
  dfProj  = backend.db.getView('viewDocType/x0')
  projID1 = list(dfProj['id'])[0]
  if callbackPercent is not None:
    callbackPercent(5)
  backend.changeHierarchy(projID1)
  if callbackPercent is not None:
    callbackPercent(6)
  backend.addData('x1',    {'comment': 'This is hard! #TODO', 'name': 'This is an example task'})
  if callbackPercent is not None:
    callbackPercent(7)
  currentID = backend.addData('x1', {'comment': 'This will take a long time. #WAIT',
                                     'name': 'This is another example task'})['id']
  if callbackPercent is not None:
    callbackPercent(8)
  backend.changeHierarchy(currentID)
  if backend.cwd is not None:
    data2DirName = backend.basePath/backend.cwd
  else:
    return "**ERROR: backend is incorrect"
  backend.addData('x2',    {'name': 'This is an example subtask',     'comment': 'Random comment 1'})
  if callbackPercent is not None:
    callbackPercent(9)
  backend.addData('x2',    {'name': 'This is another example subtask','comment': 'Random comment 2'})
  if callbackPercent is not None:
    callbackPercent(10)
  backend.changeHierarchy(None)
  semStepID = backend.addData('x1',    {'name': 'Data files'})['id']
  if callbackPercent is not None:
    callbackPercent(11)
  backend.changeHierarchy(semStepID)
  if backend.cwd is not None:
    dataDirName = backend.basePath/backend.cwd
  else:
    return "**ERROR: backend is incorrect"
  backend.changeHierarchy(None)
  outputString(outputFormat,'info',backend.outputHierarchy())
  if callbackPercent is not None:
    callbackPercent(12)
  logging.info('Finished project planning')

  #TODO 2-branches copy the entire test-01 to here once finished
  ### TEST PROCEDURES
  outputString(outputFormat,'h2','TEST PROCEDURES')
  sopDir = backend.basePath/'StandardOperatingProcedures'
  os.makedirs(sopDir, exist_ok=True)
  with open(sopDir/'Example_SOP.md','w', encoding='utf-8') as fOut:
    fOut.write('# Put sample in instrument\n# Do something\nDo not forget to\n- not do anything wrong\n- **USE BOLD LETTERS**\n')
  if callbackPercent is not None:
    callbackPercent(13)
  backend.addData('procedure', {'name': 'StandardOperatingProcedures/Example_SOP.md', 'comment': '#v1'})
  if callbackPercent is not None:
    callbackPercent(14)
  outputString(outputFormat,'info',backend.output('procedure'))
  if callbackPercent is not None:
    callbackPercent(15)
  logging.info('Finished procedures creating')

  ### TEST SAMPLES
  outputString(outputFormat,'h2','TEST SAMPLES')
  backend.addData('sample',    {'name': 'Example sample', '.chemistry': 'A2B2C3', 'qrCode': '13214124 99698708', 'comment': 'can be used as example or removed'})
  if callbackPercent is not None:
    callbackPercent(16)
  outputString(outputFormat,'info',backend.output('sample'))
  if callbackPercent is not None:
    callbackPercent(17)
  outputString(outputFormat,'info',backend.outputQR())
  if callbackPercent is not None:
    callbackPercent(18)
  logging.info('Finished samples creating')

  ###  TEST MEASUREMENTS AND SCANNING/CURATION
  outputString(outputFormat,'h2','TEST MEASUREMENTS AND SCANNING')
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.png', dataDirName)
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.csv', dataDirName)
  if callbackPercent is not None:
    callbackPercent(19)
  logging.info('Finished copy files')
  progressBar = DummyProgressBar()
  backend.scanProject(progressBar, projID1)
  logging.info('Finished scan tree')
  if callbackPercent is not None:
    callbackPercent(20)

  ### USE GLOBAL FILES
  outputString(outputFormat,'h2','USE GLOBAL FILES')
  backend.changeHierarchy(semStepID)
  if callbackPercent is not None:
    callbackPercent(21)
  backend.addData('measurement', {
    'name': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Misc_pollen.jpg/315px-Misc_pollen.jpg',\
    'comment':'remote image from wikipedia. Used for testing and reference. Can be deleted.'})
  if callbackPercent is not None:
    callbackPercent(22)
  outputString(outputFormat,'info',backend.output('measurement'))
  if callbackPercent is not None:
    callbackPercent(23)
  logging.info('Finished global files additions')


  ###  TEST MEASUREMENTS AND SCANNING/CURATION
  outputString(outputFormat,'h2','TEST MEASUREMENTS AND SCANNING 2')
  shutil.copy(Path(__file__).parent/'Resources'/'ExampleMeasurements'/'simple.png', data2DirName)
  logging.info('Finished copy files 2')
  progressBar = DummyProgressBar()
  backend.scanProject(progressBar, projID1)
  logging.info('Finished scan tree 2')
  outputString(outputFormat,'info',backend.output('measurement'))


  ### VERIFY DATABASE INTEGRITY
  outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
  outputString(outputFormat,'info',backend.checkDB(outputStyle='text'))
  outputString(outputFormat,'h2','DONE WITH VERIFY')
  if callbackPercent is not None:
    callbackPercent(24)
  logging.info('Finished checking database')
  return 'Finished checking database'


def createShortcut() -> None:
  """
  Create alias and shortcut icon depending on operating system
  """
  logging.info('Create shortcut starting')
  if platform.system()=='Linux':
    content ='[Desktop Entry]\nName=PASTA ELN\nComment=PASTA electronic labnotebook\n'
    if sys.prefix==sys.base_prefix:   #normal installation into user-space
      content+='Exec=pastaELN\n'
    else:                             #installation in a virtual environment
      logging.info('In virtual environment, create an alias')
      with open(Path.home()/'.bashrc','a', encoding='utf-8') as fOut:
        alias = f"alias pastaELN='{sys.prefix}/bin/python3 -m pasta_eln.gui'"
        logging.info(alias)
        fOut.write(f'{alias}\n')
      content += f'Exec={sys.prefix}/bin/python3 -m pasta_eln.gui\n'
    content+='Icon='+ (Path(__file__).parent/'Resources'/'Icons'/'favicon64.png').as_posix() + '\n'
    content+='Terminal=false\nType=Application\nCategories=Science;Application;\n'
    try:
      linkString = (Path.home()/'Desktop'/'pastaELN.desktop').as_posix()
      with open(linkString,'w', encoding='utf-8') as fOut:
        fOut.write(content)
        os.system(f'gio set {linkString} metadata::trusted true') #for ubuntu systems
        os.chmod(Path.home()/'Desktop'/'pastaELN.desktop', 0o775)
    except Exception:
      pass
    try:
      with open(Path.home()/'.local'/'share'/'applications'/'pastaELN.desktop','w', encoding='utf-8') as fOut:
        fOut.write(content)
        os.chmod(Path.home()/'.local'/'share'/'applications'/'pastaELN.desktop', 0o777)
    except Exception:
      pass
  elif platform.system()=='Windows':
    import winshell
    from win32com.client import Dispatch
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut( os.path.join(winshell.desktop(), "pastaELN.lnk") )
    if env := os.environ.get('CONDA_PREFIX', ''):
      env = env.split('\\')[-1]  #just the env name
      user = os.getlogin()
      batContent = f"cmd.exe /c \"C:\\Users\\{user}\\anaconda3\\Scripts\\activate {env} && python -m pasta_eln.gui\""
      batLocation= f"C:\\Users\\{user}\\startPastaELN.bat"
      with open(batLocation, 'w', encoding='utf-8') as fBat:
        fBat.write(batContent)
      shortcut.Targetpath = batLocation
    else:
      shortcut.Targetpath = r"python -m pasta_eln.gui"
    shortcut.WorkingDirectory = str(Path.home())
    shortcut.IconLocation = str(Path(__file__).parent/'Resources'/'Icons'/'favicon64.ico')
    shortcut.save()
  logging.info('Create shortcut end')
  return


##############
# Main method for testing and installation without GUI
def main() -> None:
  ''' Main method and entry point for commands '''
  logPath = Path.home()/'pastaELN.log'
  #old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')   #This logging is always info, since for installation only
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA Install')
  print('---- Test PASTA-ELN installation----')
  print('--   if nothing reported: it is ok.')
  print('getOS        :', getOS())
  res = configuration('test','.')
  flagConfiguration = 'ERROR' in res
  print(res)

  print('Add "install" argument to install PASTA-ELN.')
  if len(sys.argv)>2 and 'install' in sys.argv:
    print('---- Create PASTA-ELN installation ----')
    print(sys.argv)
    if flagConfiguration:
      print('repair  configuration:', configuration('repair', sys.argv[2] ))
  print('Add "example" argument to create example data.')
  if len(sys.argv)>1 and 'example' in sys.argv:
    print('---- Create Example data ----')
    print('create example data  :', exampleData())

  logging.info('End PASTA Install')
  return

# called by python3 -m pasta_eln.installTools
if __name__ == '__main__':
  main()
