#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, json, uuid
import warnings
import unittest
import pandas as pd
import numpy as np
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.miscTools import DummyProgressBar
from pasta_eln.textTools.stringChanges import outputString

fastTesting = [140211,240037,440182,540113,840047,940160,940372,1240182,1940004,2040113,2040353,2040561,2040768,2040970,2041178,2041400,2240058,2240276,2440166,3440008,4640004,6840020,8340039,8640153,8940012,9140206,9440033,9540062,9740103,9840032,10240079,48240105,48240317,48240521,48240733,48840006,48840221,49740035,49840099,51740129,]
flagfastTesting = True  #test only some entries with those sample numbers; False=test all


class TestStringMethods(unittest.TestCase):
  """
  derived class for this test
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.be = None
    self.dirName = ''


  def test_main(self):
    """
    main function
    """
    dummyProgressBar = DummyProgressBar()
    outputFormat = 'print'  #change to 'print' for human usage, '' for less output
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)

    projectGroup = 'research'
    path = 'testsComplicated/Data_CorrosionDB/'
    idBase = uuid.uuid4().hex[:-9]
    self.be = Backend(projectGroup)

    self.dirName = self.be.basePath
    self.be.exit()
    shutil.rmtree(self.dirName)
    os.makedirs(self.dirName)
    self.be = Backend(projectGroup)
    print()

    ### Update sample information
    self.be.db.cursor.execute('INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                        ['sample', '', '5', 'bh4', '', '', ''])
    self.be.db.cursor.execute('INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                        ['sample', '', '6', 'spec4', '', '', ''])
    self.be.db.cursor.execute('INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                        ['sample', '', '7', 'cd', '', '', ''])
    self.be.db.cursor.execute('INSERT INTO definitions VALUES (?, ?, ?)',['bh4',   'Melt, batch or heat identifier',''])
    self.be.db.cursor.execute('INSERT INTO definitions VALUES (?, ?, ?)',['spec4', 'Internal material specification',''])
    self.be.db.cursor.execute('INSERT INTO definitions VALUES (?, ?, ?)',['cd',    'Date of data entry',''])
    measurementView = 'name,type,.duration,.en2,.initialweight,.si5,.surftreatment'
    self.be.db.cursor.execute(f'UPDATE docTypes SET view = "{measurementView}" WHERE docType = "measurement"')
    sampleView = 'name,.bh4,.spec4,.cd,'
    self.be.db.cursor.execute(f'UPDATE docTypes SET view = "{sampleView}" WHERE docType = "sample"')
    projectView = 'name,.resp1,.dr1'
    self.be.db.cursor.execute(f'UPDATE docTypes SET view = "{projectView}" WHERE docType = "x0"')
    for docType in ['instrument','instrument/extension','workflow','workflow/worklog','workflow/workplan','workflow/procedure']:
      self.be.db.cursor.execute(f'DELETE FROM docTypes WHERE docType = "{docType}"')
      self.be.db.cursor.execute(f'DELETE FROM docTypeSchema WHERE docType = "{docType}"')
    self.be.db.connection.commit()
    self.be.db.connection.commit()

    # # COPY GENERAL FILES
    self.be.addData('x0', {'name':'General information'})
    idProjGeneral = self.be.db.getView('viewDocType/x0')['id'].values[0]
    self.be.changeHierarchy(idProjGeneral)
    shutil.copy(Path(path)/'FieldAcronyms.json', self.be.basePath/self.be.cwd/'FieldAcronyms.json')
    self.be.scanProject(None ,idProjGeneral)

    ### SOURCES = AUTHORS => PROJECTS: loop over them
    outputString(outputFormat,'h2','read c-source_address.json  = SOURCES = AUTHORS')
    tr = {'rn1':'id', 'pi1':'name'}
    authors = json.load(open(path+'Json/C-source_address.json', errors='replace'))
    for item in authors['results'][0]['items']:
      itemsCopy = {}
      for k,v in item.items():
        if k in tr:
          itemsCopy[tr[k]] = v
        else:
          itemsCopy[f'.{k}']=v
      itemsCopy['id'] = f'x-{idBase}_{itemsCopy["id"]:08d}'
      itemsCopy['name'] = itemsCopy['name'].replace('/','_').replace('.','')
      self.be.addData('x0', itemsCopy)
    outputString(outputFormat, 'info', self.be.output('x0'))

    # allow to relate Material to project
    df = pd.read_csv(path+'Relation.csv')
    toDrop = ['JFLAG', 'CMN4', 'CBH4', 'VA5', 'CD', 'CU', 'SI5']
    for label in toDrop:
      df = df.drop(label, axis=1)
    self.be.changeHierarchy(itemsCopy['id'])

    ### MATERIAL => SAMPLES
    outputString(outputFormat,'h2','read materials_pro&designa.json  = SAMPLES = MATERIALS')
    pro= json.load(open(path+'Json/C-material_pro.json', errors='replace'))
    trPro     = {}
    majorPro  = ['rn4', 'bh4', 'spec4', 'cd']
    delPro    = ['cu', 'rn4']
    designa = json.load(open(path+'Json/C-material_designa.json', errors='replace'))
    trDesigna = {'mn4':'name'}
    majorDesigna=['mn4']
    delDesigna= ['rn4','cu']
    for idx0, item in enumerate(pro['results'][0]['items']):
      doc = {}
      #pro
      metaPro = {}
      id = item['rn4']
      if flagfastTesting and id not in fastTesting:
        continue
      for k,v in item.items():
        if k in delPro:
          continue
        newK = trPro[k] if k in trPro else k
        if k in majorPro:
          doc[f'.{newK}'] = v
        else:
          metaPro[newK] = v
      doc['.material_pro'] = metaPro
      #designa
      metaDesigna = {}
      rows = [i for i in designa['results'][0]['items'] if i['rn4']==id]
      if len(rows)==1:
        for k,v in rows[0].items():
          if k in delDesigna:
            continue
          newK = trDesigna[k] if k in trDesigna else k
          if k in majorDesigna:
            doc[newK] = v
          else:
            metaDesigna[newK] = v
        doc['.material_designa'] = metaDesigna
      else:
        pass
        # print('***Warning designa',rows)
      if id==1740015:
        doc['.ccbm'] = [{'el4':'Al','mec4':5.54},{'el4':'C','mec4':0.028},{'el4':'Ca','mec4':0.0006},{'el4':'Co','mec4':0.023}\
                       ,{'el4':'Cr','mec4':20.3},{'el4':'Cu','mec4':0.013},{'el4':'Fe','mec4':72.8},{'el4':'Hf','mec4':0.013,'mac4':0.0156,'mic4':0.0104}\
                       ,{'el4':'Mg','mec4':0.0085},{'el4':'Mn','mec4':0.176},{'el4':'Mo','mec4':0.006,'mac4':0.0072,'mic4':0.0048}\
                       ,{'el4':'N','mec4':0.0038},{'el4':'Nb','mac4':0.001},{'el4':'Ni','mec4':0.163},{'el4':'O','mac4':0.001}\
                       ,{'el4':'P','mac4':0.000001},{'el4':'S','mec4':0.002},{'el4':'Si','mec4':0.038,'mac4':0.054,'mic4':0.022}\
                       ,{'el4':'Ti','mec4':0.005},{'el4':'V','mec4':0.0027,'mac4':0.0032,'mic4':0.0022},{'el4':'Y','mec4':0.039}\
                       ,{'el4':'Zr','mec4':0.0052,'mac4':0.006,'mic4':0.0044}]
      projIDs = df[df['RN4']==id]['RN1']
      if len(projIDs)==0:
        print('Could not find unique proj id for material')
        print(projIDs)
        print(id)
        raise Exception('ERROR')
      for idx, projID in enumerate(np.unique(projIDs)):
        doc['id'] = f's-{idBase[:-2]}_{id:08d}_{idx}'
        self.be.changeHierarchy(None)
        self.be.changeHierarchy(f'x-{idBase}_{projID:08d}')
        self.be.addData('sample', doc)
    outputString(outputFormat, 'info', self.be.output('sample'))


    ### MEASUREMENTS
    outputString(outputFormat,'h2','read all measurement .json')
    rel   = json.load(open(path+'Json/C-relation.json', errors='replace'))
    majorRel  = ['cmn4']
    delRel    = ['cu']

    dimension = json.load(open(path+'Json/C-specimen_dimension.json', errors='replace'))
    majorDimension=['th3','wi3','le3','he3','as3','initialweight']
    delDimension  = ['rn3','cu']

    condition = json.load(open(path+'Json/C-condition_test.json', errors='replace'))
    majorCondition=['en2','tm2']
    delCondition  = ['rn2','cu']

    geopro = json.load(open(path+'Json/C-specimen_geopro.json', errors='replace'))
    majorGeopro=['sn3']
    delGeopro  = ['rn3']

    surface = json.load(open(path+'Json/C-specimen_surface.json', errors='replace'))
    majorSurface=['surftreatment']
    delSurface  = ['rn3','cu']

    t_cor = json.load(open(path+'Json/C-t_cor.json', errors='replace'))
    majorTCor=['mach5','tdate5','si5','duration','tt5']
    delTCor  = ['rn5','cu']

    numMeasurements= len(rel['results'][0]['items'])
    for idx, item in enumerate(rel['results'][0]['items']):
      doc = {}
      #relation.json
      id1 = item['rn1']
      id2 = item.get('rn2',-1)
      id3 = item.get('rn3',-1)
      id4 = item.get('rn4',-1)
      if flagfastTesting and id4 not in fastTesting:
        continue
      id5 = item.get('rn5',-1)
      id7 = item.get('rn7','')
      for k,v in item.items():
        if k in delRel:
          continue
        if k in majorRel:
          doc[f'.{k}'] = v
        else:
          doc[f'relation.{k}'] = v
      #Dimension
      rows = [i for i in dimension['results'][0]['items'] if i['rn3']==id3]
      if len(rows)==1:
        for k,v in rows[0].items():
          if k in delDimension:
            continue
          if k in majorDimension:
            doc[f'.{k}'] = v
          else:
            doc[f'specimen_dimension.{k}'] = v
      else:
        pass
        # print('***Warning dimension',rows)
      # Condition
      rows = [i for i in condition['results'][0]['items'] if i['rn2']==id2]
      if len(rows)==1:
        for k,v in rows[0].items():
          if k in delCondition:
            continue
          if k in majorCondition:
            doc[f'.{k}'] = v
          else:
            doc[f'condition_test.{k}'] = v
      else:
        pass
        # print('***Warning condition',rows)
      #Geopro
      rows = [i for i in geopro['results'][0]['items'] if i['rn3']==id3]
      if len(rows)==1:
        for k,v in rows[0].items():
          if k in delGeopro:
            continue
          if k in majorGeopro:
            doc[f'.{k}'] = v
          else:
            doc[f'specimen_geopro.{k}'] = v
      else:
        pass
        # print('***Warning geopro',rows)
      #Surface
      rows = [i for i in surface['results'][0]['items'] if i['rn3']==id3]
      if len(rows)==1:
        for k,v in rows[0].items():
          if k in delSurface:
            continue
          if k in majorSurface:
            doc[f'.{k}'] = v
          else:
            doc[f'specimen_surface.{k}'] = v
      else:
        pass
        # print('***Warning surface',rows)
      # t_Cor
      rows = [i for i in t_cor['results'][0]['items'] if i['rn5']==id5]
      if len(rows)==1:
        for k,v in rows[0].items():
          if k in delTCor:
            continue
          if k in majorTCor:
            doc[f'.{k}'] = v
          else:
            doc[f't_cor.{k}'] = v
      else:
        pass
        # print('***Warning t_cor',rows)
      # finish
      doc['id'] = f'm-{idBase}_{id5:08d}'
      doc['name'] = f'{id5}.csv'
      doc['.sample'] = f's-{idBase[:-2]}_{id4:08d}_0'
      doc['.rawFile'] = id7
      if idx%1000==0:
        print('SAVE DOC ',doc['id'], round(100.*idx/numMeasurements, 2),'%')

      projIDs = df[df['RN5']==id5]['RN1']
      if len(projIDs)==0:
        print('Could not find unique proj id for material')
        print(projIDs)
        print(id5)
        raise Exception('ERROR')
      projID = list(projIDs)[0]
      self.be.changeHierarchy(None)
      self.be.changeHierarchy(f'x-{idBase}_{projID:08d}')
      fromPath = Path(path)/'timeSeriesFiles'/f'{id5}.csv'
      if fromPath.exists():
        shutil.copy(fromPath, self.be.basePath/self.be.cwd/f'{id5}.csv')
      self.be.addData('measurement', doc)
    outputString(outputFormat, 'info', self.be.output('measurement'))
