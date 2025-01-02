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

We recommend **against** using Anaconda as its license agreements prohibit its free use for anything else than education. Much work in universities and research institutions is carried out as funded third-party research that is not covered by the free Anaconda license. We give the Anaconda instructions here for those users that only use Python in an educational framework or that know about the excemptions from this short paragraph.

1. Visit the Anaconda website at https://www.anaconda.com/download and download the installer.
2. Run the installer and accept the default installation settings.
3. Create a new environment named "PASTA-ELN" and select the Python 3.11 option.
4. Click the "New" button to open the terminal and execute the following commands:

    .. code-block:: bash

      pip install pasta-eln
      python -m pasta_eln.gui


Linux Installation
------------------

1. Navigate to a folder of your choice (e.g., your home directory) and create a new virtual environment with the name `.venvPastaELN`.
2. Activate the virtual environment by running `source .venvPastaELN/bin/activate`.
3. Install PASTA-ELN by executing `pip install pasta-eln`.
4. Run the PASTA-ELN graphical interface by executing `python -m pasta_eln.gui`.

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
