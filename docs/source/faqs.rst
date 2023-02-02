.. _faqs:

Frequently Asked Questions (FAQ)
********************************

Motivation for PASTA-ELN
========================

*What is the goal of the software?*
    Data has two origins
    - local harddrive where data can be dumped into (freedom to research)
    - links to stored data in a repository
    follows [agile project management](agileProjects.md), which is used in IT-projects
    PASTA is similar to Labfolder(TM), SciNote(TM), etc. only that it is open-source, has two data-sources, etc.

*What do you not want to do?*
    - persistent database of published data. "Dataverse" exists for that goal and does a fabulous job. PASTA is planned to upload to those databases
    - storage for large amounts of raw data: giga-, terra- and peta-bytes. PASTA can link, extract data from that storage
    - conceptional and legal data management database. "Data management plan (DMP)" exists as RDMO on GitHub. PASTA is planned to link to that database

*How is privacy (german Datenschutz) accounted for?*
    The lead designer of PASTA-ELN (as well as many of his immediate colleagues) demand privacy when they use software. PASTA was designed to support privacy on multiple levels.
    - Initially all data and metadata are collected only on the desktop/laptop of the researcher. No data is collected in a central location. Only if the researcher whishes to share the data, it will be uploaded to the database of the research group.
    - Complete decoupling of authorization and authorship (Only, members of a research group are allowed to write to the database (authorization). Who writes each entry can be recorded or not (authorship).)
    - Everybody can select if she/he wants to be identified as author in the database of the research group. If the scientist does not want to be identified, he becomes anonymous (We use a _ for that.) Even another user, or the system administrator cannot identify the author of a entry because that information is not stored.
    - Once the data and meta is shared - as it should be according to the FAIR principles of research - all user identification is removed (even if you choose to be known to your research group) and everybody becomes an anonymous _.
    - This approach relies on the user not entering personal data into any database field, which is therefore discouraged.

*Who is responsible for violations or rules? Who owns the data?*
    The ownership has to be decided by the user and the shareholders (e.g. supervisor) and should take into account cases when user/shareholder changes institution.

Implementation
==============

*Most databases use a web-interface. Why does PASTA not use that?*
    There are many disadvantages to web-interfaces for databases:
    - They are slower than native applications (Nobody writes a thesis on google-docs.)
    - When you update a file on your hard-drive, you have to update it on the database version (The user has to synchronize the files which is an error-prone process.)
    Hence, two versions of each file exist (local and in the cloud) and have to be maintained. We find it better to maintain your version on your hard-disk and let the software synchronize to a server to allow for persistence and collaboration.
    - Most programs that scientists use work well for local files: imageJ, Gwyddion, Origin. Implementing all this functionality into a web-interface is too complicated.

*What are the advantages of web-based and desktop-based software?*
    - Webbased (webforms incl. drag-drop)
        - works independently of operating system
        - works for all screen sizes
        - always updated software
    - Desktop-based
        - faster typing, interaction
        - full control by user and free flow of ideas, thoughts
        - no internet access required
        - no lock-in by software, software-architecture
    - Best version
        - A scientist has a desktop-based version that uploads the data to central servers.
        - Supervisors, guests can use the webbased version to see the meta-data
        - The database can be filled with a command-line-interface (CLI), desktop program or cellphone.
        - Similar to 'git' which is the standard for distributed development.

*Which user interfaces exist?*
    - GUI
    - CLI

*Why is the software for some users fast and for others slow?*
    We are aware of different run-times in different operating system. A backend test has different execution times on Windows (Thinkpad E495: 57.9sec), macOS (Macbook Air 2020: 20.8sec) and Linux (Thinkpad E495: 14.8sec). The graphical user interface seems to work similarly fast on all operating systems. We will investigate how to speed up the backend for Windows users in the future.

*Why dont' you package everything in a flatpak or snap?*
    Containerization is a great concept for many software as it separates the host operating system from the software. This concept is not for PASTA-ELN because we require and want to extend extractors [See ...](extractors.md). As such the user/scientist should be able to change code and require libraries that are not included by default. These libraries cannot be added to the container. Scientist developed extractors cannot be archived in a container which should be self-sufficient and encapsulated. (Also, one could think of creating detours via system-calls / demons on the host system. However, flatpak and snap severely restrict host system-calls and cannot interact with processes on the host system.)
