# How to transfer database from version 1 to version 2
- Move entry in .pasta.json from one file to the other
- update Ontology

# run with ./pastaELN_CLI.py verifyDB

# Change harddrive content
- datalad unlock
- ls -lR . | grep ^l
- sudo rm -rf .datalad/ .git/ .gitattributes .gitignore
- find . -name '*_pasta.jpg' -exec rm {} \;
- find . -name '*_jamDB.jpg' -exec rm {} \;

# Change database
- use commented out code
- ./pastaELN_CLI.py verifyDB

# recreate views
- ./pastaELN_CLI.py test

# V2 Ontology
  "-version": 2,
  "x0": {
    "link": "",
    "label": "Projects",
    "prop": [
      {
        "name": "-name",
        "query": "What is the name of the project?"
      },
      {
        "name": "status",
        "query": "What is the project status",
        "list": [
          "active",
          "paused",
          "passive",
          "finished"
        ]
      },
      {
        "name": "objective",
        "query": "What is the objective?"
      },
      {
        "name": "-tags"
      },
      {
        "name": "comment",
        "query": "#tags comments remarks :field:value:"
      }
    ]
  },
  "x1": {
    "link": "",
    "label": "Tasks",
    "prop": [
      {
        "name": "-name",
        "query": "What is the name of task?"
      },
      {
        "name": "comment",
        "query": "#tags comments remarks :field:value:"
      }
    ]
  },
  "x2": {
    "link": "",
    "label": "Subtasks",
    "prop": [
      {
        "name": "-name",
        "query": "What is the name of subtask?"
      },
      {
        "name": "comment",
        "query": "#tags comments remarks :field:value:"
      }
    ]
  },
  "measurement": {
    "link": "",
    "label": "Measurements",
    "prop": [
      {
        "name": "-name",
        "query": "What is the file name?"
      },
      {
        "name": "-tags"
      },
      {
        "name": "comment",
        "query": "#tags comments remarks :field:value:"
      },
      {
        "name": "-type"
      },
      {
        "name": "image"
      },
      {
        "name": "#_curated"
      },
      {
        "name": "sample",
        "query": "Which sample was used?",
        "list": "sample"
      },
      {
        "name": "procedure",
        "query": "Which procedure was used?",
        "list": "procedure"
      }
    ]
  },
  "sample": {
    "link": "",
    "label": "Samples",
    "prop": [
      {
        "name": "-name",
        "query": "What is the name / identifier of the sample?"
      },
      {
        "name": "chemistry",
        "query": "What is its chemical composition?"
      },
      {
        "name": "-tags"
      },
      {
        "name": "comment",
        "query": "#tags comments remarks :field:value:"
      },
      {
        "name": "qrCode"
      }
    ]
  },
  "procedure": {
    "link": "",
    "label": "Procedures",
    "prop": [
      {
        "name": "-name",
        "query": "What is the name / path?"
      },
      {
        "name": "-tags"
      },
      {
        "name": "comment",
        "query": "#tags comments :field:value: e.g. #SOP_v1"
      },
      {
        "name": "content",
        "query": "What is procedure (Markdown possible; autofilled if file given)?"
      }
    ]
  },
  "instrument": {
    "link": "",
    "label": "Instruments",
    "prop": [
      {
        "name": "-name",
        "query": "What is the name / path?"
      },
      {
        "name": "comment",
        "query": "#tags comments :field:value: e.g. #SOP_v1"
      },
      {
        "name": "vendor",
        "query": "Who is the vendor?"
      }
    ]
  }
}