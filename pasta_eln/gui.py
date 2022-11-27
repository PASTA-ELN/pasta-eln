#!/usr/bin/python3
import traceback, json
from pathlib import Path
import urllib.request
import webbrowser
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, \
  QHBoxLayout, QTextEdit, QLabel, QStyle
from qt_material import apply_stylesheet

from backend import Pasta
from miscTools import checkConfiguration

# TODO
# KEEP everything together in one file: only after pip-version, create folders, structure, ...
# keep list of packages: PySide6, qt-material

class MainWindow(QMainWindow):
  """
  Main class
  """
  def __init__(self):
    super().__init__()
    self.setWindowTitle('Test PASTA-ELN installation')
    #main widget
    layout = QVBoxLayout()
    mainWidget = QWidget()
    mainWidget.setLayout(layout)
    self.setCentralWidget(mainWidget)
    #button
    button = QPushButton('Test installation')
    button.setCheckable(True)
    button.clicked.connect(self.runTest)
    layout.addWidget(button)
    #graphic for displaying info
    graphic = QWidget()
    self.lytGraphic = QVBoxLayout()
    graphic.setLayout(self.lytGraphic)
    layout.addWidget(graphic)
    #button more
    btnMore = QPushButton('More information')
    btnMore.setCheckable(True)
    btnMore.clicked.connect(self.visible)
    layout.addWidget(btnMore)
    #info-area
    self.info = QTextEdit(mainWidget)
    self.infoText = ''
    self.info.setVisible(False)
    layout.addWidget(self.info)
    return


  def visible(self, checked):
    """
    change visibility of bottom box
    """
    if checked:
      self.info.setVisible(True)
      self.info.setText(self.infoText)
    else:
      self.info.setVisible(False)
    return


  def addLine(self, success, startLabel, anchor):
    """
    add a line to graphical widget
    """
    def clickLink():
      webbrowser.open('https://pasta-eln.github.io/troubleshooting.html#'+anchor)
    #add one line
    widget = QWidget()
    lytWidget = QHBoxLayout()
    if success:
      # img = QPixmap('assets/checkmark.png')
      img = self.style().standardPixmap(QStyle.SP_DialogYesButton).scaledToHeight(24, Qt.SmoothTransformation)
    else:
      #img = QPixmap('assets/redCross.png')
      #should be added to asserts in QT for more efficient ...?!
      img = self.style().standardPixmap(QStyle.SP_DialogNoButton).scaledToHeight(24, Qt.SmoothTransformation)
    label1 = QLabel()
    label1.setPixmap(img)
    lytWidget.addWidget(label1)
    if success:
      label2 = QLabel(startLabel+' is correct')
    else:
      label2 = QLabel(startLabel+' FAILED')
    lytWidget.addWidget(label2)
    lytWidget.addStretch()
    if not success:
      btn3 = QPushButton('?')
      btn3.clicked.connect(clickLink)
      lytWidget.addWidget(btn3)
    widget.setLayout(lytWidget)
    self.lytGraphic.addWidget(widget)


  def runTest(self):
    """
    Run the test itself
    """
    #PART 1 of test: precede with configuration test
    output = checkConfiguration(repair=False)  #verify configuration file .pastaELN.py TODO: Return bool
    self.infoText += output
    self.addLine('ERROR' in output, 'Configuration file', 'problems-after-installation')
    # local and remote server test
    pathConfig = Path.home()/'.pastaELN.json'
    with open(pathConfig,'r', encoding='utf-8') as f:
      config = json.load(f)
    urls = ['http://127.0.0.1:5984']
    database = config['default']
    if config['links'][database]['remote']!={}:
      urls.append(config['links'][database]['remote']['url'])
    for url in urls:
      try:
        with urllib.request.urlopen(url) as package:
          contents = package.read()
          if json.loads(contents)['couchdb'] == 'Welcome':
            self.infoText += 'CouchDB server '+url+' is working: username and password test upcoming'
            self.addLine(True, 'server '+url, 'problems-after-installation')
      except:
        self.infoText += '**ERROR: CouchDB server not working |'+url
        self.addLine(False, 'server '+url, 'problems-after-installation')
        if url=='http://127.0.0.1:5984':
          self.addLine(False, 'ERROR local server ', 'problems-after-installation')
          raise NameError('**ERROR pma01a: Wrong local server.') from None
    #PART 2 start backend
    try:
      be = Pasta(linkDefault=database, initViews=False, initConfig=True, resetOntology=False)
    except:
      self.addLine(False, 'PASTA-backend', 'problems-after-installation')
      self.infoText += '**ERROR: backend could not be started.\n'+traceback.format_exc()+'\n\n'
    #PART 3 of test: main test
    self.infoText += 'database server:'+be.db.db.client.server_url+'\n'
    self.infoText += 'default link:'+be.confLinkName+'\n'
    self.infoText += 'database name:'+be.db.db.database_name+'\n'
    designDocuments = be.db.db.design_documents()
    self.infoText += 'Design documents'+'\n'
    self.addLine(True, 'Design documents exist '+str(len(designDocuments)), 'problems-after-installation')
    for item in designDocuments:
      numViews = len(item['doc']['views']) if 'views' in item['doc'] else 0
      self.infoText += '  '+item['id']+'   Num. of views:'+str(numViews)+'\n'
    try:
      _ = be.db.getDoc('-ontology-')
      self.infoText += 'Ontology exists on server'+'\n'
      self.addLine(True, 'Ontology', 'problems-after-installation')
    except:
      self.infoText += '**ERROR: Ontology does NOT exist on server'+'\n'
      self.addLine(False, 'Ontology', 'problems-after-installation')
    self.infoText += 'local directory: '+str(be.basePath)+'\n'
    self.infoText += 'software directory: '+str(be.softwarePath)+'\n'
    self.info.setText(self.infoText)
    return

def main():
  app = QApplication([])
  window = MainWindow()
  apply_stylesheet(app, theme='dark_blue.xml')
  window.show()
  app.exec()

if __name__ == '__main__':
  main()
