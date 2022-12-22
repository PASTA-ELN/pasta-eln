##Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, QFormLayout, QLineEdit, QRadioButton, QLabel, QCheckBox, QGridLayout
import qtawesome as qta

from installationTools import getOS, datalad

class Configuration(QDialog):
  """
  Main class
  """
  def __init__(self, backend, cbFunction):
    super(Configuration, self).__init__()
    self.backend = backend
    self.setWindowTitle('PASTA-ELN configuration')
    self.mainLayout = QVBoxLayout()
    self.setLayout(self.mainLayout)
    self.tabWidget = QTabWidget(self)
    self.mainLayout.addWidget(self.tabWidget)

    # ---------------------
    # Setup / Troubeshoot Pasta: main widget
    self.tabSetup = QWidget()
    self.tabWidget.addTab(self.tabSetup, 'Setup')
    self.tabLayout = QGridLayout()
    self.tabSetup.setLayout(self.tabLayout)

    title = QLabel('PASTA-ELN: setup and troubleshoot local installation. All items have have to work.')
    self.tabLayout.addWidget(title, 0, 0, 1, 3)

    title = QLabel('Operating system is: "'+getOS()+'"')
    self.tabLayout.addWidget(title, 1, 0, 1, 3)

    title = QLabel('Datalad')
    self.tabLayout.addWidget(title, 2, 0)
    icon = qta.icon('fa.question', scale_factor=1.2)
    button = QPushButton(icon, "")  #icon with no text
    button.clicked.connect(lambda: self.datalad('test'))
    self.tabLayout.addWidget(button, 2, 1)
    title = QLabel('Datalad ensures that data is synchronized to server.')
    self.tabLayout.addWidget(title, 2, 2)

    title = QLabel('CouchDB')
    self.tabLayout.addWidget(title, 3, 0)
    icon = qta.icon('fa.question', scale_factor=1.2)
    button = QPushButton(icon, "")
    button.clicked.connect(lambda: self.couchdb('test'))
    self.tabLayout.addWidget(button, 3, 1)
    title = QLabel('CouchDB is the local database for metadata.')
    self.tabLayout.addWidget(title, 3, 2)

    title = QLabel('Configuration')
    self.tabLayout.addWidget(title, 4, 0)
    icon = qta.icon('fa.question', scale_factor=1.2)
    button = QPushButton(icon, "")
    button.clicked.connect(lambda: self.configuration('test'))
    self.tabLayout.addWidget(button, 4, 1)
    title = QLabel('PASTA-ELN has a global configuration.')
    self.tabLayout.addWidget(title, 4, 2)

    title = QLabel('Ontology')
    self.tabLayout.addWidget(title, 5, 0)
    icon = qta.icon('fa.question', scale_factor=1.2)
    button = QPushButton(icon, "")
    button.clicked.connect(lambda: self.ontology('test'))
    self.tabLayout.addWidget(button, 5, 1)
    title = QLabel('Each project group has its own configuration.')
    self.tabLayout.addWidget(title, 5, 2)
    print('....',self.backend.basePath)


    # ---------------------
    # Misc configuration: e.g. theming...
    self.tabConfig = QWidget()
    self.tabWidget.addTab(self.tabConfig, 'Miscellaneous')
    #...
    #magic order
    #Comment says what you do
    #1. define widget
    #2. define layout and assign to widget
    #3. define and add elements immediately

  def datalad(self, command):
    if command == 'help':
      webbrowser.open('https://pasta-eln.github.io/troubleshooting.html#'+anchor)

    if command == 'test':
      if datalad(command):
        icon = qta.icon('fa.check', scale_factor=1.2)
        button = QPushButton(icon, "")
        self.tabLayout.addWidget(button, 2, 1)
      else:
        button = QPushButton('Repair')
        button.clicked.connect(lambda: datalad('repair'))
        self.tabLayout.addWidget(button, 2, 1)
        button = QPushButton('Help')
        button.clicked.connect(lambda: datalad('help'))
        self.tabLayout.addWidget(button, 2, 3)


  def couchdb(self, command):
    print('couchdb...',command)

  def configuration(self, command):
    print('config...',command)

  def ontology(self, command):
    print('ontology...',command)
