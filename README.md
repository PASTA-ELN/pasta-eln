# PASTA-ELN | The favorite ELN for experimental scientists
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-12-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![Build status](https://ci.appveyor.com/api/projects/status/g9von5wtpoidcecy/branch/main?svg=true)](https://ci.appveyor.com/project/mih/datalad-gooey/branch/main)
[![codecov.io](https://codecov.io/github/datalad/datalad-gooey/coverage.svg?branch=main)](https://codecov.io/github/datalad/datalad-gooey?branch=main)
[![crippled-filesystems](https://github.com/datalad/datalad-gooey/workflows/crippled-filesystems/badge.svg)](https://github.com/datalad/datalad-gooey/actions?query=workflow%3Acrippled-filesystems)
[![docs](https://github.com/datalad/datalad-gooey/workflows/docs/badge.svg)](https://github.com/datalad/datalad-gooey/actions?query=workflow%3Adocs)
[![Documentation Status](https://readthedocs.org/projects/datalad-gooey/badge/?version=latest)](http://docs.datalad.org/projects/gooey/en/latest/?badge=latest)
[![GitHub release](https://img.shields.io/github/release/datalad/datalad-gooey.svg)](https://GitHub.com/datalad/datalad-gooey/releases/)
[![PyPI version fury.io](https://badge.fury.io/py/datalad-gooey.svg)](https://pypi.python.org/pypi/datalad-gooey/)

## Table of contents
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

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://psychoinformatics.de"><img src="https://avatars.githubusercontent.com/u/136479?v=4?s=100" width="100px;" alt="Michael Hanke"/><br /><sub><b>Michael Hanke</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=mih" title="Code">💻</a> <a href="#ideas-mih" title="Ideas, Planning, & Feedback">🤔</a> <a href="#projectManagement-mih" title="Project Management">📆</a> <a href="#mentoring-mih" title="Mentoring">🧑‍🏫</a></td>
      <td align="center" valign="top" width="14.28%"><a href="www.onerussian.com"><img src="https://avatars.githubusercontent.com/u/39889?v=4?s=100" width="100px;" alt="Yaroslav Halchenko"/><br /><sub><b>Yaroslav Halchenko</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=yarikoptic" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/effigies"><img src="https://avatars.githubusercontent.com/u/83442?v=4?s=100" width="100px;" alt="Chris Markiewicz"/><br /><sub><b>Chris Markiewicz</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=effigies" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="www.adina-wagner.com"><img src="https://avatars.githubusercontent.com/u/29738718?v=4?s=100" width="100px;" alt="Adina Wagner"/><br /><sub><b>Adina Wagner</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=adswa" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jwodder"><img src="https://avatars.githubusercontent.com/u/98207?v=4?s=100" width="100px;" alt="John T. Wodder II"/><br /><sub><b>John T. Wodder II</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=jwodder" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/bpoldrack"><img src="https://avatars.githubusercontent.com/u/10498301?v=4?s=100" width="100px;" alt="Benjamin Poldrack"/><br /><sub><b>Benjamin Poldrack</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=bpoldrack" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://jsheunis.github.io/"><img src="https://avatars.githubusercontent.com/u/10141237?v=4?s=100" width="100px;" alt="Stephan Heunis"/><br /><sub><b>Stephan Heunis</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=jsheunis" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="mslw.github.io"><img src="https://avatars.githubusercontent.com/u/11985212?v=4?s=100" width="100px;" alt="Michał Szczepanik"/><br /><sub><b>Michał Szczepanik</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=mslw" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/aqw"><img src="https://avatars.githubusercontent.com/u/765557?v=4?s=100" width="100px;" alt="Alex Waite"/><br /><sub><b>Alex Waite</b></sub></a><br /><a href="#userTesting-aqw" title="User Testing">📓</a> <a href="#ideas-aqw" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="manukapp.itch.io"><img src="https://avatars.githubusercontent.com/u/86295664?v=4?s=100" width="100px;" alt="Leonardo Muller-Rodriguez"/><br /><sub><b>Leonardo Muller-Rodriguez</b></sub></a><br /><a href="#userTesting-Manukapp" title="User Testing">📓</a> <a href="https://github.com/datalad/datalad-gooey/commits?author=Manukapp" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/loj"><img src="https://avatars.githubusercontent.com/u/15157717?v=4?s=100" width="100px;" alt="Laura Waite"/><br /><sub><b>Laura Waite</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=loj" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/christian-monch"><img src="https://avatars.githubusercontent.com/u/17925232?v=4?s=100" width="100px;" alt="Christian Mönch"/><br /><sub><b>Christian Mönch</b></sub></a><br /><a href="https://github.com/datalad/datalad-gooey/commits?author=christian-monch" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
