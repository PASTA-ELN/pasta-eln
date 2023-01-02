.. _install:

Installation and Troubleshoot Instructions
******************************************

Requirements
============

Install python on windows
-------------------------

If you do not have Python installed, we recommend the default python installation without conda environments. Please go to
https://www.python.org/downloads/windows/
and download "Windows installer" for your architecture, likely 64-bit. In the installer, click "Add python.exe to PATH" at the bottom of the screen, and click "Install Now".
Afterwards, we recommend that you install some nice-to-have packages by using the command line tool CMD.exe:

.. code-block:: bash

    pip install matplotlib pandas spyder

If you want to test the python installation, use the following line in the command line tool CMD.exe:

.. code-block:: bash

    python.exe -c "import numpy as np;x = np.linspace(0,2*np.pi);y = np.sin(x);import matplotlib.pyplot as plt;plt.plot(x,y);plt.show()"

Install PASTA-ELN on all operating systems
==========================================

.. code-block:: bash

    pip install pasta-eln

Afterwards, start PASTA-ELN with

.. code-block:: bash

    pastaELN

which starts automatically the **setup** if no valid PASTA-ELN configuration is found.

If, for whatever reason, the graphical interface does not open, one can also execute
.. code-block:: bash

    pastaELN_Install

to determine the status. To start the setup of the requirements, execute
.. code-block:: bash

    pastaELN_Install install

**ONLY DO THE NEXT STEP WHEN YOU SETUP PASTA-ELN.** Finally, to create the example dataset, execute
.. code-block:: bash

    pastaELN_Install example

Afterwards, the normal 'pastaELN' command should work.


Setup of PASTA-ELN on Windows
-----------------------------

CouchDB installation
^^^^^^^^^^^^^^^^^^^^
To install couchDB, execute the following step in its setup-assistent:

1. -> Next
2. Accept License -> Next
3. -> Next
4. enter UserName (e.g. admin) and password and click "Validate Credentials" -> Next
5. -> Install
6. ... wait ...
7. -> Finish



