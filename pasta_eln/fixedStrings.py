defaultOntology = """
{
  "_id":"-ontology-",

  "x0": [
    {"name":"-name",     "query":"What is the project's name?"},
    {"name":"status",   "query":"What is the project status", "list":["active","paused","passive","finished"]},
    {"name":"objective","query":"What is the objective?"},
    {"name":"tags"},
    {"name":"comment",  "query":"#tags comments remarks :field:value:"}
  ],
  "x1": [
    {"name":"-name",     "query":"What is the name of task?"},
    {"name":"comment",  "query":"#tags comments remarks :field:value:"}
  ],
  "x2": [
    {"name":"-name",     "query":"What is the name of subtask?"},
    {"name":"comment",  "query":"#tags comments remarks :field:value:"}
  ],

  "measurement": [
    {"name":"-name",       "query":"What is the file name?"},
    {"name":"tags"},
    {"name":"comment",    "query":"#tags comments remarks :field:value:"},
    {"name":"-type"},
    {"name":"image"},
    {"name":"-curated"},
    {"name":"sample",     "query":"Which sample was used?",     "list":"sample"},
    {"name":"procedure",  "query":"Which procedure was used?",  "list":"procedure"}
  ],
  "sample": [
    {"name":"-name",       "query":"What is the name / identifier of the sample?"},
    {"name":"chemistry",  "query":"What is its chemical composition?"},
    {"name":"tags"},
    {"name":"comment",    "query":"#tags comments remarks :field:value:"},
    {"name":"qrCode"}
  ],
  "procedure": [
    {"name":"-name",       "query":"What is the name / path?"},
    {"name":"tags"},
    {"name":"comment",    "query":"#tags comments :field:value: e.g. #SOP_v1"},
    {"name":"content",    "query":"What is procedure (Markdown possible; autofilled if file given)?"}
  ],
  "instrument": [
    {"name":"-name",       "query":"What is the name / path?"},
    {"name":"comment",    "query":"#tags comments :field:value: e.g. #SOP_v1"},
    {"name":"vendor",     "query":"Who is the vendor?"},
  ]
}
"""

configurationOverview = """
## Overview
###  Setup: Setup and troubleshoot PASTA-ELN installation
### Project group: configure how project groups are saved
### Ontology: configure the data structure for current project group
### Miscellaneous: different things like look-and-feel
"""