#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, traceback, logging, socket
import warnings
import unittest
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.miscTools import outputString

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
    outputFormat = 'print'
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    warnings.filterwarnings('ignore', module='js2py')
    if socket.gethostname()=='dena':  #SB's computer
      projectGroup = 'pasta_tutorial'
    else:
      projectGroup = 'research'
    self.be = Backend(projectGroup, initConfig=False)
    self.dirName = self.be.basePath
    self.be.exit(deleteDB=True)
    shutil.rmtree(self.dirName)
    os.makedirs(self.dirName)
    self.be = Backend(projectGroup, initViews=True, initConfig=False)

    try:
      ### CREATE PROJECTS AND SHOW
      outputString(outputFormat,'h2','CREATE PROJECTS AND SHOW')
      self.be.addData('x0', {'-name': 'Demonstrator: Indentation', \
        'objective': 'Can we show interaction of the 3 TA-WSD members', 'status': 'active', \
        'comment': '#NFDI I am a comment for the project'})  #HT
      outputString(outputFormat, 'info', self.be.output('x0'))

      ### TEST PROJECT PLANING
      outputString(outputFormat,'h2','TEST PROJECT PLANING')
      idProj = self.be.db.getView('viewDocType/x0')[0]['id']
      self.be.changeHierarchy(idProj)
      idIndent   = self.be.addData('x1',    {'-name': 'Nanoindentation','comment': 'executed at FZJ'})  #HT
      self.be.changeHierarchy(idIndent)
      pathIndent = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      idConfocal = self.be.addData('x1',    {'-name': 'Confocal microscopy','comment': 'executed at FZJ'}) #HT
      self.be.changeHierarchy(idConfocal)
      pathConfocal = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      idArea     = self.be.addData('x1',    {'-name': 'Area identification','comment': 'executed at DZKI'})#HT
      self.be.changeHierarchy(idArea)
      pathArea = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      idDFT      = self.be.addData('x1',    {'-name': 'DFT simulations','comment': 'executed at MPIE'})#HT
      self.be.changeHierarchy(idDFT)
      pathDFT = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      outputString(outputFormat,'info',self.be.outputHierarchy())

      ### TEST PROCEDURES
      outputString(outputFormat,'h2','TEST PROCEDURES')
      sopDir = self.dirName/'StandardOperatingProcedures'
      os.makedirs(sopDir)
      with open(sopDir/'Nanoindentation.md','w', encoding='utf-8') as fOut:
        fOut.write('### Put sample in nanoindenter\n### Do indentation\nDo not forget to\n- calibrate tip\n- *calibrate stiffness*\n') #HT
      with open(sopDir/'Confocal.md','w', encoding='utf-8') as fOut:
        fOut.write('### Put sample in Confocal\n### Do scanning\nDo not forget to\n- focus\n- adjust contrast\n') #HT
      self.be.addData('procedure', {'-name': 'StandardOperatingProcedures/Confocal.md', 'comment': '#v1'})
      self.be.addData('procedure', {'-name': 'StandardOperatingProcedures/Nanoindentation.md', 'comment': '#v1'})
      outputString(outputFormat,'info',self.be.output('procedure'))

      ### TEST SAMPLES
      outputString(outputFormat,'h2','TEST SAMPLES')
      self.be.addData('sample',    {'-name': 'Al', 'chemistry': 'Al99.9', 'qrCode': '13214124 99698708', 'comment': 'from RWTH S. Pruente'}) #HT
      outputString(outputFormat,'info',self.be.output('sample'))
      outputString(outputFormat,'info',self.be.outputQR())

      ###  TEST MEASUREMENTS AND SCANNING
      outputString(outputFormat,'h2','TEST MEASUREMENTS AND SCANNING')
      examplePath = Path(__file__).parent/'DemonstratorIndentation'
      for i in [10,20,40,80,160]:
        shutil.copy(examplePath/('Al_'+str(i)+'mN_load20s_hold5s.hdf5'), pathIndent)
      for i in range(1,6):
        shutil.copy(examplePath/('Al_10mN_'+str(i)+'.gwy'), pathConfocal)
        shutil.copy(examplePath/('Al_160mN_'+str(i)+'.gwy'), pathConfocal)
      shutil.copy(examplePath/('Al_20mN.gwy'), pathConfocal)
      for i in [40,80]:
        shutil.copy(examplePath/('Al_'+str(i)+'mN_1and6.gwy'), pathConfocal)
        shutil.copy(examplePath/('Al_'+str(i)+'mN_2and5.gwy'), pathConfocal)
        shutil.copy(examplePath/('Al_'+str(i)+'mN_3and4.gwy'), pathConfocal)
      shutil.copy(examplePath/'elastic_constants.ipynb', pathDFT)
      self.be.scanProject(idProj)

      ### ADD INSTRUMENTS AND THEIR ATTACHMENTS
      outputString(outputFormat,'h2','ADD INSTRUMENTS AND ATTACHMENTS')
      self.be.addData('instrument', {'-name': 'FischerScope', 'vendor':'Fischer', 'model':'100'})#HT
      self.be.addData('instrument', {'-name': 'Confocal', 'vendor':'XXX', 'model':'YYY'})#HT
      outputString(outputFormat,'info',self.be.output('instrument'))


      ### VERIFY DATABASE INTEGRITY
      outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
      outputString(outputFormat,'info', self.be.checkDB(outputStyle='text'))
      outputString(outputFormat,'h2','DONE WITH VERIFY')
    except:
      outputString(outputFormat,'h2','ERROR OCCURRED IN VERIFY TESTING\n'+ traceback.format_exc() )
      raise
    return

  def tearDown(self):
    logging.info('End 3Projects test')
    return

if __name__ == '__main__':
  unittest.main()
