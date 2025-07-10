.. _install:

Installation and Troubleshooting Instructions
=============================================

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Installation Instructions and Troubleshooting</h2>
      </div>
   </div>

**Overview**: Install Pasta-ELN on :ref:`Windows <windows_installation>`, :ref:`Linux <linux_installation>`, and :ref:`MacOS <macOS_installation>`. :ref:`Troubleshooting <troubleshooting>` tips are provided at the end.

.. _windows_installation:

Windows Installation
--------------------

.. raw:: html

   <div class="text-highlight">

Automatic Installation
^^^^^^^^^^^^^^^^^^^^^^

.. raw:: html

   Download <a href="https://raw.githubusercontent.com/PASTA-ELN/pasta-eln/refs/heads/main/docs/source/_static/InstallPastaELN.bat">
   Installation batch script</a> and execute it
   </div>


Manual Installation
^^^^^^^^^^^^^^^^^^^
1. Download Python: https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe.
2. Run the installer and select **"Add python.exe to PATH"**.
3. Click **"Install Now"**.
4. Open Command Prompt (cmd) and copy-paste following content:

.. code-block:: bash

   pip install pasta-eln
   python -m pasta_eln.installationTools install "%UserProfile%\Documents\PASTA_ELN_DATA"
   python -m pasta_eln.installationTools shortcut
   python -m pasta_eln.installationTools example
   python -m pasta_eln.gui

**Recommendation**: Install additional packages for enhanced functionality and test python installation:

.. code-block:: bash

    pip install matplotlib pandas spyder
    python -c "import numpy as np; x = np.linspace(0, 2*np.pi); y = np.sin(x); import matplotlib.pyplot as plt; plt.plot(x, y); plt.show()"

**Using Anaconda**: Not recommended due to licensing restrictions. For educational use:

1. Download Anaconda: https://www.anaconda.com/download.
2. Install with default settings.
3. Create a new environment with Python 3.11.
4. Copy-Paste following content:

    .. code-block:: bash

      pip install pasta-eln
      python -m pasta_eln.gui

.. _linux_installation:

Linux Installation
------------------

.. raw:: html

   <div class="text-highlight">

Open terminal and copy-paste following content:

    .. code-block:: bash

        export pastaPath="PASTA_ELN"
        mkdir ~/$pastaPath
        python3 -m venv ~/$pastaPath/venv
        source ~/$pastaPath/venv/bin/activate
        pip install pasta-eln
        python3 -m pasta_eln.installationTools install ~/$pastaPath/data
        python3 -m pasta_eln.installationTools shortcut
        python3 -m pasta_eln.installationTools example
        python3 -m pasta_eln.gui

.. raw:: html

   </div>

**Command Explanation**:

1. Create a folder for PASTA-ELN files.
2. Set up and activate a virtual environment.
3. Install PASTA-ELN.
4. Initialize the data folder.
5. Launch the graphical interface.


.. _macOS_installation:

MacOS Installation
------------------

Requirements
^^^^^^^^^^^^

If not done already, install first Homebrew and then python3 using that

   .. code-block:: bash

      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      brew install python


.. raw:: html

   <div class="text-highlight">

Open terminal and copy-paste following content:

    .. code-block:: bash

        export pastaPath="PASTA_ELN"
        mkdir ~/$pastaPath
        python3 -m venv ~/$pastaPath/venv
        source ~/$pastaPath/venv/bin/activate
        pip install pasta-eln
        python3 -m pasta_eln.installationTools install ~/$pastaPath/data
        python3 -m pasta_eln.installationTools shortcut
        python3 -m pasta_eln.installationTools example
        python3 -m pasta_eln.gui

.. raw:: html

   </div>

**Command Explanation**:

1. Create a folder for PASTA-ELN files.
2. Set up and activate a virtual environment.
3. Install PASTA-ELN.
4. Initialize the data folder.
5. Launch the graphical interface.

.. _troubleshooting:

Troubleshooting Instructions
----------------------------

If large errors occur:

1. Copy terminal output into an email.
2. Attach `pastaELN.log` (found in your home folder or "My Documents" on Windows).
3. Zip the `pastaELN` folder contents.

Send the email with attachments to our support team.

**Error Resolutions**:

1. "ERROR: File on harddisk but not DB": Scan the folder for new data.
2. Deleting Documents: Use the serverActions API or write a script to remove duplicates.

.. raw:: html

   <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
   <span style="float: right"><img src="_static/pasta_logo.svg" alt="logo" style="width: 60px;"/></span>
