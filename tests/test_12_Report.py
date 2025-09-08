import logging, tempfile
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.AddOns.project_html_report import main
from .test_34_GUI_Form import getTable

def test_simple(qtbot, caplog):
  # start and wait to be up
  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

  # main part
  df = getTable(qtbot, comm, 'x0')
  projID = df[df['name']=='PASTAs Example Project']['id'].values[0]
  tempDir = tempfile.gettempdir()
  fileName = f'{tempDir}/temp.html'
  print(f'Filename {fileName}')
  main(comm, projID, None, {'fileNames':[fileName]})

  #clean shutdown
  comm.shutdownBackendThread()
  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
