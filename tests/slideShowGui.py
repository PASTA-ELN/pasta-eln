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
from pasta_eln.GUI.sidebar import Sidebar
from pasta_eln.GUI.palette import Palette
from pasta_eln.GUI.form import Form

class SlideShow(QMainWindow):
  def __init__(self, createData=False, theme='none'):
    super().__init__()
    if createData:
      exampleData(True, None, 'research', '')
    self.backend = Backend('research')
    palette      = Palette(self, theme)
    self.comm    = Communicate(self.backend, palette)

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

  def testSidebar(self, docID):
    """
    table
    """
    self.setWindowTitle('Test sidebar')
    widget = Sidebar(self.comm)
    widget.setMinimumHeight(800)
    widget.setMinimumWidth(800)
    self.setCentralWidget(widget)
    self.comm.changeSidebar.emit(docID)
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


  def testForm(self, docID):
    """
    form view
    """
    doc = self.comm.backend.db.getDoc(docID)
    dialog = Form(self.comm, doc)
    dialog.show()
    return


def main(tasks=['detail'], theme='none'):
  """ Main function
  Args:
    tasks: project, table, detail, sidebar
    theme: theme without xml
  """
  app = QApplication()
  apply_stylesheet(app, theme=f'{theme}.xml')
  window = SlideShow(createData=False, theme=theme)
  allProjects = window.backend.db.getView('viewDocType/x0All')['id'].values
  if 'project' in tasks:           # project views
    for docID in allProjects:
      window.testProject(docID)
      window.show()
      app.exec()
  if 'table' in tasks:             # all tables
    for docType in ['_tags_','x0','measurement','procedure','sample','instrument','-']:
      window.testTable(docType)
      window.show()
      app.exec()
  if 'sidebar' in tasks:           # sidebar
    for docID in allProjects:
      window.testSidebar(docID)
      window.show()
      app.exec()
  if 'form' in tasks:             # form
    window.testForm(allProjects[0])
    app.exec()
  if 'detail' in tasks:           # all measurements
    allTasks =  window.backend.db.getView('viewDocType/measurementAll')['id'].to_list()
    allTasks += window.backend.db.getView('viewDocType/sampleAll')['id'].to_list()
    for docID in allTasks:
      print()
      window.testDetails(docID)
      window.show()
      app.exec()
  return

# all widgets: are good for all themes and both none
if __name__ == '__main__':
  # main(['detail','sidebar','detail','table','project','form'],'none')  # to test all colors everywhere
  main(['table'],'none')
