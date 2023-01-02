# PASTA-ELN | The favorite ELN for experimental scientists

[![PyPI version](https://badge.fury.io/py/pasta-eln.svg)](https://badge.fury.io/py/pasta-eln)
[![GitHub version](https://badge.fury.io/gh/PASTA-ELN%2Fpasta-eln.svg)](https://badge.fury.io/gh/PASTA-ELN%2Fpasta-eln)
[![PyPi build](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pypi.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pypi.yml)
[![Documentation building](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/docbuild.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/docbuild.yml)
[![Linting](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pylint.yml/badge.svg)](https://github.com/PASTA-ELN/pasta-eln/actions/workflows/pylint.yml)

Users, all the documentation can be found at [Github-pages](https://pasta-eln.github.io/pasta-eln/)

This page / area is for developers and contains some helpful information for them

- Installation location windows:
  - C:\Users\Steffen\AppData\Local\Programs\Python\Python311\Scripts
  - C:\Users\Steffen\AppData\Local\Programs\Python\Python311\Lib\site-packages\pasta_eln
  -

- Run Pasta-ELN directly from commandline without installation
  -  python -m pasta_eln.installationTools

- Hints for developers
  -  qta-browser
## How to create a new version
1. normal commit to test the actions, then do ..
2. create a new version: ./commit.py "Minimal viable product" 1

``` Python
from pasta_eln.backend import Pasta
pasta = Pasta()
viewProj = pasta.db.getView('viewDocType/x0')
projID1  = [i['id'] for i in viewProj if 'PASTA' in i['value'][0]][0]
pasta.changeHierarchy(projID1)
print(pasta.outputHierarchy())
```



# Old stuff
- Installation instructions
  - [Linux/Ubuntu](installLinux.md)
  - [Windows](installWindows.md)
  - [Apple's macOS](installMacOS.md)
- Troubleshooting: [What if errors occur?](troubleshooting.md)
- Suggestions for:
  - [new users](firstUsage.md)
  - [advanced users](notesUser.md)
  - [developes](notesDevelopers.md)

* * *

## Concepts of PASTA electronic lab notebook (ELN)
Pasta-dishes are a mixture pasta and sauce, the latter adds flavors and richness to the otherwise boring pasta. This ELN combines raw-data with rich metadata to allow advanced data science. In the database, one can fully adapt and improvise the metadata definitions to generate something novel. PASTA uses a local-first approach: store all data and metadata locally (always accessible to user) and synchronize with a server upon user request.

Extractors are little python scripts that 'extract' metadata, thumbnails and user-metadata from the raw measurement files. These little programs can be written/adopted by scientists and can be shared. [To read more.... (for advanced users)](extractors.md)

In PASTA, the meta-data is stored in a document database called **CouchDB**. This non-SQL database is very adaptive to the different raw data sources and corresponding different meta-data. [Read more on this CouchDB implementation...(for developers of PASTA)](couchDB.md)

Adaptive software development (scrum) has revolutionized software projects. We believe that **agile project planning** is also highly beneficial for scientific research projects. [To read more... (for all useres)](agileProjects.md)

The raw data is the origin of scientific work and has to follow the FAIR principles to be trusted. PASTA uses **DataLad** for the raw data and simplifies it to the typical use of experimental material scientists. [To read more on the use of dataLad...(for developers)](dataLad.md)

If CouchDB and DataLad are the two legs on which PASTA is built (and agile project planning is its heart), then the **python backend** is its torso, which links everything together. [Read more on the backend...](software.md)

All users will interact with the python backend via **graphical user interfaces (GUI)** that use QT and pyside6. [Read more on the GUI and React implementation...](software.md)

The development of the software started shortly before the Corona-pandemic hit Germany in 2020. The current state is given in [features](features.md)

* * *

## Frequently Asked Questions (FAQ)
### Motivation
- *What is the goal of the software?*
  - Data has two origins
    - local harddrive where data can be dumped into (freedom to research)
    - links to stored data in a repository
  - follow [agile project management](agileProjects.md), which is used in IT-projects
  -   PASTA is similar to Labfolder(TM), SciNote(TM), etc. only that it is open-source, has two data-sources, etc.
- *What do you not want to do?*
  - persistent database of published data. "Dataverse" exists for that goal and does a fabulous job. PASTA is planned to upload to those databases
  - storage for large amounts of raw data: giga-, terra- and peta-bytes. PASTA can link, extract data from that storage
  - conceptional and legal data management database. "Data management plan (DMP)" exists as RDMO on GitHub. PASTA is planned to link to that database
- *How is privacy (german Datenschutz) accounted for?*
  The lead designer of PASTA-ELN (as well as many of his immediate colleagues) demand privacy when they use software. PASTA was designed to support privacy on multiple levels.
  - Initially all data and metadata are collected only on the desktop/laptop of the researcher. No data is collected in a central location. Only if the researcher whishes to share the data, it will be uploaded to the database of the research group.
  - Complete decoupling of authorization and authorship (Only, members of a research group are allowed to write to the database (authorization). Who writes each entry can be recorded or not (authorship).)
  - Everybody can select if she/he wants to be identified as author in the database of the research group. If the scientist does not want to be identified, he becomes anonymous (We use a _ for that.) Even another user, or the system administrator cannot identify the author of a entry because that information is not stored.
  - Once the data and meta is shared - as it should be according to the FAIR principles of research - all user identification is removed (even if you choose to be known to your research group) and everybody becomes an anonymous _.
  - This approach relies on the user not entering personal data into any database field, which is therefore discouraged.
- *Who is responsible for violations or rules? Who owns the data?*
  The ownership has to be decided by the user and the shareholders (e.g. supervisor) and should take into account cases when user/shareholder changes institution.

### Implementation
- *Most databases use a web-interface. Why does PASTA not use that?*
  There are many disadvantages to web-interfaces for databases:
  - They are slower than native applications (Nobody writes a thesis on google-docs.)
  - When you update a file on your hard-drive, you have to update it on the database version (The user has to synchronize the files which is an error-prone process.)
  Hence, two versions of each file exist (local and in the cloud) and have to be maintained. We find it better to maintain your version on your hard-disk and let the software synchronize to a server to allow for persistence and collaboration.
  - Most programs that scientists use work well for local files: imageJ, Gwyddion, Origin. Implementing all this functionality into a web-interface is too complicated.
- *What are the advantages of web-based and desktop-based software?*
  - Webbased (webforms incl. drag-drop)
    + works independently of operating system
    + works for all screen sizes
    + always updated software
  - Desktop-based
    + faster typing, interaction
    + full control by user and free flow of ideas, thoughts
    + no internet access required
    + no lock-in by software, software-architecture
  - Best version
    + A scientist has a desktop-based version that uploads the data to central servers.
    + Supervisors, guests can use the webbased version to see the meta-data
    + The database can be filled with a command-line-interface (CLI), desktop program or cellphone.
    + Similar to 'git' which is the standard for distributed development.
- *Which user interfaces exist?*
  - GUIs
    - reactElectron: allows a GUI on desktop
    - reactNative: allows Android / iPhone interaction
- *Why is the software for some users fast and for others slow?*
  We are aware of different run-times in different operating system. A backend test has different execution times on Windows (Thinkpad E495: 57.9sec), macOS (Macbook Air 2020: 20.8sec) and Linux (Thinkpad E495: 14.8sec). The graphical user interface seems to work similarly fast on all operating systems. We will investigate how to speed up the backend for Windows users in the future.

- *Why dont' you package everything in a flatpak or snap?*
  Containerization is a great concept for many software as it separates the host operating system from the software. This concept is not for PASTA-ELN because we require and want to extend extractors [See ...](extractors.md). As such the user/scientist should be able to change code and require libraries that are not included by default. These libraries cannot be added to the container. Scientist developed extractors cannot be archived in a container which should be self-sufficient and encapsulated. (Also, one could think of creating detours via system-calls / demons on the host system. However, flatpak and snap severely restrict host system-calls and cannot interact with processes on the host system.)
