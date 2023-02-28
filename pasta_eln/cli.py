""" OLD Main function when command-line commands used

Called by user or react-electron frontend. Keep it simple: only functions that
are required by frontend. Otherwise, make only temporary changes
"""
import json, sys, argparse, traceback
from pathlib import Path
from subprocess import run, PIPE, STDOUT
import urllib.request

from pasta_eln import __version__
from .backend import Backend
from .miscTools import upOut, upIn, updateExtractorList
from .inputOutput import importELN, exportELN
from .installationTools import configuration as checkConfiguration

def commands(getDocu, args):
  """
  Main function

  Args:
    getDocu (bool): True=return documentation string; False=use arguments
    args (argparse.Namespace): arguments supplied by user / frontend

  Returns:
    string: documentation or empty string
  """
  doc = ''
  success = ''  #success ''=undecided; '-1'=False; '1'=True
  pathConfig = Path.home()/'.pastaELN.json'

  ##################################################
  ## general things that do not require open database / change configuration file
  if getDocu:
    doc += '  help: help information\n'
    doc += '    example: pastaELN.py help\n'
  elif args.command=='help':
    print("HELP:")
    return '1'

  doc += '\n-- Configuration file commands --\n'
  if getDocu:
    doc += '  verifyConfiguration: verify configuration file\n'
    doc += '    example: pastaELN.py verifyConfiguration\n'
    doc += '    example: pastaELN.py verifyConfigurationRepair (repair function)\n'
  elif args.command.startswith('verifyConfiguration'):
    command = 'repair' if args.command=='verifyConfigurationRepair' else 'test'
    output = checkConfiguration(command=command)
    print(output)
    return '-1' if '**ERROR' in output else '1'

  if getDocu:
    doc += '  extractorScan: get list of all extractors and save into .pastaELN.json\n'
    doc += '    example: pastaELN.py extractorScan\n'
  elif args.command=='extractorScan':
    with open(pathConfig,'r', encoding='utf-8') as f:
      configuration = json.load(f)
      pathToExtractors = Path(__file__).parent / 'extractors' \
        if 'extractorDir' not in configuration \
        else configuration['extractorDir']
    updateExtractorList(pathToExtractors)
    return '1'

  if not getDocu and args.command=='up':
    print('up:',upOut(args.docID))
    return '1'

  if getDocu:
    doc += '  scramble: scramble the password and user name in configuration file\n'
    doc += '    example: pastaELN.py scramble\n'
  elif args.command=='scramble':
    with open(pathConfig,'r', encoding='utf-8') as f:
      configuration = json.load(f)
    configBackup  = dict(configuration)
    links = configuration['links']
    changed = False
    for link,site in [(i,j) for i in links.keys() for j in ['local','remote']]:
      if 'user' in links[link][site] and 'password' in links[link][site]:
        links[link][site]['cred'] = upIn(links[link][site]['user']+':'+links[link][site]['password'])
        del links[link][site]['user']
        del links[link][site]['password']
        changed = True
    if changed:
      with open(Path.home()/'.pastaELN_BAK.json','w', encoding='utf-8') as f:
        f.write(json.dumps(configBackup,indent=2))
      with open(pathConfig,'w', encoding='utf-8') as f:
        f.write(json.dumps(configuration,indent=2))
    return '1'

  if getDocu:
    doc += '  decipher: decipher encrypted string\n'
    doc += '    content: string\n'
  elif args.command=='decipher':
    from serverActions import passwordDecrypt
    print(passwordDecrypt(args.content).decode())
    return '1'


  ##################################################
  ## Commands that require open PASTA database, but not specific project
  doc += '\n-- Commands that interact with backend --\n'
  try:
    # use configuration file
    if not getDocu:
      with open(pathConfig,'r', encoding='utf-8') as f:
        config = json.load(f)
      if args.database=='':
        args.database = config['default']

    initViews, initConfig, resetOntology = False, True, False
    if getDocu:
      doc += '  test: test PASTA setup\n'
      doc += '    example: pastaELN.py test -d instruments\n'
    elif args.command.startswith('test'):
      #PART 1 of test: precede with configuration test
      initViews, initConfig = True, True
      if args.command=='testDev':
        resetOntology = True
      output = "" #checkConfiguration(repair=False)  #verify configuration file .pastaELN.py
      print(output)
      if 'ERROR' in output:
        return ''
      # local and remote server test
      urls = ['http://127.0.0.1:5984']
      if config['links'][args.database]['remote']!={}:
        urls.append(config['links'][args.database]['remote']['url'])
      for url in urls:
        try:
          with urllib.request.urlopen(url) as package:
            contents = package.read()
            if json.loads(contents)['couchdb'] == 'Welcome':
              print('CouchDB server',url,'is working: username and password test upcoming')
        except:
          print('**ERROR pma01: CouchDB server not working |',url)
          if url=='http://127.0.0.1:5984':
            raise NameError('**ERROR pma01a: Wrong local server.') from None

    #open backend
    if not getDocu:
      try:
        be = Backend(linkDefault=args.database, initViews=initViews, initConfig=initConfig,
                  resetOntology=resetOntology)
      except:
        print('**ERROR pma20: backend could not be started.\n'+traceback.format_exc()+'\n\n')
        return ''

    if not getDocu and args.command.startswith('test') and be:
      #PART 2 of test: main test
      print('database server:',be.db.db.client.server_url)
      print('default link:',be.confLinkName)
      print('database name:',be.db.db.database_name)
      designDocuments = be.db.db.design_documents()
      print('Design documents')
      for item in designDocuments:
        numViews = len(item['doc']['views']) if 'views' in item['doc'] else 0
        print('  ',item['id'], '   Num. of views:', numViews )
      try:
        data = be.db.getDoc('-ontology-')
        print('Ontology exists on server')
      except:
        print('**ERROR pma02: Ontology does NOT exist on server')
      print('local directory:',be.basePath)
      print('software directory:',be.softwarePath)
      print('software version: '+__version__)
      return '1'

    if getDocu:
      doc += '  verifyDB: test PASTA database\n'
      doc += '    example: pastaELN.py verifyDB\n'
      doc += '    example: pastaELN.py verifyDBdev (repair function)\n'
    elif args.command.startswith('verifyDB'):
      repair = args.command=='verifyDBdev'
      output = be.checkDB(verbose=False, repair=repair)
      print(output)
      return '1'

    if getDocu:
      doc += '  syncLR / syncRL: synchronize with / from remote server\n'
      doc += '    example: pastaELN.py syncLR\n'
    elif args.command=='syncLR':
      success = be.replicateDB()
      return '1' if success else '-1'
    elif args.command=='syncRL':
      be.exit()
      print('**ERROR pma03: syncRL not implemented yet')
      return '-1'

    if getDocu:
      doc += '  print: print overview\n'
      doc += "    label: possible docLabels 'Projects', 'Samples', 'Measurements', 'Procedures'\n"
      doc += "    example: pastaELN.py print -d instruments -l instrument\n"
    elif args.command=='print':
      print(be.output(args.label,True))
      return '1'

    if getDocu:
      doc += '  saveBackup,loadBackup: save to file.zip / load from file.zip\n'
      doc += '    - docId is optional as it reduces the scope of the backup\n'
      doc += '    - database is optional as otherwise the default is used\n'
      doc += '    example: pastaELN.py saveBackup -d instruments\n'
      doc += '    example: pastaELN.py saveBackup -i x-76b0995cf655bcd487ccbdd8f9c68e1b\n'
    elif args.command=='saveBackup':   #save to backup file.zip
      if args.docID!='':
        exportELN(be, args.docID)
      else:
        be.backup('backup')

    elif args.command=='loadBackup':   #load from backup file.zip
      be.backup('restore')
      return '1'

    if getDocu:
      doc += '  importXLS: import first sheet of excel file into database\n'
      doc += '    before: ensure database configuration and project exist\n'
      doc += '    example: pastaELN.py importXLS -d instruments -i x-123456 -c "~/path/to.xls" -l instrument\n'
      doc += '    -l is the document type\n'
      doc += '    afterwards: adopt ontology (views are automatically generated)\n'
    elif args.command=='importXLS':
      import pandas as pd
      from commonTools import commonTools as cT  #not globally imported since confuses translation
      if args.docID!='':
        be.changeHierarchy(args.docID)
      #change for matwerks examples
      data = pd.read_excel(args.content, sheet_name=0)
      if data.shape[0]>40 and data.iloc[38].isnull().sum() < data.iloc[36].isnull().sum():
        data = pd.read_excel(args.content, sheet_name=0, skiprows=39, usecols=range(11))
        data=data.drop(data.index[[0,1]])
        data=data.drop(data.index[[-1,-2,-3]])
        #add metadata
        meta = pd.read_excel(args.content, sheet_name=0, skiprows=4, nrows=13, usecols=[0,2])
        for i in range(meta.shape[0]):
          key, value = meta.iloc[i,0], meta.iloc[i,1]
          data[key] = value
        #add more metadata
        meta = pd.read_excel(args.content, sheet_name=0, skiprows=19, nrows=8, usecols=[2,8])
        for i in range(meta.shape[0]):
          if meta.iloc[i,:].isnull().sum()==2:
            continue
          key, value = meta.iloc[i,0], meta.iloc[i,1]
          data[key] = value
        meta = pd.read_excel(args.content, sheet_name=0)
        data['batch'] = meta.iloc[1,0].split(' - ')[1].split(' ')[1]
        data['test']  = meta.iloc[1,0].split(' - ')[0][1:-1]
        data = data.rename(columns={"AMTwin label": "-name"})
      else:
        #default file
        data = pd.read_excel(args.content, sheet_name=0).fillna('')
      print(data.columns)
      print(data)
      for _, row in data.iterrows():
        data = dict((k.lower(), v) for k, v in row.items())
        be.addData(args.label, data )
      return '1'

    if getDocu:
      doc += '  createDoc: add document to database\n'
      doc += '    content is required as json-string\n'
      doc += "    example: pastaELN.py createDoc --content \"{'-name':'Instruments','docType':'project'}\"\n"
    elif args.command=='createDoc':
      from urllib import parse
      content = parse.unquote(args.content)
      data = json.loads(content)
      docType = data['docType']
      del data['docType']
      if len(args.docID)>1 and args.docID!='none':
        be.changeHierarchy(args.docID)
      be.addData(docType,data)
      return '1'

    if getDocu:
      doc += '  redo: recreate thumbnail / use-extractor\n'
      doc += '    example: pastaELN.py redo -i m-1234567890abcdefghijklmnopqrstuv -c type/test/subtest\n'
    elif args.command=='redo':
      data = dict(be.getDoc(args.docID))
      data['-type'] = args.content.split('/')
      be.useExtractors(data['-branch'][0]['path'], data['shasum'], data, extractorRedo=True)  #any path is good since the file is the same everywhere; data-changed by reference
      if len(data['-type'])>1 and len(data['image'])>1:
        be.db.updateDoc({'image':data['image'], '-type':data['-type']},args.docID)
        return '1'
      else:
        print('**ERROR pma06: error after redo-extraction')
        return '-1'

    ##################################################
    ## Commands that require open database and open project
    doc += '\n-- Commands that interact with a special project --\n'
    if not getDocu and args.docID!='':
      be.changeHierarchy(args.docID)

    if getDocu:
      doc += '  scanHierarchy: scan project with docID\n'
      doc += '    example: pastaELN.py scanHierarchy -i ....\n'
    elif args.command=='scanHierarchy':
      be.scanTree()
      return '1'

    if getDocu:
      doc += '  hierarchy: print document hierarchy\n'
      doc += '    example: pastaELN.py hierarchy -i x-1234567890abc'
    elif args.command=='hierarchy':
      print(be.outputHierarchy(True,True))
      return '1'

  except:
    print("**ERROR pma10: exception thrown during pastaELN.py"+traceback.format_exc()+"\n")
    raise

  if not getDocu and be is not None:
    be.exit()
  return doc

###################
## MAIN FUNCTION ##
def main():
  """
  Main function
  """
  usage = "pastaELN.py <command> [-i docID] [-c content] [-l labels] [-d database]\n\n"
  usage+= "Possible commands are:\n"
  usage+= commands(True, None)
  argparser = argparse.ArgumentParser(usage=usage)
  argparser.add_argument('command', help='see above...')
  argparser.add_argument('-i','--docID',   help='docID of project; a long alpha-numeric code', default='')
  argparser.add_argument('-c','--content', help='content to save/store', default=None)
  argparser.add_argument('-l','--label',   help='label used for printing', default='x0')
  argparser.add_argument('-d','--database',help='name of database configuration', default='') #required for be = Pasta(args.database)
  arguments = argparser.parse_args()
  result = commands(False, arguments)
  if arguments.command=='help':
    argparser.print_help()
  if result == '':
    print('**ERROR pma08: command in pastaELN.py does not exist |',arguments.command)
  elif result == '1' and arguments.command!='up':
    print('SUCCESS')
