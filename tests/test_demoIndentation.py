#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, traceback, logging, socket
import warnings
import unittest
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.miscTools import outputString
from pasta_eln.miscTools import DummyProgressBar

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
      self.be.addData('x0', {'-name': 'Demonstrator - Youngs modulus of EN AW 1050A', \
        'objective': 'To follow a journey of real materials scientists that study elastic modulus using RDM tools and solutions developed by the NFDI-MatWerk community', 'status': 'active', \
        'comment': '#NFDI This project includes indentation and confocal microscopy data.'})
      outputString(outputFormat, 'info', self.be.output('x0'))

      ### TEST PROJECT PLANING
      outputString(outputFormat,'h2','TEST PROJECT PLANING')
      idProj = self.be.db.getView('viewDocType/x0')[0]['id']
      self.be.changeHierarchy(idProj)
      idIndent   = self.be.addData('x1',    {'-name': 'Nanoindentation','comment': 'executed at FZJ'})
      self.be.changeHierarchy(idIndent)
      pathIndent = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      idConfocal = self.be.addData('x1',    {'-name': 'Confocal microscopy','comment': 'executed at FZJ'})
      self.be.changeHierarchy(idConfocal)
      pathConfocal = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      idArea     = self.be.addData('x1',    {'-name': 'Area identification via image analysis','comment': 'executed at DFKI'})
      self.be.changeHierarchy(idArea)
      pathArea = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      idDFT      = self.be.addData('x1',    {'-name': 'Molecular statics simulations','comment': 'executed at MPIE'})
      self.be.changeHierarchy(idDFT)
      pathDFT = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      outputString(outputFormat,'info',self.be.outputHierarchy())

      ### TEST PROCEDURES
      outputString(outputFormat,'h2','TEST PROCEDURES')
      sopDir = self.dirName/'StandardOperatingProcedures'
      os.makedirs(sopDir)
      with open(sopDir/'Nanoindentation.md','w', encoding='utf-8') as fOut:
        fOut.write('### Nanoindentation instructions\n1. Insert sample into the glovebox (Siemens SIMATIC HMI)\n   * Vacuum box has to be refilled 3 times with Ar gas\n   * Open the vacuum box from the inside and place the sample under the microscope\n\n2. Setting up the experiment (Vickers nanoindentation)\n   * Find the area of interest using an appropriate microscope magnification setting (default- 40x)\n   * Define measurement parameters: normal force, time until maximum load, hold time at maximum load\n   * Select the positions for the required number of indents (define correct spacing)\n   * Start the experiment\n\n3. After the experiment:\n   * Save the nanoindentation curves to the local storage\n   * Download the data\n   * Remove the sample from the instrument and glovebox",\n')
      with open(sopDir/'Confocal.md','w', encoding='utf-8') as fOut:
        fOut.write('### Confocal microscopy instructions\n1. Place the sample on the platform below the lens\n   * The lens should be at its smallest setting 5x\n\n2. Measurement procedure\n   * Adjust the height of the specimen manually by moving the platform up or down until the surface will be in focus\n   * Search for the area of interest\n   * Select stronger lenses and adjust the focus  each time when the lens is changed\n   * Repeat until desired magnification is reached (5x, 10x, 20x, 50x, 100x)\n   * Adjust the brightness settings so that the surface does not appear too bright (red areas in the image)\n   * Scan the area\n   * Save the image\n   * To move to a different area, select a lens with smaller magnification if needed (esp. for measurement with 100x lens)\n\n3. Finishing the measurement:\n   *  Select the 5x lens\n   * Remove the sample from the platform\n   * Save the files on the local storage device\n')
      self.be.addData('procedure', {'-name': 'StandardOperatingProcedures/Confocal.md', 'comment': '#v1'})
      self.be.addData('procedure', {'-name': 'StandardOperatingProcedures/Nanoindentation.md', 'comment': '#v1'})
      outputString(outputFormat,'info',self.be.output('procedure'))

      ### TEST SAMPLES
      outputString(outputFormat,'h2','TEST SAMPLES')
      self.be.addData('sample',    {'-name': 'EN AW 1050A', 'chemistry': 'Al 99.5, Si 0.25, Fe 0.25', 'qrCode': '13214124 99698708', 'comment': ' received from RWTH S. Pruente'})
      outputString(outputFormat,'info',self.be.output('sample'))
      outputString(outputFormat,'info',self.be.outputQR())

      ###  TEST MEASUREMENTS AND SCANNING
      outputString(outputFormat,'h2','TEST MEASUREMENTS AND SCANNING')
      examplePath = Path(__file__).parent/'DemonstratorIndentation'
      for i in [10,20,40,80,160]:
        shutil.copy(examplePath/('Al_'+str(i)+'mN_load20s_hold5s.hdf5'), pathIndent)
      for i in range(1,3):
        shutil.copy(examplePath/('Al_10mN_'+str(i)+'.gwy'), pathConfocal)
        shutil.copy(examplePath/('Al_160mN_'+str(i)+'.gwy'), pathConfocal)
      shutil.copy(examplePath/('Al_20mN.gwy'), pathConfocal)
      for i in [40]:
        shutil.copy(examplePath/('Al_'+str(i)+'mN_1and6.gwy'), pathConfocal)
        shutil.copy(examplePath/('Al_'+str(i)+'mN_2and5.gwy'), pathConfocal)
        shutil.copy(examplePath/('Al_'+str(i)+'mN_3and4.gwy'), pathConfocal)
      shutil.copy(examplePath/'elastic_constants.ipynb', pathDFT)
      self.be.scanProject(dummyProgressBar ,idProj)

      ### ADD INSTRUMENTS AND THEIR ATTACHMENTS
      outputString(outputFormat,'h2','ADD INSTRUMENTS AND ATTACHMENTS')
      self.be.addData('instrument', {'-name': 'Fischerscope', 'vendor':'Fischer', 'model':'H100C'})
      self.be.addData('instrument', {'-name': 'Confocal', 'vendor':'LEXT', 'model':'OLS4000'})
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
