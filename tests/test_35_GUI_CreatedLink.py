import logging
from pathlib import Path
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.form import Form
from .test_34_GUI_Form import getTable

def test_simple(qtbot, caplog):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

  # identify items that change
  tabMeasurements = getTable(qtbot, comm, 'measurement')
  tabSamples = getTable(qtbot, comm, 'sample')
  idSample = tabSamples[tabSamples['name']=='Example sample']['id'].values[0]
  idMeasurement = tabMeasurements[tabMeasurements['name']=='example.tif']['id'].values[0]

  # find file
  pathExtractor = Path(__file__).parent.parent/'pasta_eln'/'AddOns'/'extractor_tif.py'

  print(pathExtractor, pathExtractor.exists())
  print(tabMeasurements)
  print(tabSamples)
  print(idSample, idMeasurement)

  # docID = table[table['name']=='simple.png']['id'].values[0]
  # dialog = Form(comm, {'id':docID})
  # dialog.setMinimumSize(1024,800)
  # dialog.show()
  # qtbot.addWidget(dialog)
  # while True:
  #   qtbot.wait(100)
  #   if len(dialog.doc) > 2 and dialog.docTypeComboBox.count()>2:
  #     break
  # qtbot.wait(1000)
  # path = qtbot.screenshot(dialog)
  # print(path)

  comm.shutdownBackendThread()
  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
