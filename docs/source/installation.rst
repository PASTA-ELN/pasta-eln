Installation
############

Installing via PyPI
-------------------

You can install the latest version of ``datalad-gooey`` from PyPI. It is recommended to
use a dedicated `virtualenv`_:

.. code::

   # Create and enter a new virtual environment (optional)
   python3 -m venv ~/.venvs/datalad-gooey
   source ~/.venvs/datalad-gooey/bin/activate

.. code::

   # Install from PyPI
   pip install datalad_gooey

.. admonition:: Dependencies

   Because this is an extension to ``datalad``, the installation process also installs
   the `datalad`_ Python package, although all recursive dependencies (such as ``git-annex``)
   are not automatically installed. For complete instructions on how to install ``datalad`` 
   and ``git-annex``, please refer to the `DataLad Handbook`_.


Installing on Windows
---------------------

Download and run the `installer`_. Follow the prompts to complete the setup.

The installer comes with ``git`` and ``git-annex`` installers. If you have
``git`` and ``git-annex`` already installed, just quit the ``git`` and
``git-annex`` installers when they are executed.


Installing on Linux
-------------------

Install DataLad Gooey via PyPI while specifying the ``--user`` flag:

.. code::

   pip install --user datalad_gooey

Then run the following line to ensure that the application's desktop
file is generated:

.. code::
   
   datalad gooey --postinstall


Installing on macOS
-------------------

.. admonition:: macOS application pending
   
   Until the macOS application is available to allow standard installation into the
   Applications folder, macOS users can install DataLad Gooey via PyPI.

.. code::

   # Install from PyPI
   pip install datalad_gooey

.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _datalad: https://github.com/datalad/datalad
.. _installer: https://github.com/datalad/datalad-gooey/releases
.. _DataLad Handbook: https://handbook.datalad.org/en/latest/intro/installation.html
