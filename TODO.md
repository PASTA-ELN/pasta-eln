# Minimum viable product

# Optimize installation
-  QtPy-2.3.0 (should be installed in the dependency tree)
-  qta-browser
- fixed version number gitannex and datalad

# Cleaning
- reduce self.
- commenting, pylint
- (HT) replace documentation
- rename be. -> backend. or leave be.; don't call it pasta

# Optimize everything
- separate backend.py into CLI
- edit

# General hints
- create a new version: ./commit.py "Minimal viable product" 1
- search for word datalad
- include requirements into setup.cfg
- setup.cfg: pytest



https://www.python.org/downloads/windows/

and download "Windows installer" for your architecture, likely 64-bit
click "Add python.exe to PATH" at the bottom of the screen, and click "Install Now"

``` bash
pip install win-unicode-console pywin32 pywin32-ctypes
pip install matplotlib pandas wget spyder
```


Test if python is fully working: plot a sine-curve
python.exe -c "import numpy as np;x = np.linspace(0,2*np.pi);y = np.sin(x);import matplotlib.pyplot as plt;plt.plot(x,y);plt.show()"


pip install pasta-eln

https://setuptools.pypa.io/en/latest/userguide/dependency_management.html

C:\Users\Steffen\AppData\Local\Programs\Python\Python311\Scripts

C:\Users\Steffen\AppData\Local\Programs\Python\Python311\Lib\site-packages\pasta_eln