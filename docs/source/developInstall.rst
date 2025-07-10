.. _developInstall:


Guides for Testing and Debugging
================================

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Guides for Testing and Debugging</h2>
      </div>
   </div>

**Overview**: This document offers platform-specific instructions for developers working with PASTA-ELN on Windows and Linux. It details how to run the application, manage installation paths, perform reinstallations, create installers on Windows, and set up a Linux development environment using virtual environments.


Notes for Windows Developers
----------------------------

How to start Pasta ELN
^^^^^^^^^^^^^^^^^^^^^^

Anaconda

  - python -m pasta_eln.gui
  - DOES NOT WORK "pastaELN"

Installation location
^^^^^^^^^^^^^^^^^^^^^

Default installation

  - C:\\Users\\...\\AppData\\Local\\Programs\\Python\\Python311\\Scripts
  - C:\\Users\\...\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pasta_eln

Anaconda

  - C:\\Users\\...\\anaconda3\\envs\\...\\Scripts>
  - C:\\Users\\...\\anaconda3\\envs\\...\\Lib\\site-packages\\pasta_eln

Reinstall / retry windows installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- remove directories

  - C:\\Users\\....\\AppData\\Local\\Programs\\Python [If deleted python]
  - Pasta-Folder in Documents

- remove Users\\...\\.pastaELN.json
- remove shortcut on Windows desktop
- **python -m pasta_eln.gui**

Create an installer using pyInstaller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In terminal

  - cd Documents\\PastaELN_src: all files in pasta-eln
  - pyinstaller pastaELN.py -F

File is in /dist/ folder


Notes for Linux Developers
--------------------------

Be sure to have an additional backup of your previous ~/.pastaELN.json

Installation
^^^^^^^^^^^^

.. code-block:: batch

   python -m venv venvPastaTest
   . venvPastaTest/bin/activate
   mv ~/.pastaELN.json ~/.pastaELN.backup.json
   pip install git+https://github.com/PASTA-ELN/pasta-eln@sb_sqlite

Test (you can edit the code in venvPastaTest/lib/python3.12/site-packages/pasta_eln):

.. code-block:: batch

   python -m pasta_eln.gui


.. raw:: html

   <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
   <span style="float: right"><img src="_static/pasta_logo.svg" alt="logo" style="width: 60px;"/></span>
