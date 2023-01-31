.. _install:

Installation and Troubleshoot Instructions
******************************************

Requirements
============

Install python on windows
-------------------------

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

Install python on linux
-----------------------

Generally, Python3 is installed in all Linux distributions. Sometimes, the package installer is missing. Hence, install it:

.. code-block:: bash

    sudo apt install python3-pip

|

|


Install PASTA-ELN on all operating systems
==========================================

.. code-block:: bash

    pip install pasta-eln

which typically can take some time. Afterwards, start PASTA-ELN with

.. code-block:: bash

    pastaELN

which starts automatically the **setup** if no valid PASTA-ELN configuration is found.

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

Afterwards, the normal 'pastaELN' command should work.


Setup of PASTA-ELN on Windows
-----------------------------

Git for windows
^^^^^^^^^^^^^^^
To install git for windows, execute the following step in its setup-assistent:

1.-14. Next

15. Install

16. Finish

Git-annex for windows
^^^^^^^^^^^^^^^^^^^^^
To install git-annex for windows, execute the following step in its setup-assistent:

1. Next >
2. I Agree
3. Close

CouchDB installation
^^^^^^^^^^^^^^^^^^^^
To install couchDB, execute the following step in its setup-assistent:

1. -> Next
2. Accept License -> Next
3. -> Next
4. enter UserName (e.g. admin) and password and click "Validate Credentials" -> Next
5. -> Install
6. -> Finish
