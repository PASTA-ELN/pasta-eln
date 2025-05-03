.. _install:

Installation and Troubleshooting Instructions
=============================================

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Installation instructions and help for Troubleshooting</h2>
      </div>
   </div>

**Overview**: You can install Pasta-ELN on :ref:`Windows <windows_installation>`, :ref:`Linux <linux_installation>` and Mac-Computers. :ref:`Troubleshooting <troubleshooting>` hints are given at the end.


.. _windows_installation:

Windows Installation
--------------------

.. raw:: html

   <div class="text-highlight">

1. Download the current Python installer: https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe.
2. Run the installer and select the option to **"Add python.exe to PATH"** on the first screen.
3. Click **"Install Now"** to complete the installation.
4. Open the Command Prompt (cmd) and copy-paste the following commands:

    .. code-block:: bash

       pip install pasta-eln
       python -m pasta_eln.tools "_ i q" ~/$pastaPath/data
       python -m pasta_eln.gui

.. raw:: html

   </div>

Recommendation
^^^^^^^^^^^^^^
We recommend installing additional packages such as `matplotlib`, `pandas`, and `spyder` to enhance your Python environment. To test your installation, open the Command Prompt and execute the following commands:

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


.. _linux_installation:

Linux Installation
------------------

.. raw:: html

   <div class="text-highlight">

Open the terminal and copy-paste the following commands:

    .. code-block:: bash

        export pastaPath="PASTA_ELN"
        mkdir ~/$pastaPath
        python3 -m venv ~/$pastaPath/venv
        source ~/$pastaPath/venv/bin/activate
        pip install pasta-eln
        python -m pasta_eln.tools "_ i q" ~/$pastaPath/data
        python3 -m pasta_eln.gui

.. raw:: html

   </div>

**Command Explanation**:

1. Create a folder to store all PASTA-ELN-related files.
2. Set up a virtual environment named `venv`.
3. Activate the virtual environment.
4. Install PASTA-ELN.
5. Initialize the PASTA-ELN data folder.
6. Launch the PASTA-ELN graphical interface.

.. _troubleshooting:

Troubleshooting Instructions
----------------------------

If the graphical interface does not open, follow these steps to help diagnose the issue:

1. Copy the terminal output into an email.
2. Attach the `pastaELN.log` file (found in your home folder or above "My Documents" on Windows).
3. Zip the contents of the `pastaELN` folder.

Send the email with the attachments to our support team for assistance.
