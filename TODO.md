# Priority 1:

# Priority 4: bigger features
- show links to other docs and use
- table: rerun extractors on group

# Priority 5: Don't forget might become useful
- Tests
- have discussion with Georg, KIT
- setup.cfg: pytest
- Windows/Anaconda generally works, use Marble documentation if it fully works. Git/Git-annex/datalad do not work currently
  - Datalad documentation has the following suggestion for git-installation
    - Enable Use a TrueType font in all console windows  (I cannot find)
    - Select Git from the command line and also from 3rd-party software (default on page ~6)
    - Enable file system caching (page 12)
    - Enable symbolic links (page 12)


# Notes
- allow to change docType of undefined types

# Implement in future
- sidebar
  - hover over project, task, ...: on right side folder icon appears: if click: open filemanager in that folder
- table
  - export table as xls
  - rows can be selected individually (shift) or select all: What to do with that
    - one can hide things, change tags, ...
  - search in table
  - change table collumns
- details
  - show tags in boxes, different style
    - if click on tag: show all items with the same tag
- progressbar for scanning tree
- add attachements / issues
- removed items
- Help


# Future features in order of priority
These are notes of features. These notes are there such that we do not forget future directions, responses if someone asks.

## Links of interest
https://github.com/GavinMendelGleason/blog/blob/main/entries/semantic_future.md



## terminate projects and tables-per-project, modifiable tables
  - add search
  - don't show archivedProjects (depending on if you want)
  - tables per project
  - curation: only show samples of this project to ease the selection
  - allow to prioritize projects,
  - print to-dos etc: is that something that is in dataDictionary and entered as text
  - TODO,Paused,DONE into steps

## What is the QR-code: Does it include a human-readable name?
  Yes, in the future

## Allow multi-user and groups
  - entities have a database
  - in entities some users have read/write access
  - a user can be part of different entities
  - a master-database has a list of all entities, users, the databases

## Use ORCID to sign in into PASTA?
  - ORCID has a nice [API](https://members.orcid.org/api/integrate/orcid-sign-in)
  - However, ORCID id only includes identification not the role in the individual Pasta database
  - Therefore, user-information has to exist in database anyhow
  - Moreover, ORCID not work in off-line usage
  - ORCID is no benefit for authentication (since requires database roles anyhow) but could be beneficial for authorship (which should be hidden to protect privacy).

## advanced procedures and compress-content
  - copy content or parts of the content (main points) into the database (similar to getMeasurement)
  - make sure procedure is not updated, no revisioning but versioning
  - versioning of procedures and software links to the current one
  - consider document compression: it is said that CouchDB stores in 4kB chunks so compression might not make sense

## Push to data-fz-juelich
  - interface has to exist
  - package data and then create package document: zip and push to data-fz-juelich

## Cluster measurements
  - select experiments in a tables
  - calculate new measurement group: mean, standard-dev

## "to form" button to convert data into pdf-form for polished reports of experiments
  - use doc and template (.tex, .html)
  - use pandoc to create pdf for download only, no storage
  - allow preparing reports: json->...pandoc -->pdf (only json is stored)

## Pull data from matDB

## easy presentations

## device integration

## word, excel extract data from them

## counter-sign: gegenzeichnen

## labor management system

## bubble up issues
  - can be evaluated after project, sprints,...
  - during the review: mark things that might become important in the future
  - every meeting the bubble up items
  - are shown and addressed: no more bubble-up
  - or posted: bubble-up again
  - important items bubble up every time
  - unimportant items bully up more seldom

## App.js
  - decide on default page: <Route exact path="/" component={AboutPage}/>

## how to include comments of others into doc?
  - is it necessary or the current system enough

