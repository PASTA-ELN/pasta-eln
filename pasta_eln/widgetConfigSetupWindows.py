""" Widget: setup tab inside the configuration dialog window """
import webbrowser
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QMessageBox, QInputDialog, QFileDialog    # pylint: disable=no-name-in-module
import qtawesome as qta

from .installationTools import getOS, gitAnnex, couchdb, couchdbUserPassword, configuration, ontology, exampleData

class ConfigurationSetup(QWidget):
  """
  Main class
  """
  def __init__(self, backend, callbackFinished):
    super().__init__()
    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)
    self.callbackFinished = callbackFinished

    #widget 1 = screen 1
    self.screen1W = QWidget()
    self.mainL.addWidget(self.screen1W)
    screen1L = QVBoxLayout(self.screen1W)
    self.text1 = QTextEdit()
    self.mainText = """
### Welcome to PASTA-ELN Windows setup
Four components are needed for proper function
- Git-Annex
- CouchDB
- Configuration of preferences
- Ontology of the datastructure

Analyse and (possibly) correct these items.
"""
    self.text1.setMarkdown(self.mainText)
    screen1L.addWidget(self.text1)
    footerW = QWidget()
    screen1L.addWidget(footerW)
    footerL = QHBoxLayout(footerW)
    self.button1 = QPushButton('Start analyse and repair')
    self.button1.clicked.connect(self.analyse)
    footerL.addWidget(self.button1)

  def analyse(self):
    """
    Main method that does all the analysis: open dialogs, ...
    """
    flagContinue = True

    #Git annex
    res = gitAnnex('test')
    if res =='':
      self.mainText = self.mainText.replace('- Git-Annex','- Git-Annex is installed' )
      self.text1.setMarkdown(self.mainText)
    else:
      button = QMessageBox.question(self, "Git-Annex installation", "Do you want to install git-annex?\nIf you choose yes, the installer will open and guide you through the installation.")
      if button == QMessageBox.Yes:
        gitAnnex('install')
      else:
        self.mainText = self.mainText.replace('- Git-Annex','- Git-Annex: user chose to NOT install' )
        self.text1.setMarkdown(self.mainText)
        flagContinue = False

    #Couchdb
    if flagContinue:
      res = couchdb('test')
      if res =='':
        self.mainText = self.mainText.replace('- CouchDB','- CouchDB is installed' )
        self.text1.setMarkdown(self.mainText)
      else:
        tempString = "Do you want to install CouchDB?\nIf you choose yes, the installer will open and guide you through the installation. Please do the following:\n"
        tempString+= "1. click 'Next'\n2. Accept License & 'Next'\n3. 'Next'\n4. enter username (e.g. admin) and password and click 'Validate Credentials' and then 'Next'\n"
        tempString+= "5. 'Install'\n6. 'Finish'"
        button = QMessageBox.question(self, "CouchDB installation", tempString)
        if button == QMessageBox.Yes:
          couchdb('install')
        else:
          self.mainText = self.mainText.replace('- CouchDB','- CouchDB: user chose to NOT install' )
          self.text1.setMarkdown(self.mainText)
          flagContinue = False

    #Configuration
    if flagContinue:
      res = configuration('test')
      if res =='':
        self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration of preferences is acceptable' )
        self.text1.setMarkdown(self.mainText)
      else:
        button = QMessageBox.question(self, "PASTA-ELN configuration", "Do you want to create/repain the configuration.")
        if button == QMessageBox.Yes:
          flagUserPw = True #Continue running until false
          usernameVerified, passwordVerified = '', ''
          while flagUserPw:
            username, ok = QInputDialog.getText(self, 'Username input','Please enter the user name you entered into couchDB.',text='admin')
            if not ok:
              self.mainText = '### User chose to stop during CouchDB installation\nIf you forgot username or password, please uninstall couchdb and execute PASTA-ELN again'
              self.text1.setMarkdown(self.mainText)
              flagContinue = False
              flagUserPw  = False
            elif username!='':
              password, ok = QInputDialog.getText(self, 'Password input','Please enter the password you entered into couchDB.')
              if not ok:
                self.mainText = '### User chose to stop during CouchDB installation\nIf you forgot username or password, please uninstall couchdb and execute PASTA-ELN again'
                self.text1.setMarkdown(self.mainText)
                flagContinue = False
                flagUserPw  = False
              else:
                if password!='' and couchdbUserPassword(username,password):
                  flagUserPw = False  #This is the good and desired end
                  usernameVerified = username
                  passwordVerified = password
          dirName = QFileDialog.getExistingDirectory(self,'Choose directory to save PASTA-ELN data',str(Path.home()))
          configuration('repair',usernameVerified, passwordVerified,dirName)
        else:
          self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration: user chose to NOT install' )
          self.text1.setMarkdown(self.mainText)
          flagContinue = False

    #Ontology
    if flagContinue:
      res = ontology('test')
      if '**ERROR' not in res:
        self.mainText = self.mainText.replace('- Ontology of the datastructure','- Ontology of the datastructure is acceptable\n'+res )
        self.text1.setMarkdown(self.mainText)
      else:
        button = QMessageBox.question(self, "PASTA-ELN ontology", "Do you want to create the default ontology?")
        if button == QMessageBox.Yes:
          ontology('install')
        else:
          self.mainText = self.mainText.replace('- Ontology of the datastructure','- Ontology: user chose to NOT install' )
          self.text1.setMarkdown(self.mainText)
          flagContinue = False

    #Example data
    if flagContinue:
      button = QMessageBox.warning(self, "Example data", "Do you want to install some example data? This helps to verify the installation and guide you.")
      if button == QMessageBox.Yes:
        exampleData()
        self.mainText += '- Example data was added'
        self.text1.setMarkdown(self.mainText)
      else:
        self.mainText += '- Example data was NOT added, per user choice'
        self.text1.setMarkdown(self.mainText)

    #at end
    self.button1.setText('Finished')
    self.button1.clicked.disconnect(self.analyse)
    self.button1.clicked.connect(self.finished)


  def finished(self):
    """
    What do do when setup is finished: success or unsuccessfully
    """
    self.callbackFinished()
