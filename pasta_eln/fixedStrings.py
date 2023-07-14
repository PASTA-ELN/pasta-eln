""" Long strings that would obfuscate code """
import json

defaultOntology = json.loads("""
{
  "_id":"-ontology-",
  "-version":2,

  "x0": {"link":"", "label":"Projects", "prop":[
    {"name":"-name",    "query":"What is the name of the project?"},
    {"name":"status",   "query":"What is the project status", "list":["active","paused","passive","finished"]},
    {"name":"objective","query":"What is the objective?"},
    {"name":"-tags"},
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
    {"name":"-tags"},
    {"name":"comment",    "query":"#tags comments remarks :field:value:"},
    {"name":"-type"},
    {"name":"image"},
    {"name":"#_curated"},
    {"name":"sample",     "query":"Which sample was used?",     "list":"sample"},
    {"name":"procedure",  "query":"Which procedure was used?",  "list":"procedure"}
  ]},
  "sample": {"link":"", "label":"Samples", "prop":[
    {"name":"-name",       "query":"What is the name / identifier of the sample?"},
    {"name":"chemistry",  "query":"What is its chemical composition?"},
    {"name":"-tags"},
    {"name":"comment",    "query":"#tags comments remarks :field:value:"},
    {"name":"qrCode"}
  ]},
  "procedure": {"link":"", "label":"Procedures", "prop":[
    {"name":"-name",       "query":"What is the name / path?"},
    {"name":"-tags"},
    {"name":"comment",    "query":"#tags comments :field:value: e.g. #SOP_v1"},
    {"name":"content",    "query":"What is procedure (Markdown possible; autofilled if file given)?"}
  ]},
  "instrument": {"link":"", "label":"Instruments", "prop":[
    {"name":"-name",       "query":"What is the name / path?"},
    {"name":"comment",    "query":"#tags comments :field:value: e.g. #SOP_v1"},
    {"name":"vendor",     "query":"Who is the vendor?"}
  ]}
}
""")

defaultOntologyNode = json.loads("""
  [{"name": "-name", "query": "What is the file name?"},
   {"name": "-tags"},
   {"name": "comment", "query": "#tags comments remarks :field:value:"},
   {"name": "-type"}]
""")


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
Ctrl+.: Configuration
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