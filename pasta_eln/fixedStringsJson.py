""" Long strings and dictionaries/JSON that would obfuscate code """
from typing import Any

defaultOntology: dict[str, Any] = {
  "_id": "-ontology-",
  "-version": 3,

  "x0": {"IRI": "", "attachments": [], "displayedTitle": "Projects", "metadata": {"default": [
    {"name": "-name", "query": "What is the name of the project?", "mandatory": True},
    {"name": "-tags", "query": "What are the tags associated with the project?", "mandatory": True},
    {"name": "status", "query": "What is the project status", "list": ["active", "paused", "passive", "finished"]},
    {"name": "objective", "query": "What is the objective?"},
    {"name": "comment", "query": "#tags comments remarks :field:value:"}
  ]}},
  "x1": {"IRI": "", "attachments": [], "displayedTitle": "Folders", "metadata": {"default": [
    {"name": "-name", "query": "What is the name of task?", "mandatory": True},
    {"name": "-tags", "query": "What are the tags associated with the task?", "mandatory": True},
    {"name": "comment", "query": "#tags comments remarks :field:value:"}
  ]}},
  "x2": {"IRI": "", "attachments": [], "displayedTitle": "Folders", "metadata": {"default": [
    {"name": "-name", "query": "What is the name of subtask?", "mandatory": True},
    {"name": "-tags", "query": "What are the tags associated with the subtask?", "mandatory": True},
    {"name": "comment", "query": "#tags comments remarks :field:value:"}
  ]}},

  "measurement": {"IRI": "", "attachments": [], "displayedTitle": "Measurements", "metadata": {"default": [
    {"name": "-name", "query": "What is the name of file name?", "mandatory": True},
    {"name": "-tags", "query": "What are the tags associated with the file name?", "mandatory": True},
    {"name": "comment", "query": "#tags comments remarks :field:value:"},
    {"name": "-type"},
    {"name": "image"},
    {"name": "#_curated"},
    {"name": "sample", "query": "Which sample was used?", "list": "sample"},
    {"name": "procedure", "query": "Which procedure was used?", "list": "procedure"}
  ]}},
  "sample": {"IRI": "", "attachments": [], "displayedTitle": "Samples", "metadata": {"default": [
    {"name": "-name", "query": "What is the name / identifier of the sample?", "mandatory": True},
    {"name": "-tags", "query": "What are the tags associated with the sample?", "mandatory": True},
    {"name": "chemistry", "query": "What is its chemical composition?"},
    {"name": "comment", "query": "#tags comments remarks :field:value:"},
    {"name": "qrCode"}
  ]}},
  "procedure": {"IRI": "", "attachments": [], "displayedTitle": "Procedures", "metadata": {"default": [
    {"name": "-name", "query": "What is the name / path of the procedure?", "mandatory": True},
    {"name": "-tags", "query": "What are the tags associated with the procedure?", "mandatory": True},
    {"name": "comment", "query": "#tags comments :field:value: e.g. #SOP_v1"},
    {"name": "content", "query": "What is procedure (Markdown possible; autofill if file given)?"}
  ]}},
  "instrument": {"IRI": "", "attachments": [], "displayedTitle": "Instruments", "metadata": {"default": [
    {"name": "-name", "query": "What is the name / path of the instrument?", "mandatory": True},
    {"name": "-tags", "query": "What are the tags associated with the instrument?", "mandatory": True},
    {"name": "comment", "query": "#tags comments :field:value: e.g. #SOP_v1"},
    {"name": "vendor", "query": "Who is the vendor?"}
  ]}}
}

defaultOntologyNode: dict[str, list[dict[str, str]]] = {
  "default": [
    {"name": "-name", "query": "What is the file name?"},
    {"name": "-tags"},
    {"name": "comment", "query": "#tags comments remarks :field:value:"},
    {"name": "-type"}
  ]}

defaultConfiguration: dict[str, Any] = {
  "defaultProjectGroup": "research",
  "userID": "$os.getlogin()$",
  "version": 0,
  "tableColumnsMax": 16,
  "qrPrinter": {},
  "extractorDir": "$(Path(__file__).parent/'Extractors').as_posix()$",
  "extractors": {},
  "authors": [{"first": "", "last": "", "title": "", "email": "", "orcid": "",
               "organizations": [{"organization": "", "rorid": ""}]}],
  "GUI": {},
  "projectGroups": {}
}

# level 1: type of property
#   within each: array of 3: description, default, all_choices
configurationGUI: dict[str, Any] = {
  "general": {
    "theme": ["Theme",
              "light_blue",
              ["dark_amber", "dark_blue", "dark_cyan", "dark_lightgreen", "dark_pink", "dark_purple", "dark_red", \
               "dark_teal", "dark_yellow", "light_amber", "light_blue", "light_cyan", "light_cyan_500",
               "light_lightgreen", \
               "light_pink", "light_purple", "light_red", "light_teal", "light_yellow", "none"]],
    "loggingLevel": ["Logging level (more->less)", "INFO", ["DEBUG", "INFO", "WARNING", "ERROR"]],
  },
  "dimensions": {
    "sidebarWidth": ["Sidebar width", 280, [220, 280, 340]],
    "maxTableColumnWidth": ["Maximum column width in tables", 400, [300, 400, 500, 600]],
    "imageSizeDetails": ["Image size in details view and form", 600, [300, 400, 500, 600]],
    "imageWidthProject": ["Image width in project view", 300, [200, 250, 300, 350, 400]],
    "maxProjectLeafHeight": ["Maximum height of item in project view", 250, [200, 250, 300, 400]],
    "widthContent": ["Width of procedures in project view", 600, [400, 500, 600, 700]],
    "docTypeOffset": ["Offset of document type in project view", 500, [400, 500, 600, 700]],
    "frameSize": ["Frame width around items in project view", 6, [4, 6, 8, 10]],
  }
}

setupTextLinux = """
### Welcome to the PASTA-ELN setup for Linux
Three components are needed for proper functioning of PASTA-ELN:
- CouchDB
- Configuration of preferences / default ontology
- Example project creation

This setup will analyse and (possibly) correct these items.

If the installation is successful, manually and permanently remove the 'pastaELN.log' logfile that is in your home-directory.
"""

setupTextWindows = """
### Welcome to the PASTA-ELN setup for Windows
Four components are needed for proper functioning of PASTA-ELN:
- CouchDB
- Configuration of preferences / default ontology
- Shortcut creation
- Example project creation

This setup will analyse and (possibly) correct these items.

If the installation is successful, manually and permanently remove the 'pastaELN.log' logfile that is in your home-directory (folder above "My Documents").

If an attempt fails: please follow to this [website](https://pasta-eln.github.io/pasta-eln/install.html).
"""

gitWindows = """
Do you want to install git?

Be aware, downloading the installer requires some time, depending on the internet connection.
"""

rootInstallLinux = """
Do you want to install Apache CouchDB (TM)?
If you choose yes, you will be first asked to

- choose a directory to store the data
- enter the super-user password in the new terminal that will open automatically

Be aware that downloading the installer requires time, depending on the internet connection.
"""

couchDBWindows = """
Do you want to install CouchDB?

Be aware that downloading the installer requires time, depending on the internet connection.
"""

restartPastaWindows = """
Close software now (will be done automatically in the future)

Please restart the software by
- clicking on the shortcut OR
- executing the command in a new cmd.exe window
"""

exampleDataLinux = """
Do you want to create an example project?

This step helps to verify the installation and provides an helpful example for new users.

!WARNING! This process will RESET everything and thereby DELETE EVERYTHING since you installed pastaELN.

This step usually takes up to 20sec, so please be patient. Sometimes, Linux mentions that the program
is not responding and asks if to close/wait. Please WAIT.
"""

exampleDataWindows = """
Do you want to create an example project?

This step helps to verify the installation and provides an helpful example for new users.

!WARNING! This process will RESET everything and thereby DELETE EVERYTHING since you installed pastaELN.

This step usually takes up to 1min, so please be patient.
"""

shortcuts = """
Ctrl+Space: List projects
Ctrl+M: List measurements
Ctrl+S: List samples
Ctrl+P: List procedures
Ctrl+I: List instruments
Ctrl+T: List tags
Ctrl+U: List unidentified
F2: Test file extraction
F5: Synchronize
F9: Restart
Ctrl+?: Verify database integrity
Ctrl+0: Configuration
"""

tableHeaderHelp = """
<h4>You can add custom rows via bottom text area.</h4>

If you want to add a column:
<ul>
<li> for a normal data-field (comment, content, name, type, tags, user, date), enter this field : 'comment'
<li> to check the existence of an image: enter 'image'
<li> to check if a tag is present: "#tag", in which you replace "tag" by the tag you want to look for. "_curated" is a special tag for measurements.
<li> for information inside the metadata, use a "/": e.g. "metaVendor/fileExtension", "metaUser/stress". Capitalization is important.
</ul>
"""
