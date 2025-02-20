.. _install:

Installation and Troubleshooting Instructions
=============================================

Windows Installation
--------------------

Using Default Python
^^^^^^^^^^^^^^^^^^^^

We recommend to use the default Python installer:

1. Visit the Python website at https://www.python.org/downloads/windows/ and download the Windows installer for your architecture (likely 64-bit).
2. Run the installer and select the option to "Add python.exe to PATH".
3. Click "Install Now" to complete the installation.
4. Open the Command Prompt (cmd) and execute the following commands:

    .. code-block:: bash

       pip install pasta-eln
       python -m pasta_eln.gui


**Recommendation:** We recommend installing additional packages such as `matplotlib`, `pandas`, and `spyder` to enhance your Python environment. To test your installation, open the Command Prompt and execute the following commands:

.. code-block:: bash

    pip install matplotlib pandas spyder
    python -c "import numpy as np;x = np.linspace(0,2*np.pi);y = np.sin(x);import matplotlib.pyplot as plt;plt.plot(x,y);plt.show()"


Using Anaconda
^^^^^^^^^^^^^^

We recommend **against** using Anaconda as its license agreements prohibit its free use for anything else than education. Much work in universities and research institutions is carried out as funded third-party research that is not covered by the free Anaconda license. We give the Anaconda instructions here for those users that only use Python in an educational framework or that know about the exceptions from this short paragraph.

1. Visit the Anaconda website at https://www.anaconda.com/download and download the installer.
2. Run the installer and accept the default installation settings.
3. Create a new environment named "PASTA-ELN" and select the Python 3.11 option.
4. Click the "New" button to open the terminal and execute the following commands:

    .. code-block:: bash

      pip install pasta-eln
      python -m pasta_eln.gui


Linux Installation
------------------

1. Open the terminal and create a new folder to hold all your PASTA related information

    .. code-block:: bash

        mkdir ~/PASTA

2. Create a new virtual environment with the name `venvPasta`.

    .. code-block:: bash

        python3 -m venv ~/PASTA/venvPasta

3. Activate the virtual environment by running

    .. code-block:: bash

        source ~/PASTA/venvPastabin/activate

4. Install PASTA-ELN by executing

    .. code-block:: bash

        pip install pasta-eln

5. Run the PASTA-ELN graphical interface by executing

    .. code-block:: bash

        python3 -m pasta_eln.gui

5. When prompted for data, we suggest to put your data inside a new **DATA** folder inside the Pasta folder you just created.





Troubleshooting
---------------

If the graphical interface does not open, you can execute the following command to determine the status:

.. code-block:: bash

    python -m pasta_eln.installationTools

To start the setup of the requirements, execute:

.. code-block:: bash

    python -m pasta_eln.installationTools install

**Important:** Only execute the next step when setting up PASTA-ELN for the first time. To create the example dataset, execute:

.. code-block:: bash

    python -m pasta_eln.installationTools example

Afterwards, the normal 'pastaELN' command should work, and a desktop icon should be present.
