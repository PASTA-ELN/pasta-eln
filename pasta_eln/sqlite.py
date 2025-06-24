""" Class for interaction with sqlite """
import base64
import copy
import io
import json
import logging
import os
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional, Union
import pandas as pd
from anytree import Node
from PIL import Image
from .fixedStringsJson import SQLiteTranslation, defaultDefinitions, defaultDocTypes, defaultSchema
from .miscTools import hierarchy
from .textTools.stringChanges import camelCase, createDirName, outputString, tracebackString

MAIN_ORDER     =['id'  ,'name','user','type','dateCreated','dateModified','gui',      'client','shasum','image','content','comment','externalId','dateSync']
MAIN_TYPE      =['TEXT','TEXT','TEXT','TEXT','TEXT',       'TEXT',        'varchar(2)','TEXT',  'TEXT',  'TEXT', 'TEXT',   'TEXT',   'TEXT',     'TEXT']
DOC_TYPES      =['docType', 'PURL','title','icon','shortcut','view']
DOC_TYPE_SCHEMA=['docType', 'class', 'idx', 'name', 'unit', 'mandatory', 'list']


class SqlLiteDB:
  """
  Class for interaction with sqlite
  """


  def __init__(self, resetDataHierarchy:bool=False, basePath:Path=Path()):
    """
    Args:
      configuration (dict): configuration of GUI elements
      resetDataHierarchy (bool): reset dataHierarchy
      basePath (Path): path of project group
    """
    self.connection = sqlite3.connect(basePath/'pastaELN.db', check_same_thread=False)
    self.basePath   = basePath
    self.cursor     = self.connection.cursor()
    self.dataHierarchyInit(resetDataHierarchy)
    # main table
    self.createSQLTable('main',            MAIN_ORDER,                                  'id', MAIN_TYPE)
    # branches table
    self.createSQLTable('branches', ['id','idx','stack','child','path','show'],'id, idx', ['TEXT','INTEGER']*2+['TEXT']*2)
    # metadata table
    # - contains metadata of specific item
    # - key is generally not shown to user
    # - flattened key
    # - can be adopted by adv. user
    self.createSQLTable('properties',      ['id','key','value','unit'],                'id, key')
    # tables: each item can have multiple of these: tags, qrCodes
    self.createSQLTable('tags',            ['id','tag'],                               'id, tag')
    self.createSQLTable('qrCodes',         ['id','qrCode'],                            'id, qrCode')
    # list of changes to attachments
    self.createSQLTable('attachments',     ['id','location','date','guest','remark','user'], 'id, location, date')
    # list of changes to all documents: gives history
    self.createSQLTable('changes',         ['id','date','change'],                     'id, date')
    return


  def dataHierarchyInit(self, resetDataHierarchy:bool=False) -> None:
    """
    create data hierarchy in sqlite database

    Args:
      resetDataHierarchy (bool): recreate the data hierarchy from default state
    """
    self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [i[0] for i in self.cursor.fetchall()]                                               # all tables
    self.connection.commit()
    # check if default documents exist and create
    if 'docTypes' not in tables or resetDataHierarchy:
      if 'docTypes' in tables:
        logging.info('Remove old docTypes')
        self.cursor.execute('DROP TABLE docTypes')
      self.createSQLTable('docTypes',  DOC_TYPES,    'docType')
      command = f"INSERT INTO docTypes ({', '.join(DOC_TYPES)}) VALUES ({', '.join(['?']*len(DOC_TYPES))});"
      self.cursor.executemany(command, defaultDocTypes)
      # docTypeSchema table (see below)
      # - define the key of the metadata table, units, icons, ...
      if 'docTypeSchema' in tables:
        logging.info('Remove old docTypeSchema')
        self.cursor.execute('DROP TABLE docTypeSchema')
      self.createSQLTable('docTypeSchema', DOC_TYPE_SCHEMA,  'docType, class, idx')
      command = f"INSERT INTO docTypeSchema ({', '.join(DOC_TYPE_SCHEMA)}) VALUES ({', '.join(['?']*len(DOC_TYPE_SCHEMA))});"
      self.cursor.executemany(command, defaultSchema)
      # definitions of all the keys (those from the docTypeSchema and those of the properties table)
      self.createSQLTable('definitions',     ['key','long','PURL'],                       'key')
      command =  'INSERT OR REPLACE INTO definitions VALUES (?, ?, ?);'
      self.cursor.executemany(command, defaultDefinitions)
      self.connection.commit()
    return


  def dataHierarchyChangeView(self, docType:str, columns:list[str]) -> None:
    """ Set different view of docType in data hierarchy

    Args:
      docType (str): docType
      columns (list): list of columns
    """
    self.cursor.execute(f"UPDATE docTypes SET view='{','.join(columns)}' WHERE docType = '{docType}'")
    self.connection.commit()
    return


  def createSQLTable(self, name:str, columns:list[str], primary:str, colTypes:Optional[list[Any]]=None) -> list[str]:
    """
    Create a table in the sqlite system

    Args:
      name (str): name of table
      columns (list): list of column names
      primary (str): primary keys as comma-separated
      colTypes (list): optional list of data-types of the columns
    """
    if colTypes is None:
      colTypes = ['TEXT']*len(columns)
    colText = ', '.join(f'{i} {j}' for i,j in zip(columns, colTypes))
    self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} ({colText}, PRIMARY KEY ({primary}))")
    self.cursor.execute(f"SELECT * FROM {name}")
    columnNames = list(map(lambda x: x[0], self.cursor.description))
    if columnNames != columns:
      logging.error('Difference in sqlite table: %s', name)
      logging.error(columnNames)
      logging.error(columns)
      raise ValueError(f'SQLite table difference: {name}')
    return columnNames


  def dataHierarchy(self, docType:str, column:str, group:str='') -> list[Any]:
    """
    get data hierarchy information, old name 'ontology', from database

    Args:
      docType (str): document typ
      column (str): column name as in meta, title, shortcut, ...
      group (str): group of metadata rows; if group not given: return all
    Returns:
      list: information inquired
    """
    ### return column information
    if not docType:                                                                           #if all docTypes
      column = f', {column}' if column else ''
      self.cursor.execute(f"SELECT docType {column} FROM docTypes")
      results = self.cursor.fetchall()
      return [i[0] for i in results] if column=='' else results
    ### if metadata = docTypeSchema of data
    if column == 'meta':
      self.connection.row_factory = sqlite3.Row                                                  #default None
      cursor = self.connection.cursor()
      if group:
        cursor.execute(f"SELECT * FROM docTypeSchema WHERE docType == '{docType}' and class == '{group}'")
      else:
        cursor.execute(f"SELECT * FROM docTypeSchema WHERE docType == '{docType}'")
      return [dict(i) for i in cursor.fetchall()]
    if column == 'metaColumns':
      self.cursor.execute(f"SELECT DISTINCT class FROM docTypeSchema WHERE docType == '{docType}'")
      return [i[0] for i in self.cursor.fetchall()]
    # if specific docType
    self.cursor.execute(f"SELECT {column} FROM docTypes WHERE docType == '{docType}'")
    result = self.cursor.fetchone()
    if result is None:
      return []
    if column=='meta':
      return json.loads(result[0])
    elif column=='view':
      return result[0].split(',')
    return result


  def exit(self) -> None:
    """
    Shutting down things
    """
    self.cursor.close()
    del self.cursor
    self.connection.close()
    del self.connection
    return


  def getDoc(self, docID:str, noError:bool=False) -> dict[str,Any]:
    """
    Wrapper for get from database function

    Args:
        docID (dict): document id
        noError (bool): False=report errors as they occur; True=do not report on errors

    Returns:
        dict: json representation of document
    """
    self.connection.row_factory = sqlite3.Row                                                    #default None
    cursor = self.connection.cursor()
    cursor.execute(f"SELECT * FROM main WHERE id == '{docID}'")
    res = cursor.fetchone()
    if res is None:
      if not noError:
        logging.error('sqlite: could not get docID: %s | %s', docID, tracebackString(True, docID))
      return {}
    doc = dict(res)
    self.cursor.execute(f"SELECT tag FROM tags WHERE id == '{docID}'")
    doc['tags'] = [i[0] for i in self.cursor.fetchall()]
    self.cursor.execute(f"SELECT qrCode FROM qrCodes WHERE id == '{docID}'")
    doc['qrCodes'] = [i[0] for i in self.cursor.fetchall()]
    for key in ['image', 'content', 'shasum', 'client', 'qrCodes']:
      if len(doc[key])==0 or doc[key]==['']:
        del doc[key]
    doc['type']= doc['type'].split('/')
    doc['gui'] = [i=='T' for i in doc['gui']]
    doc['branch'] = []
    # data ends with 'id' 'stack', 'child', 'path', 'show', 'dateModified'
    self.cursor.execute(f"SELECT * FROM branches WHERE id == '{docID}'")
    for dataI in self.cursor.fetchall():
      doc['branch'].append({'stack': dataI[2].split('/')[:-1],
                            'child': dataI[3],
                            'path':  None if dataI[4] == '*' else dataI[4],
                            'show':   [i=='T' for i in dataI[5]]})
    cmd = 'SELECT properties.key, properties.value, properties.unit, definitions.long, definitions.PURL, ' \
          'docTypeSchema.unit FROM properties LEFT JOIN definitions USING(key) '\
          "LEFT JOIN docTypeSchema ON properties.key = (docTypeSchema.class || '.' || docTypeSchema.name) "\
          f"WHERE properties.id == '{docID}'"
    self.cursor.execute(cmd)
    res = self.cursor.fetchall()
    metadataFlat:dict[str, tuple[str,str,str,str]]  = {i[0]:(    i[1],                                  #value
                ('' if i[2] is None else i[2]) or ('' if i[5] is None else i[5]),#unit(priority:property.unit)
                ('' if i[3] is None else i[3]),                                                          #long
                ('' if i[4] is None else i[4])                                                           #PURL
                ) for i in res}
    doc |= hierarchy(metadataFlat)
    return doc


  def saveDoc(self, doc:dict[str,Any]) -> dict[str,Any]:
    """
    Save to database
    - not helpful to convert _id to int since sqlite does not digest such long integer
      doc['id']  = int(doc['id'][2:], 16)
    - **metaUser, metaVendor and branch as dict, everything else flattened**
    - Example{
        name: PASTAs Example Project
        type: ['measurement', 'image']
        type: ['-']
        tags: ['_3']
        comment: Can be used as reference or deleted
        user: sb-0bacab30726e181fe1e34d82e59a8ce9
        branch: {'stack': [], 'child': 0, 'path': 'PastasExampleProject', 'show': [True], 'op': 'u'}
        id: x-3cb1932eb3c4440cb5ca22cf57a6083f
        externalId:
        dateCreated: 2025-05-18T22:19:57.051393
        dateModified: 2025-05-18T22:19:57.051415
        gui: [True, True]
        content:# Put sample in instrument
        shasum: 74fd0aea706e0c51d1fd92e9c8e731f83cf92009
        qrCodes: ['13214124', '99698708']
        image: data:image/jpg;base64...

        .objective: Test if everything is working as intended.
        .status: active
        .chemistry: A2B2C3
        geometry.height: 4
        geometry.width: 2
        .workflow/procedure: w-e1ae41142b38416bb9332b3e01bf10a5

        metaVendor: {'fileExtension': 'md'}
        metaUser: {'Sample frequency [Hz]': 2.5, 'Maximum y-data [m]': 0.9996}
        metaUser: [{'key': 'imageWidth', 'value': 800, 'unit': 'mm', 'label': 'Largeur de l`image', 'PURL': '...'},
                   {'key': 'imageHeight', 'value': '600+/- 3', 'unit': 'mm', 'label': 'Höhe des Bildes', 'PURL': '...'}]

    Discussion on branch['path']:
    - full path (from basePath) allows to easily create a view of all paths and search through them
      during each scan, which happens rather often
    - just the incremental path (file-name, folder-name) allows to easily change that if the user wants
      and not change all the children paths, too. However, the renaming of the folder is likely occurring
      less often.

    Args:
        doc (dict): document to save

    Returns:
        dict: json representation of submitted document
    """
    # print('\nsave\n'+'\n'.join([f'{k}: {v}' for k,v in doc.items() if k not in ['image']]))
    # for k,v in doc.items():
    #   if isinstance(v, dict) and k not in ['metaUser','metaVendor','branch']:
    #     print('ERROR',k,v)
    # end initial testing
    docOrg = copy.deepcopy(doc)
    # save into branch table
    self.cursor.execute(f"INSERT INTO branches VALUES ({', '.join(['?']*6)})",
                        [doc['id'],
                         0,
                         '/'.join(doc['branch']['stack']+[doc['id']]),
                         str(doc['branch']['child']),
                         '*' if doc['branch']['path'] is None else doc['branch']['path'],
                         ''.join(['T' if j else 'F' for j in doc['branch']['show']])])
    del doc['branch']
    # save into tags table
    self.cursor.executemany('INSERT INTO tags VALUES (?, ?);', zip([doc['id']]*len(doc['tags']), doc['tags']))
    del doc['tags']
    if 'qrCodes' in doc:
      cmd = 'INSERT INTO qrCodes VALUES (?, ?);'
      self.cursor.executemany(cmd, zip([doc['id']]*len(doc['qrCodes']), doc['qrCodes']))
      del doc['qrCodes']
    if 'content' in doc and len(doc['content'])>200:
      doc['content'] = doc['content'][:200]
    doc['type'] = '/'.join(doc['type'])
    doc['gui']  = ''.join(['T' if i else 'F' for i in doc['gui']])
    doc['client'] = tracebackString(False, 'save:'+doc['id'])
    docList = [doc[x] if x in doc else doc.get(f'.{x}','') for x in MAIN_ORDER]
    self.cursor.execute(f"INSERT INTO main VALUES ({', '.join(['?']*len(docList))})", docList)
    doc = {k:v for k,v in doc.items() if (k not in MAIN_ORDER and k[1:] not in MAIN_ORDER) or k == 'id'}

    def insertMetadata(data:dict[str,Any], parentKeys:str) -> None:
      parentKeys = f'{parentKeys}.' if parentKeys else ''
      cmd    = 'INSERT OR REPLACE INTO properties VALUES (?, ?, ?, ?);'
      cmdDef = 'INSERT OR REPLACE INTO definitions VALUES (?, ?, ?);'
      for key,value in data.items():
        key = str(key) if isinstance(key, int) else key
        if isinstance(value, dict):
          insertMetadata(value, f'{parentKeys}{key}')
        elif key.endswith(']') and ('[') in key:
          unit   = re.findall(r'\[\S+\]', key)[-1][1:-1]
          label  = key[:-len(unit)-2].strip()
          key    = camelCase(label)
          key    = key[0].lower()+key[1:]
          self.cursor.execute(cmd, [doc['id'], parentKeys+key, str(value), unit])
          self.cursor.execute(cmdDef, [parentKeys+key, label, ''])
        elif isinstance(value, list) and isinstance(value[0], dict) and value[0].keys() >= {'key', 'value', 'unit'}:
          self.cursor.executemany(cmd, zip([doc['id']]*len(value),      [parentKeys+key+'.'+i['key'] for i in value],
                                            [i['value'] for i in value], [i['unit'] for i in value]  ))
          self.cursor.executemany(cmdDef, zip([parentKeys+key+'.'+i['key'] for i in value],
                                            [i['label'] for i in value], [i['PURL'] for i in value]  ))
        elif isinstance(value, tuple) and len(value)==4:
          self.cursor.execute(cmd,    [doc['id'], parentKeys+key, value[0], value[1]])
          self.cursor.execute(cmdDef, [parentKeys+key, value[2], value[3]])
        elif str(value)!='':
          try:
            self.cursor.execute(cmd, [doc['id'], parentKeys+key, str(value), ''])
          except Exception:
            logging.error('SQL command %s did not succeed %s', cmd, [doc['id'], parentKeys+key, str(value), ''])
      self.connection.commit()
      return
    # properties
    metaDoc = {k:v for k,v in doc.items() if k not in MAIN_ORDER}
    insertMetadata(metaDoc, '')
    # save changes
    self.connection.commit()
    branch = copy.deepcopy(docOrg['branch'])
    del branch['op']
    docOrg['branch'] = [branch]
    return docOrg


  def updateDoc(self, dataNew:dict[str,Any], docID:str) -> dict[str,Any]:
    """
    Update document by
    - saving changes to oldDoc (revision document)
    - updating new-document concurrently
    - create a docID for oldDoc

    Key:Value
    - if value is None: do not change it;
    - if key does not exist: change it to empty, aka remove it

    Args:
        dataNew (dict): item to update
        docID (string):  id of document to change

    Returns:
        dict: json representation of updated document
    """
    if set(dataNew.keys()) == {'type','image'}:        #if only type and image in update = change of extractor
      self.cursor.execute(f"UPDATE main SET type='{'/'.join(dataNew['type'])}', image='{dataNew['image']}' WHERE id = '{docID}'")
      self.connection.commit()
      return {'id':docID}
    dataNew['client'] = tracebackString(False, f'updateDoc:{docID}')
    if 'edit' in dataNew:                                                                           #if delete
      dataNew = {'id':dataNew['id'], 'branch':dataNew['branch'], 'user':dataNew['user'], 'externalId':dataNew['externalId'], 'name':''}
    changesDict:dict[str,Any]         = {}
    self.connection.row_factory = sqlite3.Row                                                    #default None
    cursor = self.connection.cursor()

    # tags and qrCodes
    tagsNew= set(dataNew.pop('tags'))
    self.cursor.execute(f"SELECT tag FROM tags WHERE id == '{docID}'")
    tagsOld= {i[0] for i in self.cursor.fetchall()}
    if tagsOld.difference(tagsNew):
      cmd = f"DELETE FROM tags WHERE id == '{docID}' and tag == ?"
      self.cursor.executemany(cmd, [(i,) for i in tagsOld.difference(tagsNew)])
      changesDict['tags'] = ','.join(tagsOld)
    if tagsNew.difference(tagsOld):
      change = tagsNew.difference(tagsOld)
      self.cursor.executemany('INSERT INTO tags VALUES (?, ?);', zip([docID]*len(change), change))
      changesDict['tags'] = ','.join(tagsOld)
    qrCodesNew= set(dataNew.pop('qrCodes', []))
    self.cursor.execute(f"SELECT qrCode FROM qrCodes WHERE id == '{docID}'")
    qrCodesOld= {i[0] for i in self.cursor.fetchall()}
    if qrCodesOld.difference(qrCodesNew):
      cmd = f"DELETE FROM qrCodes WHERE id == '{docID}' and qrCode == ?"
      self.cursor.executemany(cmd, [(i,) for i in qrCodesOld.difference(qrCodesNew)])
      changesDict['qrCodes'] = ','.join(qrCodesOld)
    if qrCodesNew.difference(qrCodesOld):
      change = qrCodesNew.difference(qrCodesOld)
      self.cursor.executemany('INSERT INTO qrCodes VALUES (?, ?);', zip([docID]*len(change), change))
      changesDict['qrCodes'] = ','.join(qrCodesOld)
    # separate into main and properties
    mainNew    = {key: dataNew.pop(key) for key in MAIN_ORDER if key in dataNew}
    branchNew  = dataNew.pop('branch',{})
    # read branches and identify changes
    cursor.execute(f"SELECT stack, child, path, show FROM branches WHERE id == '{docID}'")
    branchOld = [dict(i) for i in cursor.fetchall()]
    branchOld[0]['show'] = [i=='T' for i in branchOld[0]['show']]
    branchOld[0]['stack'] = branchOld[0]['stack'].split('/')[:-1]
    # print(f'do something with branch: \nnew {branchNew} \nold: {branchOld}')
    if branchNew:
      op      = branchNew.pop('op')                                                                 #operation
      oldPath = branchNew.pop('oldPath',None)
      if not branchNew['path']:
        branchNew['path'] = branchOld[0]['path']
      if branchNew not in branchOld:              #only do things if the newBranch is not already in oldBranch
        changesDict['branch'] = branchOld.copy()
        idx = None
        for branch in branchOld:                #check if the path is already exist, then it is only an update
          if op=='c' and branch['path']==branchNew['path']:
            op='u'
        if op=='c':                                                                            #create, append
          if isinstance(branchNew['stack'], str):
            raise ValueError('Should be list')
          branchNew['show'] = self.createShowFromStack(branchNew['stack'])
          self.cursor.execute(f"INSERT INTO branches VALUES ({', '.join(['?']*6)})",
                        [docID,
                         len(branchOld),
                         '/'.join(branchNew['stack']+[docID]),
                         branchNew['child'],
                         '*' if branchNew['path'] is None else branchNew['path'],
                         ''.join(['T' if j else 'F' for j in branchNew['show']])])
        elif op=='u':                                                                                  #update
          if oldPath is not None:                                                   # search by using old path
            for branch in branchOld:
              if branch['path'].startswith(oldPath):
                if   os.path.basename(branch['path']) == mainNew['name'] and \
                     os.path.basename(str(branchNew['path']))!='':
                  mainNew['name'] = os.path.basename(str(branchNew['path']))
                branch['path'] = branch['path'].replace(oldPath ,branchNew['path'])
                branch['stack']= branchNew['stack']
                branch['show'] = self.createShowFromStack(branchNew['stack'], branch['show'][-1])
                break
          else:
            idx = 0
            branchOld[idx] = branchNew                                        #change branch 0 aka the default
          if idx is None:                                          # create new branch: should not happen here
            raise ValueError(f'sqlite.2: idx unset: {mainNew["id"]} {mainNew["name"]}')
          self.cursor.execute(f"UPDATE branches SET stack='{'/'.join(branchOld[idx]['stack']+[docID])}', "
                              f"path='{branchOld[idx]['path']}', child='{branchOld[idx]['child']}', "
                              f"show='{''.join(['T' if j else 'F' for j in branchOld[idx]['show']])}' "
                              f"WHERE id = '{docID}' and idx = {idx}")
        elif op=='d':                                                                                  #delete
          branchOld = [branch for branch in branchOld if branch['path']!=branchNew['path']]
        else:
          raise ValueError(f'sqlite.1: unknown branch op: {mainNew["id"]} {mainNew["name"]}: {branchNew} of doc {dataNew}')

    # read properties and identify changes
    self.cursor.execute(f"SELECT key, value FROM properties WHERE id == '{docID}'")
    dataOld = {i[0]:i[1] for i in self.cursor.fetchall()}
    for key,value in dataNew.items():
      if isinstance(value, dict):
        for subKey, subValue in value.items():
          longKey = f'{key}.{subKey}'
          if isinstance(subValue, tuple):
            subValue = subValue[0]
          if longKey in dataOld and subValue!=dataOld[longKey]:
            self.cursor.execute(f"UPDATE properties SET value='{subValue}' WHERE id = '{docID}' and key = '{longKey}'")
            changesDict[longKey] = dataOld[longKey]
          elif longKey not in dataOld:
            cmd = 'INSERT INTO properties VALUES (?, ?, ?, ?);'
            self.cursor.execute(cmd ,[docID, longKey, subValue, ''])
          if longKey in dataOld:
            del dataOld[longKey]
      elif isinstance(value, (str,int,float)) and '.' in key:
        if key in dataOld and value!=dataOld[key]:
          self.cursor.execute(f"UPDATE properties SET value='{value}' WHERE id = '{docID}' and key = '{key}'")
          changesDict[key] = dataOld[key]
        elif key not in dataOld:
          cmd = 'INSERT INTO properties VALUES (?, ?, ?, ?);'
          self.cursor.execute(cmd ,[docID, key, value, ''])
      elif isinstance(value, tuple) and len(value)==4:
        if key in dataOld and value[0]!=dataOld[key]:
          self.cursor.execute(f"UPDATE properties SET value='{value[0]}' WHERE id = '{docID}' and key = '{key}'")
          changesDict[key] = dataOld[key]
        elif key not in dataOld:
          cmd = 'INSERT INTO properties VALUES (?, ?, ?, ?);'
          self.cursor.execute(cmd ,[docID, key, value[0], value[1]])
      else:
        logging.error('Property is not a dict, ERROR %s %s %s',key, value, type(value))
    if set(dataOld.keys()).difference(dataNew.keys()):
      cmd = f"DELETE FROM properties WHERE id == '{docID}' and key == ?"
      properties = [(i,) for i in set(dataOld.keys()).difference(dataNew.keys())]
      self.cursor.executemany(cmd, properties)
      changesDict |= dataOld
    # read main and identify if something changed
    cursor.execute(f"SELECT * FROM main WHERE id == '{docID}'")
    mainOld = dict(cursor.fetchone())
    mainOld['type']= mainOld['type'].split('/')
    changesDB: dict[str,dict[str,str]] = {'main': {}}
    for key in ('name','user','type','dateModified','dateSync','client','image','content','comment'):
      if key in mainNew and mainOld[key]!=mainNew[key]:
        changesDB['main'][key] = '/'.join(mainNew[key]) if key=='type' else mainNew[key].translate(SQLiteTranslation)
        changesDict[key] = mainOld[key]
    # save change content in database: main and changes are updated
    if set(changesDict.keys()).difference(('dateModified','client','user')):
      changeString = ', '.join([f"{k}='{v}'" for k,v in changesDB['main'].items()])
      self.cursor.execute(f"UPDATE main SET {changeString} WHERE id = '{docID}'")
      if 'name' not in changesDict or changesDict['name']!='new item':#don't save initial change from new item
        self.cursor.execute('INSERT INTO changes VALUES (?,?,?)', [docID, datetime.now().isoformat(), json.dumps(changesDict)])
      self.connection.commit()
    return mainOld | mainNew | {'branch':branchOld, '__version__':'short'}


  def updateBranch(self, docID:str, branch:int, child:int, stack:list[str]=[],
                   path:Optional[str]='', **kwargs:str) -> tuple[Optional[str], Optional[str]]:
    """
    Update document by updating the branch

    Args:
      docID (string):  id of document to change
      branch (int):  index of branch to change. If -1, then append to end. If -2, then delete
      child (int):  new number of child
      stack (list):  new list of ids
      path (str): new path; None is acceptable
      kwargs (str): pathOld and stackOld can be used to identify branch to be updated

    Returns:
      str, str: old path, new path
    """
    #convert into db style
    path = '*' if path is None else path
    if branch == -2:                                                                         #delete this path
      self.cursor.execute(f"DELETE FROM branches WHERE id == '{docID}' and path == '{path}'")
      self.connection.commit()
      # test if there is a branch remaining, if not delete document
      self.cursor.execute(f'SELECT id FROM branches WHERE id == "{docID}"')
      res = self.cursor.fetchall()
      if len(res)==0:
        self.remove(docID)
      return (path, None)

    if branch == -1:                                                                      #append a new branch
      self.cursor.execute(f"SELECT idx FROM branches WHERE id == '{docID}'")
      idxOld = [i[0] for i in self.cursor.fetchall()]
      idxNew  = min(set(range(max(idxOld)+2)).difference(idxOld))
      show  = self.createShowFromStack(stack)
      self.cursor.execute(f"INSERT INTO branches VALUES ({', '.join(['?']*6)})",
                  [docID, idxNew, '/'.join(stack+[docID]), str(child), path, show])
      self.connection.commit()
      return (None, None if path=='*' else path)

    # modify existing branch
    if 'pathOld' in kwargs:
      pathOld = kwargs['pathOld']
      cmd = f"SELECT path, stack, show FROM branches WHERE path == '{pathOld}'"
    elif 'stackOld' in kwargs:
      stackOld = '/'.join(kwargs['stackOld'])
      cmd = f"SELECT path, stack, show FROM branches WHERE stack == '{stackOld}'"
    else:
      cmd = f"SELECT path, stack, show FROM branches WHERE id == '{docID}' and idx == {branch}"
    self.cursor.execute(cmd)
    reply = self.cursor.fetchone()
    if reply is None:
      raise ValueError(f"FAILED AT: {cmd}")
    pathOld, stackOld, showOld = reply
    stack = stack or stackOld.split('/')[:-1]                                       # stack without current id
    if pathOld=='*':
      path = '*'
    elif path=='':
      self.cursor.execute(f"SELECT type, name FROM main WHERE id == '{docID}'")
      docType, name = self.cursor.fetchall()[0]
      if docType.startswith('x'):
        name = createDirName(name,docType,child)
      path = ((Path(pathOld).parent)/name).as_posix()
    show  = self.createShowFromStack(stack, showOld[-1])
    cmd = f"UPDATE branches SET stack='{'/'.join(stack+[docID])}', child={child}, path='{path}', show='{show}' "\
          f"WHERE path = '{pathOld}' and stack = '{stackOld}'"
    self.cursor.execute(cmd)
    self.connection.commit()
    # move content: folder and data and write .json to disk
    if pathOld!='*' and ':/' not in pathOld and path!='*' and path is not None:
      if not (self.basePath/pathOld).exists() and (self.basePath/path).exists():
        logging.debug('sqlite:updateBranch: dont move since already good')
      else:
        shutil.move(self.basePath/pathOld, self.basePath/path)
    if docID[0]=='x' and path is not None:
      with open(self.basePath/path/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(self.getDoc(docID)))
      self.updateChildrenOfParentsChanges(pathOld, path,  stackOld,'/'.join(stack+[docID]))
    return (None if pathOld=='*' else pathOld, None if path=='*' else path)


  def updateChildrenOfParentsChanges(self, pathOld:str, pathNew:str, stackOld:str, stackNew:str) -> None:
    """
    update children's paths

    Args:
      pathOld (str): old path of parent
      pathNew (str): new path of parent
      stackOld (str): old stack of parent
      stackNew (str): new stack of parent
    """
    cmd = f"SELECT path, stack, show, id, idx FROM branches WHERE stack LIKE '{stackOld}/%'"
    self.cursor.execute(cmd)
    children = self.cursor.fetchall()
    updatedInfo = []
    for (pathIOld, stackIOld, showIOld, docID, idx) in children:
      pathINew  = pathNew+pathIOld[len(pathOld):] if pathIOld!='*' and pathIOld.startswith(pathOld) else pathIOld
      stackINew = stackNew+stackIOld[len(stackOld):]                           if stackNew else stackIOld
      showINew  = self.createShowFromStack(stackIOld.split('/'), showIOld[-1]) if stackNew else showIOld
      updatedInfo.append((pathINew, stackINew, showINew, docID, idx))
    cmd = 'UPDATE branches SET path=?, stack=?, show=? WHERE id == ? and idx == ?'
    self.cursor.executemany(cmd, updatedInfo)
    self.connection.commit()
    return


  def createShowFromStack(self, stack:list[str], currentShow:str='T') -> str:
    """
    For branches: create show entry in the branches by using the stack
    - should be 1 longer than stack
    - check parents if hidden, then this child is hidden too

    Args:
      stack (list): list of ancestor docIDs '/' separated
      currentShow (str): current show-indicator of this item

    Returns:
      str: string of show = list of bool
    """
    show = len(stack)*['T'] + [currentShow]
    for idx, docID in enumerate(stack):
      self.cursor.execute(f"SELECT show FROM branches WHERE id == '{docID}'")
      if self.cursor.fetchone()[0][-1] == 'F':
        show[idx] = 'F'
    return ''.join(show)

  def remove(self, docID:str, stack:str='') -> dict[str,Any]:
    """
    remove doc from database: temporary for development and testing

    Args:
      docID (string): id of document to remove
      stack (str): stack of branch to delete, if there are multiple branches

    Returns:
      dict: document that was removed
    """
    doc = self.getDoc(docID)
    if len(doc['branch'])>1 and stack:                                                 #only remove one branch
      stack = stack[:-1] if stack.endswith('/') else stack
      self.cursor.execute(f"DELETE FROM branches WHERE id == '{docID}' and stack LIKE '{stack}%'")
    else:                                                                                   #remove everything
      doc.pop('image','')
      doc.pop('content','')
      self.cursor.execute(f"DELETE FROM main WHERE id == '{docID}'")
      self.cursor.execute(f"DELETE FROM branches WHERE id == '{docID}'")
      self.cursor.execute(f"DELETE FROM properties WHERE id == '{docID}'")
      self.cursor.execute(f"DELETE FROM tags WHERE id == '{docID}'")
      self.cursor.execute(f"DELETE FROM qrCodes WHERE id == '{docID}'")
      self.cursor.execute(f"DELETE FROM attachments WHERE id == '{docID}'")
      self.cursor.execute('INSERT INTO changes VALUES (?,?,?)', [docID, datetime.now().isoformat(), json.dumps(doc)])
    self.connection.commit()
    return doc


  def initAttachment(self, docID:str, name:str, docType:str) -> None:
    """ initialize an attachment by defining its name and type

    Args:
      docID (str): document / instrument on which attachments are installed
      name (str): description of attachment location
      docType (str): document type what can be attached. Use empty string if these are remarks, i.e. no items are attached
    """
    cmd = 'INSERT OR REPLACE INTO attachments VALUES (?,?,?,?,?,?)'
    self.cursor.execute(cmd, [docID, name, '', docType, '', ''])
    self.connection.commit()
    return


  def addAttachment(self, docID:str, name:str, content:dict[str,Any]) -> None:
    """
    Update document by adding attachment (no new revision)

    Args:
        docID (string):  id of document to change
        name (string): attachment name to add to
        content (dict): dictionary of content to be added (should include user,date,docID,remark)

    """
    cmd = 'INSERT INTO attachments VALUES (?,?,?,?,?,?)'
    self.cursor.execute(cmd, [docID, name, content['date'], content['docID'], content['remark'], content['user']])
    self.connection.commit()
    return


  def getView(self, thePath:str, startKey:Optional[str]=None, preciseKey:Optional[str]=None) -> pd.DataFrame:
    """
    Wrapper for getting view function

    Args:
        thePath (string): path to view; e.g. 'viewDocType/x0'
        startKey (string): / separated; if given, use to filter output, everything that starts with this key
        preciseKey (string): if given, use to filter output. Match precisely

    Returns:
        df: data-frame with human-readable column names
    """
    if (startKey is not None and ' ' in startKey) or (preciseKey is not None and ' ' in preciseKey):
      raise ValueError(f'key cannot have a space inside |{startKey}|{preciseKey}|')#TODO: remove this safeguard in 2026
    allFlag = False
    if thePath.endswith('All'):
      thePath = thePath.removesuffix('All')
      allFlag = True
    viewType, docType = thePath.split('/', 1)
    if viewType=='viewDocType':
      viewColumns = self.dataHierarchy(docType, 'view')
      viewColumns = viewColumns+['id'] if viewColumns and viewColumns != [''] else ['name','tags','comment','id']
      textSelect = ', '.join([f'main.{i}' for i in viewColumns if i in MAIN_ORDER or i[1:] in MAIN_ORDER])
      cmd = f"SELECT {textSelect} FROM main INNER JOIN branches USING(id) WHERE main.type LIKE '{docType}%'"
      if not allFlag:
        cmd += r" and NOT branches.show LIKE '%F%'"
      if startKey:
        cmd += f" and branches.stack LIKE '{startKey}%'"
      df      = pd.read_sql_query(cmd, self.connection, index_col='id', ).fillna('')
      #clean main df
      df      = df[~df.index.duplicated(keep='first')]
      if 'image' in viewColumns:
        df['image'] = df['image'].apply(lambda x: 'Y' if len(str(x)) > 1 else 'N')
      # add: tags, qrCodes, parameters
      if 'tags' in viewColumns:
        cmd = 'SELECT main.id, tags.tag FROM main INNER JOIN tags USING(id) INNER JOIN branches USING(id) '\
              f"WHERE main.type LIKE '{docType}%'"
        if not allFlag:
          cmd += r" and NOT branches.show LIKE '%F%'"
        if startKey:
          cmd += f" and branches.stack LIKE '{startKey}%'"
        dfTags = pd.read_sql_query(cmd, self.connection, index_col='id').fillna('')
        dfTags = dfTags.groupby(['id'])['tag'].apply(lambda x: ', '.join(set(x))).reset_index().set_index('id')
        dfTags.rename(columns={'tag':'tags'}, inplace=True)
        df = df.join(dfTags)
      if 'qrCodes' in viewColumns:
        cmd = 'SELECT main.id, qrCodes.qrCode FROM main INNER JOIN qrCodes USING(id) INNER JOIN branches '\
              f"USING(id) WHERE main.type LIKE '{docType}%'"
        if not allFlag:
          cmd += r" and NOT branches.show LIKE '%F%'"
        if startKey:
          cmd += f" and branches.stack LIKE '{startKey}%'"
        dfQrCodes = pd.read_sql_query(cmd, self.connection, index_col='id').fillna('')
        dfQrCodes = dfQrCodes.groupby(['id'])['qrCode'].apply(', '.join).reset_index().set_index('id')
        dfQrCodes.rename(columns={'qrCode':'qrCodes'}, inplace=True)
        df = df.join(dfQrCodes)
      if metadataKeys:= [f'properties.key == "{i}"' for i in viewColumns if i not in MAIN_ORDER+['tags']]:
        cmd = 'SELECT main.id, properties.key, properties.value FROM main INNER JOIN properties USING(id) '\
              f"INNER JOIN branches USING(id) WHERE main.type LIKE '{docType}%' AND ({' OR '.join(metadataKeys)})"
        if not allFlag:
          cmd += r" and NOT branches.show LIKE '%F%'"
        if startKey:
          cmd += f" and branches.stack LIKE '{startKey}%'"
        dfParams = pd.read_sql_query(cmd, self.connection).fillna('')
        dfParams = dfParams.drop_duplicates(subset=['key', 'id'], keep='first').set_index('id')# drop duplicates if there are multiple branches
        dfParams = dfParams.pivot(columns='key', values='value')                         # Pivot the DataFrame
        #dfParams.columns.name = None                               # Flatten the columns; seems not necessary
        df = df.join(dfParams)
      # final sorting of columns
      columnOrder = [i[1:] if i.startswith('.') and i[1:] in MAIN_ORDER else i for i in viewColumns]
      df = df.reset_index().reindex(columnOrder, axis=1)
      df = df.rename(columns={i:i[1:] for i in columnOrder if i.startswith('.') })
      df = df.astype('str').fillna('')
      return df
    elif thePath=='viewHierarchy/viewHierarchy':
      cmd = 'SELECT branches.id, branches.stack, branches.child, main.type, main.name, main.gui, branches.idx '\
            f"FROM branches INNER JOIN main USING(id) WHERE branches.stack LIKE '{startKey}%'"
      if not allFlag:
        cmd += r" and NOT branches.show LIKE '%F%'"
      cmd += ' ORDER BY branches.stack'
      self.cursor.execute(cmd)
      results = self.cursor.fetchall()
      # value: [child, doc['type'], doc['name'], doc['gui'], branches.idx]
      results = [{'id':i[0], 'key':i[1],
                  'value':[i[2], i[3].split('/'), i[4], [j=='T' for j in i[5]], i[6]]} for i in results]
    elif thePath=='viewHierarchy/viewPaths':
      cmd = 'SELECT branches.id, branches.path, branches.stack, main.type, branches.child, main.shasum, branches.idx '\
            'FROM branches INNER JOIN main USING(id)'
      # JOIN and get type
      if startKey is not None:
        if startKey.endswith('/'):
          startKey = startKey.removesuffix('/')
        cmd += f" WHERE branches.path LIKE '{startKey}%'"
      elif preciseKey is not None:
        cmd += f" WHERE branches.path LIKE '{preciseKey}'"
      if not allFlag:
        if 'WHERE' in cmd:
          cmd += r" AND NOT branches.show LIKE '%F%'"
        else:
          cmd += r" WHERE NOT branches.show LIKE '%F%'"
      self.cursor.execute(cmd)
      results = self.cursor.fetchall()
      # value: [branch.stack, doc['-type'], branch.child, doc.shasum, idx]
      results = [{'id':i[0], 'key':i[1],
                  'value':[i[2], i[3].split('/')]+list(i[4:])} for i in results if i[1] is not None]
    elif viewType=='viewIdentify' and docType=='viewTags':
      return pd.read_sql_query('SELECT tags.tag, main.name, main.type, tags.id FROM tags INNER JOIN main USING(id)',
                               self.connection).fillna('')
    elif viewType=='viewIdentify':
      if docType=='viewQR':
        if startKey is None:
          cmd = 'SELECT qrCodes.id, qrCodes.qrCode, main.name FROM qrCodes INNER JOIN main USING(id)'
          if not allFlag:
            cmd += r" INNER JOIN branches USING(id) WHERE NOT branches.show LIKE '%F%'"
        else:
          raise ValueError('Not implemented sqlite l 599')
      elif docType=='viewSHAsum':
        if startKey is None:
          cmd = 'SELECT main.id, main.shasum, main.name FROM main'
          if not allFlag:
            cmd += r" INNER JOIN branches USING(id) WHERE NOT branches.show LIKE '%F%'"
        else:
          cmd = f"SELECT main.id, main.shasum, main.name FROM main INNER JOIN branches USING(id) WHERE shasum='{startKey}'"
          if not allFlag:
            cmd += r" and NOT branches.show LIKE '%F%'"
      else:
        raise ValueError('Invalid docType')
      self.cursor.execute(cmd)
      results = self.cursor.fetchall()
      results = [{'id':i[0], 'key':i[1].replace('/',' '), 'value':i[2]} for i in results if i[1] is not None]
    else:
      print('Not implemented view', thePath, startKey, preciseKey)
      raise ValueError('Not implemented')
    return results


  def getHierarchy(self, start:str, allItems:bool=False) -> tuple[Node,bool]:
    """
    get hierarchy tree for projects, ...

    Args:
      start (str): start of the hierarchy (most parent)
      allItems (bool):  true=show all items, false=only non-hidden

    Returns:
      Node: hierarchy in an anytree; children sorted by childNum (primary) and docID (secondary)
      bool: error occurred
    """
    path = 'viewHierarchy/viewHierarchyAll' if allItems else 'viewHierarchy/viewHierarchy'
    view = self.getView(path,    startKey=start)
    # create tree of folders: these are the only ones that have children
    dataTree = None
    nonFolders = []
    id2Node = {}
    error = False
    for item in view:
      docType = item['value'][1]
      if docType[0][0] != 'x':
        nonFolders.append(item)
        continue
      _id     = item['id']
      childNum, docType, name, gui, _ = item['value']
      if dataTree is None:
        dataTree = Node(id=_id, docType=docType, name=name, gui=gui, childNum=childNum)
        id2Node[_id] = dataTree
      else:
        parent = item['key'].split('/')[-2]
        if parent in id2Node:
          parentNode = id2Node[parent]
        else:
          parentNode, error = (dataTree, True)
          logging.error('There is an error in the hierarchy tree structure with parent %s missing', parent)
        subNode = Node(id=_id, parent=parentNode, docType=docType, name=name, gui=gui, childNum=childNum)
        id2Node[_id] = subNode
    # add non-folders into tree
    # print(len(nonFolders),'length: crop if too long')
    for item in nonFolders:
      _id     = item['id']
      childNum, docType, name, gui, _ = item['value']
      parentId = item['key'].split('/')[-2]
      if parentId in id2Node:
        parentNode = id2Node[parentId]
      else:
        outputString('print','error',f'repair branch table as parentID {parentId} is missing')
        parentNode, error = (dataTree,True)
      Node(id=_id, parent=parentNode, docType=docType, name=name, gui=gui, childNum=childNum)
    # sort children
    for parentNode in id2Node.values():
      children = parentNode.children
      childNums= [f'{i.childNum}{i.id}{idx}' for idx,i in enumerate(children)]
      parentNode.children = [x for _, x in sorted(zip(childNums, children))]
    return dataTree, error


  def hideShow(self, docID:str) -> None:
    """
    Toggle hide/show indicator of branch

    Args:
      docID (str): document id
    """
    def adoptShow(item:tuple[str,str,str,str]) -> tuple[str,str,str]:
      """ Adopt show string, internal mapping function

      Args:
        item (tuple): id, idx, stack, show

      Returns:
        tuple: show, id, idx
      """
      localDocID, idx, stack, show = item
      j = stack.split('/').index(docID)
      showL = list(show)
      showL[j] = 'T' if showL[j]=='F' else 'F'
      return (''.join(showL), localDocID, idx)
    cmd = f"SELECT id, idx, stack, show FROM branches WHERE stack LIKE '%{docID}%'"
    self.cursor.execute(cmd)
    changed = map(adoptShow, self.cursor.fetchall())
    cmd = 'UPDATE branches SET show=? WHERE id = ? and idx= ?'
    self.cursor.executemany(cmd, changed)
    self.connection.commit()
    return


  def setGUI(self, docID:str, guiState:list[bool]) -> None:
    """
    Set the gui state
    - 0: true=show details; false=hide details
    - 1: true=show children; false=hide children; only makes sense for folders: doctype = x1

    Args:
      docID (str): docID
      guiState (list): list of bool that show if document is shown
    """
    guiList = ''.join(['T' if i else 'F' for i in guiState])
    cmd = f"UPDATE main SET gui='{guiList}' WHERE id = '{docID}'"
    self.cursor.execute(cmd)
    self.connection.commit()
    return


  def checkDB(self, outputStyle:str='text', minimal:bool=False,
              repair:Union[None,Callable[[str],bool]]=None) -> str:
    """
    Check database for consistencies by iterating through all documents
    - only reporting, no repair
    - custom changes are possible with normal scan
    - no interaction with hard disk

    Args:
        outputStyle (str): output using a given style: see outputString
        minimal (bool): true=only show warnings and errors; else=also show information
        repair (function): auto-repair after asking user

    Returns:
        str: output
    """
    reply = ''
    if outputStyle=='html':
      reply += '<div align="right">'
    if not minimal:
      reply+= outputString(outputStyle,'h2','LEGEND')
      reply+= outputString(outputStyle,'perfect','Green: perfect and as intended')
      reply+= outputString(outputStyle,'ok',
                               'Blue: ok, can happen: empty files for testing, strange path for measurements')
      reply+= outputString(outputStyle,'h2','List all database entries')
    if outputStyle=='html':
      reply += '</div>'
      reply+= outputString(outputStyle,'h2','List all database entries')
    lostAndFoundProjId   = ''
    lostAndFoundProjPath = Path()
    if repair is not None:
      dfProjects = self.getView('viewDocType/x0')
      idProjects = dfProjects[dfProjects['name']=='Lost and Found']['id'].values
      if len(idProjects)==0:
        print('**Warning: manually create "LostAndFound" project to allow full repair')
      else:
        lostAndFoundProjId   = idProjects[0]
        lostAndFoundProjPath = Path('LostAndFound')                                             #by definition
    if not lostAndFoundProjId and repair is not None:
      errorStr = outputString(outputStyle,'error','No Lost and Found project found. Some repair impossible. '\
                                          'Repair: exit repair mode and manually create LostAndFound project.')
      if repair is None:
        reply+= errorStr
      elif repair(errorStr):
        return 'Repair aborted: no Lost and Found project found. Exit repair mode and create it manually.'
    # tests
    self.cursor.execute('SELECT main.id, main.name FROM main WHERE id NOT IN (SELECT id FROM branches)')
    if res:= self.cursor.fetchall():
      errorStr = outputString(outputStyle,'error', f'Items with no branch: {", ".join(str(i) for i in res)}')
      if repair is None:
        reply+= errorStr
      elif repair(errorStr):
        for docID, name in res:
          self.cursor.execute(f"INSERT INTO branches VALUES ({', '.join(['?']*6)})",
            [docID, 0, f'{lostAndFoundProjId}/{docID}', 9999,
            (lostAndFoundProjPath/createDirName(name, 'x0', 0)).as_posix() if docID.startswith('x-') else '*',
            'TT'])
        self.connection.commit()

    cmd = 'SELECT id, main.type, branches.stack, branches.path, branches.child, branches.show, main.name '\
          'FROM branches INNER JOIN main USING(id)'
    self.cursor.execute(cmd)
    res = self.cursor.fetchall()
    reply += outputString(outputStyle,'info', f'Number of documents: {len(res)}')
    for row in res:
      try:
        docID, docType, stack, path, child, _, name = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
      except ValueError:
        reply+= outputString(outputStyle,'error','dch03a: branch data has strange list')
        continue
      if docType.count('/')>5:
        reply+= outputString(outputStyle,'error',f"dch04a: type has too many / {docID}")
      if len(docType.split('/'))==0:
        reply+= outputString(outputStyle,'unsure',f"dch04b: no type in (removed data?) {docID}")
        continue
      if docType.startswith('x') and not docType.startswith(('x0','x1')):
        errorStr = outputString(outputStyle,'error',f"dch04c: bad data type*: {docID} {docType}")
        if repair is None:
          reply+= errorStr
        elif repair(errorStr):
          self.cursor.execute(f"UPDATE main SET type='x1' WHERE id = '{docID}'")
      if not all(k.startswith('x-') for k in stack.split('/')[:-1]):
        reply+= outputString(outputStyle,'error',f"dch03: non-text in stack in id: {docID}")
      if any(len(i)==0 for i in stack) and not docType.startswith('x0'):                    #if no inheritance
        if docType.startswith(('measurement','x')):
          reply+= outputString(outputStyle,'warning',f"branch stack length = 0: no parent {docID}")
        elif not minimal:
          reply+= outputString(outputStyle,'ok',
                                   f"branch stack length = 0: no parent for procedure/sample {docID}")
      try:
        dirNamePrefix = path.split(os.sep)[-1].split('_')[0]
        if dirNamePrefix.isdigit() and child!=int(dirNamePrefix) and docType.startswith('x'):#compare child-number to start of directory name
          reply+= outputString(outputStyle,'error',f"dch05: child-number and dirName dont match {docID}")
      except Exception:
        pass                                                                               #handled next lines
      if path is None:
        if docType.startswith('x'):
          reply+= outputString(outputStyle,'error',f"dch06: branch path is None {docID}")
        elif docType.startswith('measurement'):
          if not minimal:
            reply+= outputString(outputStyle,'ok', f'measurement branch path is None=no data {docID}')
        elif not minimal:
          reply+= outputString(outputStyle,'perfect',f"procedure/sample with empty path {docID}")
      else:                                                                                  #if sensible path
        if len(stack.split('/')) != len(path.split('/')) and path!='*' and not path.startswith('http'):
          #check if length of path and stack coincide; ignore path=None=*
          if docType.startswith('procedure'):
            if not minimal:
              reply+= outputString(outputStyle,'perfect',
                                       f"procedure: branch stack and path lengths not equal: {docID}: {name}")
          else:
            reply+= outputString(outputStyle,'unsure',
              f"branch stack and path lengths not equal: {docID}: {name} {len(stack.split('/'))}"
              f" {len(path.split(os.sep))}")
        if path!='*' and not path.startswith('http'):
          for parentID in stack.split('/')[:-1]:        #check if all parents in doc have a corresponding path
            parentDoc = self.getDoc(parentID)
            if not parentDoc:
              errorStr= outputString(outputStyle,'error',f"branch stack parent is bad: {docID}. Repair: move to lost and found.")
              if repair is None:
                reply+= errorStr
              elif repair(errorStr):
                pathNew = (lostAndFoundProjPath/createDirName(name, 'x0', 0)).as_posix() if docID.startswith('x-')\
                          else '*'
                stackNew = f'{lostAndFoundProjId}/{docID}'
                self.cursor.execute(f"UPDATE branches SET path='{pathNew}', stack='{stackNew}' "\
                                    f"WHERE id='{docID}' AND stack='{stack}'")
                self.connection.commit()
              continue
            parentDocBranches = parentDoc['branch']
            onePathFound = any(path.startswith(parentBranch['path']) for parentBranch in parentDocBranches)
            if not onePathFound:
              if docType.startswith('procedure'):
                if not minimal:
                  reply+= outputString(outputStyle,'perfect',
                    f"dch08: procedure parent does not have corresponding path {docID} | parentID {parentID}")
              else:
                reply+= outputString(outputStyle,'unsure',
                    f"dch08: parent does not have corresponding path {docID} | parentID {parentID}")

    self.cursor.execute('SELECT id, idx FROM branches WHERE idx<0')
    for docID, idx in self.cursor.fetchall():
      reply+= outputString(outputStyle,'error',f"branch idx is bad: {docID} idx: {idx}")

    self.cursor.execute("SELECT id, key FROM properties where key NOT LIKE '%.%'")
    for docID, key in self.cursor.fetchall():
      reply+= outputString(outputStyle,'error',f"key is bad, miss .: {docID} idx: {key}")
    self.cursor.execute("SELECT id, key FROM properties where value LIKE ''")
    for docID, key in self.cursor.fetchall():
      errorStr= outputString(outputStyle,'ok',f"value of this key is missing*: {docID} idx: {key}")
      if repair is None:
        reply+= errorStr
      elif repair(errorStr):
        self.cursor.execute(f"DELETE FROM properties WHERE id='{docID}' AND key='{key}'")
        self.connection.commit()

    cmd = 'SELECT branches.id, branches.path, main.shasum FROM branches JOIN main USING(id) '\
          "WHERE branches.path=='*' AND main.shasum!=''"
    self.cursor.execute(cmd)
    for line in self.cursor.fetchall():
      errorStr= outputString(outputStyle,'error',f"shasum!='' for item with no path docID:{line[0]}. Repair: remove shasum")
      if repair is None:
        reply+= errorStr
      elif repair(errorStr):
        self.cursor.execute(f"UPDATE main SET shasum='' WHERE id = '{line[0]}'")
        self.connection.commit()

    #doc-type specific tests
    cmd = "SELECT qrCodes.id, qrCodes.qrCode FROM qrCodes JOIN main USING(id) WHERE  main.type LIKE 'sample%'"
    self.cursor.execute(cmd)
    if res:= [i[0] for i in self.cursor.fetchall() if i[1] is None]:
      reply+= outputString(outputStyle,'warning',f"dch09: qrCode not in samples {res}")
    self.cursor.execute("SELECT id, shasum, image, comment FROM main WHERE  type LIKE 'measurement%'")
    for row in self.cursor.fetchall():
      docID, shasum, image, comment = row
      if shasum is None:
        reply+= outputString(outputStyle,'warning',f"dch10: shasum not in measurement {docID}")
      if image.startswith('data:image'):                                                      #for jpg and png
        try:
          imgData = base64.b64decode(image[22:])
          Image.open(io.BytesIO(imgData))                    #can convert, that is all that needs to be tested
        except Exception:
          reply+= outputString(outputStyle,'error',f"dch12: jpg-image not valid {docID}")
      elif image.startswith('<?xml'):
        #from https://stackoverflow.com/questions/63419010/check-if-an-image-file-is-a-valid-svg-file-in-python
        SVG_R = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
        SVG_RE = re.compile(SVG_R, re.DOTALL)
        if SVG_RE.match(image) is None:
          reply+= outputString(outputStyle,'error',f"dch13: svg-image not valid {docID}")
      elif image in ('', None):
        comment = comment.replace('\n','..')
        reply+=outputString(outputStyle,'unsure',f"image does not exist {docID} image:{image} comment:{comment}")
      else:
        reply+= outputString(outputStyle,'error',f"dch14: image not valid {docID} {image}")

    #test hierarchy
    for projID in self.getView('viewDocType/x0')['id'].values:
      _, error = self.getHierarchy(projID, True)
      if error:
        reply+= outputString(outputStyle,'error',f"dch15: project hierarchy invalid in project {projID}")
    if repair is not None:
      self.connection.commit()
    return reply
