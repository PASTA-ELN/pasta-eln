Welcome to DataLad Gooey's documentation!
*****************************************

DataLad Gooey is a Graphical User Interface (GUI) for using `DataLad`_,
a free and open source distributed data management tool. DataLad Gooey
is compatible with all major operating systems and allows access to 
DataLad's operations via both a simplified and complete suite.

.. image:: _static/screenshots-gin/created.png

While using DataLad Gooey assumes at least some familiarity with DataLad concepts, the simplified command suite makes starting with DataLad easier via tailor-made command selections, condensed parameter specifications, and tool tips.
The current core functionality supported via the simplified suite includes:

* `cloning`_ a dataset
* `creating`_ a dataset
* creating a sibling (`GIN`_, `GitHub`_, `WebDAV`_)
* `dropping`_/`getting`_ content
* `pushing`_ data/updates to a sibling
* `saving`_ the state of a dataset
* `updating`_ from a sibling

In addition, DataLad Gooey adds support for querying and setting :ref:`credentials <credentials>`, :ref:`git-annex metadata <annexmeta>`, and :ref:`general metadata <metadata>`.

What DataLad Gooey is not
=========================
DataLad Gooey has a number of cool features, but here are features that you will need to use other tools for:

* An interface to visualize revision histories of DataLad datasets. Please refer to many of the available visual Git visualization tools
* An interface for advanced Git operations such as branching, resetting, reverting, or otherwise interacting with commit history. Please refer to your favourite Git client or the command line for these operations. DataLad Gooey will detect such external operations, and will update its view accordingly.

Overview
========

.. toctree::
   :maxdepth: 1

   installation
   getting-started
   datalad-concepts
   gin
   credentials
   annexmetadata
   metadata

Commands and API
================

.. toctree::
   :maxdepth: 2

   cmdline
   modref

.. |---| unicode:: U+02014 .. em dash

.. _DataLad: https://www.datalad.org/
.. _cloning: http://docs.datalad.org/en/stable/generated/man/datalad-clone.html
.. _creating: http://docs.datalad.org/en/stable/generated/man/datalad-create.html
.. _GitLab: http://docs.datalad.org/en/stable/generated/man/datalad-create-sibling-gitlab.html
.. _GIN: http://docs.datalad.org/en/stable/generated/man/datalad-create-sibling-gin.html
.. _GitHub: http://docs.datalad.org/en/stable/generated/man/datalad-create-sibling-github.html
.. _WebDAV: http://docs.datalad.org/projects/next/en/latest/generated/man/datalad-create-sibling-webdav.html
.. _dropping: http://docs.datalad.org/en/stable/generated/man/datalad-drop.html
.. _getting: http://docs.datalad.org/en/stable/generated/man/datalad-get.html
.. _pushing: http://docs.datalad.org/en/stable/generated/man/datalad-push.html
.. _saving: http://docs.datalad.org/en/stable/generated/man/datalad-save.html
.. _updating: http://docs.datalad.org/en/stable/generated/man/datalad-update.html
