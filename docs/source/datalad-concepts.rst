.. _glossary:

Central Concepts (Glossary)
---------------------------

Working with DataLad is easier if you know a few technical terms that are regularly referred to in the documentation and the GUI interface.
This glossary provides short definitions, and links relevant additional documentation, where available.


.. glossary::

   annex
      :term:`git-annex` concept: a different word for the internal location in a dataset that :term:`annexed-file`'s are version controlled in.

   annexed-file
      Files managed by :term:`git-annex` are annotated as "annexed-file". Annexed files have access to additional commands in their context menus such as :term:`get` and :term:`drop`.

   branch
      Git concept: A lightweight, independent history streak of your dataset. Branches can contain less, more, or changed files compared to other branches, and one can merge the changes a branch contains into another branch. DataLad Gooey only views the currently checked out branch in your dataset, and does not support Git commands that expose branching functionality.

   clone
      The `datalad clone <http://docs.datalad.org/en/stable/generated/man/datalad-clone.html>`_ command retrieves a copy of a :term:`Git` repository or :term:`DataLad dataset` from a local or remote path or URL. In Git-terminology, all "installed" datasets
      are clones.

   commit
      Git concept: Adding selected changes of a file or dataset to the repository, and thus making these changes
      part of the revision history of the repository. The `datalad save <http://docs.datalad.org/en/stable/generated/man/datalad-save.html>`_ command creates a commit in the selected dataset. Commits should always have an informative :term:`commit message`.

   commit message
      Git concept: A concise summary of changes you should attach to a :command:`datalad save` command. This summary will
      show up in your :term:`DataLad dataset` history.

   DataLad dataset
      A DataLad dataset is a Git repository that may or may not have a data annex that is used to
      manage data referenced in a dataset. In practice, most DataLad datasets will come with an annex.

   DataLad extension
      Python packages that equip DataLad with specialized commands. The section
      `extensions_intro <http://handbook.datalad.org/en/latest/r.html?extensions>_` of the DataLad Handbook gives and overview of available extensions and links
      to Handbook chapters that contain demonstrations.

   DataLad subdataset
      A DataLad dataset contained within a different DataLad dataset (the parent or :term:`DataLad superdataset`).

   DataLad superdataset
      A DataLad dataset that contains one or more levels of other DataLad datasets (:term:`DataLad subdataset`).

   drop
      The `datalad drop <http://docs.datalad.org/en/stable/generated/man/datalad-drop.html>`_ command drops file content of annexed files. It is the antagonist to :term:`get`.

   GIN
      A web-based repository store for data management that you can use to host and share datasets. Find out more about GIN `here <https://gin.g-node.org/G-Node/Info/wiki>`__.

   Git
      A version control system to track changes made to small-sized files over time. You can find out
      more about git in `this (free) book <https://git-scm.com/book/en/v2>`_
      or `these interactive Git tutorials <https://try.github.io/>`_ on :term:`GitHub`.

   git-annex
      A distributed file synchronization system, enabling sharing and synchronizing collections
      of large files. It allows managing files with :term:`Git`, without checking the file content into Git.

   git-annex branch
      A :term:`branch` that exists in your dataset, if the dataset contains an annex. The git-annex branch is completely unconnected to any other branch in your dataset, and contains different types of log files. Its contents are used for git-annex’s internal tracking of the dataset and its annexed contents. DataLad Gooey provides support for adding git annex metadata, but does not otherwise support operations on dataset branches

   GitHub
      GitHub is an online platform where one can store and share version controlled projects
      using Git (and thus also DataLad project). See`GitHub.com <https://github.com/>`_.


   GitLab
      An online platform to host and share software projects version controlled with :term:`Git`,
      similar to :term:`GitHub`. See `Gitlab.com <https://about.gitlab.com/>`_.

   get
      The `datalad get <http://docs.datalad.org/en/stable/generated/man/datalad-get.html>`_ command gets file content of annexed files. It is the antagonist to :term:`drop`.

   https
      Hypertext Transfer Protocol Secure; A protocol for file transfer over a network.

   pip
      A Python package manager. Short for "Pip installs Python". ``pip install <package name>``
      searches the Python package index `PyPi <https://pypi.org/>`_ for a
      package and installs it while resolving any potential dependencies.

   remote
      Git-terminology: A repository (and thus also :term:`DataLad dataset`) that a given repository tracks. A :term:`sibling` is DataLad's equivalent to a remote.

   SSH
      Secure shell (SSH) is a network protocol to link one machine (computer),
      the *client*, to a different local or remote machine, the *server*.


   SSH key
      An SSH key is an access credential in the SSH protocol that can be used to login from one system to remote servers and services, such as from your private computer to an SSH server, without supplying your username or password at each visit.
      To use an SSH key for authentication, you need to generate a key pair on the system you would like to use to access a remote system or service (most likely, your computer).
      The pair consists of a *private* and a *public* key. The public key is shared with the remote server, and the private key is used to authenticate your machine whenever you want to access the remote server or service.
      Services such as :term:`GitHub`, :term:`GitLab`, and :term:`GIN` use SSH keys and the SSH protocol to ease access to repositories.
      This `tutorial by GitHub <https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent>`_ is a detailed step-by-step instruction to generate and use SSH keys for authentication.

   sibling
      DataLad concept: A dataset clone that a given :term:`DataLad dataset` knows about.
      Changes can be retrieved and pushed between a dataset and its sibling.
      It is the equivalent of a :term:`remote` in Git.

   version control
      Processes and tools to keep track of changes to documents or other collections of information.
