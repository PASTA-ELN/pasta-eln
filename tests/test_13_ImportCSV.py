import logging, tempfile
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.project import Project
from pasta_eln.AddOns.project_importCSV import main
from .test_34_GUI_Form import getTable

def verify(self):
  #Verify DB
  output = self.be.checkDB(outputStyle='text')
  output = '\n'.join(output.split('\n')[8:])
  print(output)
  self.assertNotIn('**ERROR', output, 'Error in checkDB')
  self.assertLessEqual(len(output.split('\n')), 8, 'Check db should have less than 8 almost empty lines')
  return

def test_simple(qtbot, caplog):
  # start and wait to be up
  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)
  window = Project(comm)
  window.show()

  # main part
  df = getTable(qtbot, comm, 'x0')
  projID = df[df['name']=='PASTAs Example Project']['id'].values[0]
  main(comm, projID, window, {'fileNames':['tests/inputSamples.csv']})

  df2 = getTable(qtbot, comm, 'sample')
  assert 'sample A' in df2['name'].tolist(), 'Sample A incorrect'
  assert 'sample B' in df2['name'].tolist(), 'Sample B incorrect'
  assert 'sample C' in df2['name'].tolist(), 'Sample C incorrect'

  #clean shutdown
  comm.shutdownBackendThread()
  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
