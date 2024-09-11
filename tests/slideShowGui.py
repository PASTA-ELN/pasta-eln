#!/usr/bin/python3
"""Create a GUI slide show of all widgets """
from PySide6.QtWidgets import QApplication, QMainWindow
from qt_material import apply_stylesheet  # of https://github.com/UN-GCPDS/qt-material
from pasta_eln.backend import Backend
from pasta_eln.installationTools import exampleData
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.GUI.details import Details
from pasta_eln.GUI.table import Table
from pasta_eln.GUI.project import Project

class SlideShow(QMainWindow):
  def __init__(self, createData=False):
    super().__init__()
    if createData:
      exampleData(True, None, 'research', '')
    self.backend = Backend('research')
    self.comm = Communicate(self.backend)

  def testDetails(self, docID):
    """
    details
    """
    self.setWindowTitle(f'Test docID {docID}')
    widget = Details(self.comm)
    widget.setMinimumHeight(1000)
    self.setCentralWidget(widget)
    self.comm.changeDetails.emit(docID)
    return

  def testTable(self, docType):
    """
    table
    """
    self.setWindowTitle(f'Test docType {docType}')
    widget = Table(self.comm)
    widget.setMinimumWidth(1200)
    self.setCentralWidget(widget)
    self.comm.changeTable.emit(docType,'')
    return

  def testProject(self, docID):
    """
    project view
    """
    self.setWindowTitle(f'Test docID {docID}')
    widget = Project(self.comm)
    widget.setMinimumHeight(1000)
    widget.setMinimumWidth(1200)
    self.setCentralWidget(widget)
    self.comm.changeProject.emit(docID,'')
    return


def main(tasks=['detail'], theme='dark_blue'):
  """ Main function
  Args:
    tasks: project, table, detail
    theme: theme without xml
  """
  app = QApplication()
  apply_stylesheet(app, theme=f'{theme}.xml')
  window = SlideShow(createData=False)
  if 'project' in tasks:           # project views
    allProjects = window.backend.db.getView('viewDocType/x0All')['id'].values
    for docID in allProjects:
      window.testProject(docID)
      window.show()
      app.exec()
  if 'table' in tasks:             # all tables
    for docType in ['_tags_']: #,'x0','measurement','procedure','sample','instrument','-']:
      window.testTable(docType)
      window.show()
      app.exec()
  if 'detail' in tasks:           # all measurements
    allTasks =  window.backend.db.getView('viewDocType/measurementAll')['id'].to_list()
    allTasks += window.backend.db.getView('viewDocType/sampleAll')['id'].to_list()
    print(allTasks)
    for docID in allTasks:
      window.testDetails(docID)
      window.show()
      app.exec()
  return


if __name__ == '__main__':
  main()
  # main(['table'], "dark_blue")
