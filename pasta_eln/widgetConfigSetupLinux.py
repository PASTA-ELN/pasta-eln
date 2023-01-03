""" Widget: setup tab inside the configuration dialog window """
import webbrowser
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton    # pylint: disable=no-name-in-module
import qtawesome as qta

from .installationTools import getOS, gitAnnex, couchdb, configuration, ontology, exampleData

class ConfigurationSetup(QWidget):
  """
  Main class
  """
  def __init__(self, backend):
    super().__init__()
    self.tabLayout = QVBoxLayout()
    self.setLayout(self.tabLayout)

    self.tabSetupBody = QWidget()
    self.tabLayout.addWidget(self.tabSetupBody)
    self.tabLayoutBody = QGridLayout()
    self.tabSetupBody.setLayout(self.tabLayoutBody)

    title = QLabel('PASTA-ELN: setup and troubleshoot local installation. All items have have to work.')
    self.tabLayoutBody.addWidget(title, 0, 0, 1, 3)

    title = QLabel('Operating system is: "'+getOS()+'"')
    self.tabLayoutBody.addWidget(title, 1, 0, 1, 3)

    title = QLabel('git annex')
    self.tabLayoutBody.addWidget(title, 2, 0)
    icon = qta.icon('fa.question', scale_factor=1.2)
    button = QPushButton(icon, "")  #icon with no text
    button.clicked.connect(lambda: self.gitAnnex('test'))
    self.tabLayoutBody.addWidget(button, 2, 1)
    title = QLabel('Git annex and datalad ensure that data is synchronized to server.')
    self.tabLayoutBody.addWidget(title, 2, 2)

    title = QLabel('CouchDB')
    self.tabLayoutBody.addWidget(title, 3, 0)
    icon = qta.icon('fa.question', scale_factor=1.2)
    button = QPushButton(icon, "")
    button.clicked.connect(lambda: self.couchdb('test'))
    self.tabLayoutBody.addWidget(button, 3, 1)
    title = QLabel('CouchDB is the local database for metadata.')
    self.tabLayoutBody.addWidget(title, 3, 2)

    title = QLabel('Configuration')
    self.tabLayoutBody.addWidget(title, 4, 0)
    icon = qta.icon('fa.question', scale_factor=1.2)
    button = QPushButton(icon, "")
    button.clicked.connect(lambda: self.configuration('test'))
    self.tabLayoutBody.addWidget(button, 4, 1)
    title = QLabel('PASTA-ELN has a global configuration.')
    self.tabLayoutBody.addWidget(title, 4, 2)

    title = QLabel('Ontology')
    self.tabLayoutBody.addWidget(title, 5, 0)
    icon = qta.icon('fa.question', scale_factor=1.2)
    button = QPushButton(icon, "")
    button.clicked.connect(lambda: self.ontology('test'))
    self.tabLayoutBody.addWidget(button, 5, 1)
    title = QLabel('Each project group has its own configuration.')
    self.tabLayoutBody.addWidget(title, 5, 2)


    footer = QWidget()
    self.tabLayout.addWidget(footer)
    footerLayout = QHBoxLayout()
    footer.setLayout(footerLayout)
    button = QPushButton('Create example data')
    footerLayout.addWidget(button)
    button = QPushButton('Cancel')
    footerLayout.addWidget(button)
    button = QPushButton('OK')
    footerLayout.addWidget(button)


  def gitAnnex(self, command):
    """
    Function to test and install git-annex

    Args:
      command (str): options=test, install
    """
    if command == 'test':
      if gitAnnex('test') == '':
        icon = qta.icon('fa.check', scale_factor=1.2)
        button = QPushButton(icon, "")
        self.tabLayoutBody.addWidget(button, 2, 1)
      else:
        button = QPushButton('Install')
        button.clicked.connect(lambda: gitAnnex('install'))
        self.tabLayoutBody.addWidget(button, 2, 1)
        button = QPushButton('Help')
        button.clicked.connect(lambda: self.help('gitAnnex'))
        self.tabLayoutBody.addWidget(button, 2, 3)
    else:
      gitAnnex('install')
      icon = qta.icon('fa.question', scale_factor=1.2)
      button = QPushButton(icon, "")  #icon with no text
      button.clicked.connect(lambda: self.gitAnnex('test'))
      self.tabLayoutBody.addWidget(button, 2, 1)
    return


  def couchdb(self, command):
    """
    Function to test and install couch-DB

    Args:
      command (str): options=test, install
    """
    if command == 'test':
      if couchdb('test') == '':
        icon = qta.icon('fa.check', scale_factor=1.2)
        button = QPushButton(icon, "")
        self.tabLayoutBody.addWidget(button, 3, 1)
      else:
        button = QPushButton('Install')
        button.clicked.connect(lambda: couchdb('install'))
        self.tabLayoutBody.addWidget(button, 3, 1)
        button = QPushButton('Help')
        button.clicked.connect(lambda: self.help('couchdb'))
        self.tabLayoutBody.addWidget(button, 3, 3)
    else:
      couchdb('install')
      icon = qta.icon('fa.question', scale_factor=1.2)
      button = QPushButton(icon, "")  #icon with no text
      button.clicked.connect(lambda: self.couchdb('test'))
      self.tabLayoutBody.addWidget(button, 3, 1)
    return


  def configuration(self, command):
    """
    Function to test and repair the .pastaELN.json file in the home directory

    Args:
      command (str): options=test, repair
    """
    if command == 'test':
      if configuration('test') == '':
        icon = qta.icon('fa.check', scale_factor=1.2)
        button = QPushButton(icon, "")
        self.tabLayoutBody.addWidget(button, 4, 1)
      else:
        button = QPushButton('Install')
        button.clicked.connect(lambda: configuration('install'))
        self.tabLayoutBody.addWidget(button, 4, 1)
        button = QPushButton('Help')
        button.clicked.connect(lambda: self.help('configuration'))
        self.tabLayoutBody.addWidget(button, 4, 3)
    else:
      configuration('install')
      icon = qta.icon('fa.question', scale_factor=1.2)
      button = QPushButton(icon, "")  #icon with no text
      button.clicked.connect(lambda: self.configuration('test'))
      self.tabLayoutBody.addWidget(button, 4, 1)
    return


  def ontology(self, command):
    """
    Function to test and create ontology

    Args:
      command (str): options=test, install
    """
    if command == 'test':
      answer = ontology('test')
      if '**ERROR' not in answer:
        icon = qta.icon('fa.check', scale_factor=1.2)
        button = QPushButton(icon, "")
        self.tabLayoutBody.addWidget(button, 5, 1)
        title = QLabel(answer)
        self.tabLayoutBody.addWidget(title, 5, 2)
      else:
        button = QPushButton('Install')
        button.clicked.connect(lambda: ontology('install'))
        self.tabLayoutBody.addWidget(button, 5, 1)
        button = QPushButton('Help')
        button.clicked.connect(lambda: self.help('ontology'))
        self.tabLayoutBody.addWidget(button, 5, 3)
    else:
      ontology('install')
      icon = qta.icon('fa.question', scale_factor=1.2)
      button = QPushButton(icon, "")  #icon with no text
      button.clicked.connect(lambda: self.ontology('test'))
      self.tabLayoutBody.addWidget(button, 5, 1)
    return

  @classmethod
  def help(cls, topic):
    """
    Open browser with help information

    Args:
      topic (str): topic that should be helped
    """
    baseURL = 'https://pasta-eln.github.io/troubleshooting.html#'
    system = getOS().replace(' ','_')
    webbrowser.open(baseURL+system+'_'+topic)
    return
