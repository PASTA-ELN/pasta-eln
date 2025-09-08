"""example add-on: create a report from within the project view

THIS IS A VERY ADVANCED ADD-ON TUTORIAL
This tutorial teaches
- the basic structure of project-view-add-ons (header, function for each node, body, footer)
- this add-on runs as part of the frontend worker (show a GUI element)
  -  to get the data one has to use the signal system to communicate to the backend worker
- the data collection works as part of this system
  - define a variable to store the data
  - define a function to fill the data
  - say that this function should be used whenever new data arrives
  - request new data
  - do a while loop until all data is here: wait
"""
import base64
import re
from io import BytesIO
from anytree import PreOrderIter
from PIL import Image
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QTextDocument  # This is used for html-markdown conversion: works fine here
import pasta_eln
from pasta_eln.Resources import Icons as icons
from pasta_eln.textTools.stringChanges import markdownEqualizer

# The following two variables are mandatory
description  = 'Sort children'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}

def main(backend, hierStack, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        backend (backend): backend
        hierStack (list): node in hierarchy to start the creation
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        bool: success
    """
    res = QMessageBox.question(widget, 'Sort direction', 'Sort direct children in ascending order? '
                               'If you click no, sort in descending order.',
            buttons=QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel),
            defaultButton=QMessageBox.StandardButton.Yes)
    if res == QMessageBox.StandardButton.Cancel:
        return False
    ascendingFlag = res == QMessageBox.StandardButton.Yes
    # possibly
    hierarchy, _ = backend.db.getHierarchy(hierStack.split('/')[0])

    # main function that calls the render function


    return True
