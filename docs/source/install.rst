.. _install:

Installation and Troubleshoot Instructions
******************************************

WINDOWS
=======

Requirement: install python
---------------------------

If you do not have Python installed, we recommend the default python installation without conda environments.

1. Go to https://www.python.org/downloads/windows/
2. Download "Windows installer" for your architecture, likely 64-bit.
3. In the installer, click "Add python.exe to PATH" at the bottom of the window.
4. Click "Install Now" in the middle of the window
5. Close

Recommendation
^^^^^^^^^^^^^^

Afterwards, we recommend that you install some nice-to-have packages and test these installations by using the command line tool CMD.exe:

.. code-block:: bash

    pip install matplotlib pandas spyder
    python.exe -c "import numpy as np;x = np.linspace(0,2*np.pi);y = np.sin(x);import matplotlib.pyplot as plt;plt.plot(x,y);plt.show()"



LINUX
=====

Requirement: add python packages
--------------------------------

Generally, Python3 is installed in all Linux distributions. Sometimes, the package installer is missing. Hence, install it along with venv:

.. code-block:: bash

    sudo apt install python3-pip python3.10-venv

Install PASTA-ELN
-----------------

You can install PASTA-ELN in your normal user-space, which is the easier path, or inside an environment, which is the safer path. If PASTA-ELN does not work in the normal user-space, install in in an environment.

Install in user-space
^^^^^^^^^^^^^^^^^^^^^
In any folder,

.. code-block:: bash

    pip3 install pasta-eln

which typically can take some time. Afterwards, start PASTA-ELN with

.. code-block:: bash

    pastaELN

which starts automatically the **setup** if no valid PASTA-ELN configuration is found.

Install in environment
^^^^^^^^^^^^^^^^^^^^^^

Starting in a folder of your choice but we suggest the home-folder, create a virtual environment, for instance with the name .venvPasta. (The . will ensure that it is mostly hidden.)

.. code-block:: bash

    python3 -m venv .venvPastaELN
    . .venvPastaELN/bin/activate
    pip3 install pasta-eln
    pastaELN
    deactivate

which typically can take some time and includes the **setup**. Afterwards, you can start pasta with

.. code-block:: bash

    pastaELN

or

.. code-block:: bash

    python -m pasta_eln.gui

Advanced notes if the normal setup did not succeed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If, for whatever reason, the graphical interface does not open, one can also execute

.. code-block:: bash

    pastaELN_Install

to determine the status. To start the setup of the requirements, execute

.. code-block:: bash

    pastaELN_Install install

**ONLY DO THE NEXT STEP WHEN YOU SETUP PASTA-ELN FOR THE FIRST TIME.**

Finally, to create the example dataset, execute

.. code-block:: bash

    pastaELN_Install example

Afterwards, the normal 'pastaELN' command should work and a desktop icon should be present.
