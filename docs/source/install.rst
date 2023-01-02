.. _install:

Installation and Troubleshoot Instructions
******************************************

Windows
=======

Install python
--------------

If you do not have Python installed, we recommend the default python installation without conda environments. Please go to
https://www.python.org/downloads/windows/
and download "Windows installer" for your architecture, likely 64-bit. In the installer, click "Add python.exe to PATH" at the bottom of the screen, and click "Install Now".
Afterwards, we recommend that you install some nice-to-have packages by using the command line tool CMD.exe:
``` bash
pip install matplotlib pandas wget spyder
```
If you want to test the python installation, use the following line in the command line tool CMD.exe:
``` bash
python.exe -c "import numpy as np;x = np.linspace(0,2*np.pi);y = np.sin(x);import matplotlib.pyplot as plt;plt.plot(x,y);plt.show()"
```

All systems
===========

pip install pasta-eln


CouchDB installation
--------------------

Couchdb add to GUI only once that is new
Next, Accept_License + Next, Next, UserName + Password + Validate Credentials + Next, Install, ... , Finish



