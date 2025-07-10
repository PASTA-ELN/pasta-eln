.. _developCode:

Guides for developers
=====================

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Guides for developers</h2>
      </div>
   </div>

**Overview**: We provide guidelines for developers modifying PASTA-ELN code, including instructions on writing Python test scripts for backend and frontend components like widgets and dialogs. It also covers essential development practices such as code profiling, debugging on Linux using pudb, running pytest, and notes on documentation and general coding.


Notes for Documentation Developers
-----------------------------------

When updating the documentation, ensure it is professional and concise. Use tools like GitHub Copilot to assist in refining the text.
"Can you make the markdown text professional and concise?"


How to write code
-----------------

How to write small python programs that test code directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Backend**

.. code-block:: python

   from pasta_eln.backend import Pasta
   pasta = Pasta()
   viewProj = pasta.db.getView('viewDocType/x0')
   projID1  = [i['id'] for i in viewProj if 'PASTA' in i['value'][0]][0]
   pasta.changeHierarchy(projID1)
   print(pasta.outputHierarchy())


**Frontend: widgets**: For testing widgets put this code into "pasta_eln/test.py":

.. code-block:: python

   from PySide6.QtWidgets import QApplication, QMainWindow
   from .backend import Backend
   from .communicate import Communicate
   from .widgetDetails import Details

   class MainWindow(QMainWindow):
     def __init__(self):
       super().__init__()
       self.backend = Backend()
       comm = Communicate(self.backend)
       widget = Details(comm)
       self.setCentralWidget(widget)
       comm.changeDetails.emit('m-a23019163b9c4fccb4edaab0feb2b5ee')

   app = QApplication()
   window = MainWindow()
   window.show()
   app.exec()

and execute "python -m pasta_eln.test"

**Frontend: dialogs**: For testing dialogs put this code into "pasta_eln/test.py":

.. code-block:: python

   import sys
   from PySide6.QtWidgets import QApplication
   from .GUI.form import Form
   from .backend import Backend
   from .guiCommunicate import Communicate
   from .GUI.palette import Palette

   app = QApplication(sys.argv)
   backend = Backend()
   palette = Palette(app,'none')
   comm = Communicate(backend,palette)
   doc = backend.db.getDoc("m-3a43570c4fd84b1ab81a8863ae058fb0")
   dialog = Form(comm, doc)
   dialog.show()
   sys.exit(app.exec())

and execute "python -m pasta_eln.test"


----


Profiling
^^^^^^^^^

Begin...

.. code-block:: python

   from cProfile import Profile
   from pstats import SortKey, Stats
   with Profile() as profile:

End...

.. code-block:: python

   (Stats(profile).strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(100)) #end cProfile

For example: to profile the start of the program

.. code-block:: python

   def startMain() -> None:
     """
     Main function to start GUI. Extra function is required to allow starting in module fashion
     """
     from cProfile import Profile
     from pstats import SortKey, Stats
     with Profile() as profile:
       app, window = mainGUI()
       window.show()
     (Stats(profile).strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(100)) #end cProfile
     # if app:
     #   app.exec()


Debugging on a conventional install: linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- 'sudo apt install python3-pudb' (not pip install)
- create small 'temp.py' into any folder, with this content:

  .. code-block:: python
     :caption: temp.py

     from pasta_eln.gui import startMain
     startMain()

- start with 'pudb3 temp.py'


Running pytests (python 3.12)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- python3 -m tests.test_01_3Projects


General notes
^^^^^^^^^^^^^

- Find qt-awesome icons: qta-browser
- print works great in frontend and backend
- vulture: vulture pasta_eln --exclude "markdown2html.py,html2markdown.py,minisign.py,html2mdUtils.py,html2mdConfig.py,html2mdElements.py,minisign/helpers.py,printer.py,workplan.py"
