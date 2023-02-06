""" Long strings that would obfuscate code """

defaultOntology = """
{
  "_id":"-ontology-",
  "-version":2,

  "x0": {"link":"", "label":"Projects", "prop":[
    {"name":"-name",    "query":"What is the name of the project?"},
    {"name":"status",   "query":"What is the project status", "list":["active","paused","passive","finished"]},
    {"name":"objective","query":"What is the objective?"},
    {"name":"tags"},
    {"name":"comment",  "query":"#tags comments remarks :field:value:"}
  ]},
  "x1": {"link":"", "label":"Tasks", "prop":[
    {"name":"-name",    "query":"What is the name of task?"},
    {"name":"comment",  "query":"#tags comments remarks :field:value:"}
  ]},
  "x2": {"link":"", "label":"Subtasks", "prop":[
    {"name":"-name",    "query":"What is the name of subtask?"},
    {"name":"comment",  "query":"#tags comments remarks :field:value:"}
  ]},

  "measurement": {"link":"", "label":"Measurements", "prop":[
    {"name":"-name",       "query":"What is the file name?"},
    {"name":"tags"},
    {"name":"comment",    "query":"#tags comments remarks :field:value:"},
    {"name":"-type"},
    {"name":"image"},
    {"name":"-curated"},
    {"name":"sample",     "query":"Which sample was used?",     "list":"sample"},
    {"name":"procedure",  "query":"Which procedure was used?",  "list":"procedure"}
  ]},
  "sample": {"link":"", "label":"Samples", "prop":[
    {"name":"-name",       "query":"What is the name / identifier of the sample?"},
    {"name":"chemistry",  "query":"What is its chemical composition?"},
    {"name":"tags"},
    {"name":"comment",    "query":"#tags comments remarks :field:value:"},
    {"name":"qrCode"}
  ]},
  "procedure": {"link":"", "label":"Procedures", "prop":[
    {"name":"-name",       "query":"What is the name / path?"},
    {"name":"tags"},
    {"name":"comment",    "query":"#tags comments :field:value: e.g. #SOP_v1"},
    {"name":"content",    "query":"What is procedure (Markdown possible; autofilled if file given)?"}
  ]},
  "instrument": {"link":"", "label":"Instruments", "prop":[
    {"name":"-name",       "query":"What is the name / path?"},
    {"name":"comment",    "query":"#tags comments :field:value: e.g. #SOP_v1"},
    {"name":"vendor",     "query":"Who is the vendor?"}
  ]}
}
"""

setupTextLinux = """
### Welcome to PASTA-ELN setup for Linux
Five components are needed for proper function
- CouchDB
- Configuration of preferences
- Ontology of the datastructure
- Example data

Analyse and (possibly) correct these items.

If the installation is successful, permanently remove the 'pastaELN.log' logfile that is in your home-directory.

Note: this text becomes an installation report
"""


setupTextWindows = """
### Welcome to PASTA-ELN setup for Windows
Seven components are needed for proper function
- CouchDB
- Configuration of preferences
- Ontology of the datastructure
- Shortcut creation
- Example data

Analyse and (possibly) correct these items.

If the installation is successful, permanently remove the 'pastaELN.log' logfile that is in your home-directory (folder above "My Documents").

If an attempt fails, close PASTA-ELN and CMD.exe. Restart CMD.exe and start PASTA-ELN or use Desktop shortcut.

Note: this text becomes an installation report
"""

configurationOverview = """
## Overview
###  Setup: Setup and troubleshoot PASTA-ELN installation
### Project group: configure how project groups are saved
### Ontology: configure the data structure for current project group
### Miscellaneous: different things like look-and-feel
"""

gitWindows = """
Do you want to install git?

Be aware, downloading the installer requires some time, depending on the internet connection.
"""

rootInstallLinux = """
Do you want to install XX--XX?
If you choose yes, a terminal will open and ask you for the super-user password.

Be aware, downloading the installer requires some time, depending on the internet connection.
"""

couchDBWindows = """
Do you want to install CouchDB?

Be aware, downloading the installer requires some time, depending on the internet connection.
"""

restartPastaWindows = """
Close software now (will be done automatically in the future)

Please restart the software by
- clicking on the shortcut OR
- executing the command in a new cmd.exe window
"""

exampleDataLinux = """
Do you want to install the example data?

This step helps to verify the installation and the data is an helpful example for new users.

This step usually takes up to 20sec, so please be patient. Sometimes, linux likes to mention that the program
is hanging and asks if to close/wait. Please WAIT.
"""

exampleDataWindows = """
Do you want to install the example data?

This step helps to verify the installation and the data is an helpful example for new users.

This step usually takes up to 1min, so please be patient.
"""
