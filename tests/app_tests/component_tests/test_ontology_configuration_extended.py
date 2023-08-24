#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: test_ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import json
import os

import pytest
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication
from pytestqt.exceptions import capture_exceptions
from pytestqt.qtbot import QtBot

import tests
from pasta_eln.ontology_configuration.ontology_configuration_extended import get_gui, OntologyConfigurationForm
from pasta_eln.ontology_configuration.utility_functions import get_db
from tests.app_tests.common.test_utils import dump_object_as_json


@pytest.fixture(scope="module")
def qtbot_session(qt_app, request):
  print("Setting up QTBOT.....")
  result = QtBot(qt_app)
  with capture_exceptions():
    yield result
  print("Tearing down QTBOT.....")


@pytest.fixture(scope="module")
def gui(request) -> tuple[QApplication | QApplication, QtWidgets.QDialog, OntologyConfigurationForm, QtBot]:
  print("Setting up GUI...")
  db = get_db("research", "admin", "DxiBfYvdMOZF", 'http://127.0.0.1:5984')
  dump_object_as_json(db['-ontology-'], 'ontology_document.json')
  app, ui_dialog, ui_form_extended = get_gui(db['-ontology-'])
  qtbot: QtBot = QtBot(app)
  return app, ui_dialog, ui_form_extended, qtbot


def test_form_launch(gui: tuple[QApplication | QApplication, QtWidgets.QDialog, OntologyConfigurationForm, QtBot]):
  """
      Args:
  """
  app, ui_dialog, ui_form, qtbot = gui
  assert ui_form.headerLabel is not None, "Header not loaded!"
  assert ui_form.typeLabel is not None, "Data type label not loaded!"
  assert ui_form.loadOntologyPushButton is not None, "Bush button not loaded!"
  assert ui_form.saveOntologyPushButton is not None, "Save button not loaded!"
  assert ui_form.helpPushButton is not None, "Help button not loaded!"
  assert ui_form.cancelPushButton is not None, "Cancel button not loaded!"
  assert ui_form.typePropsTableView is not None, "Properties table view not loaded!"
  assert ui_form.typeAttachmentsTableView is not None, "Type table view not loaded!"
  assert ui_form.addAttachmentPushButton is not None, "Add attachment button not loaded!"
  assert ui_form.addTypePushButton is not None, "Add type button not loaded!"
  assert ui_form.addPropsRowPushButton is not None, "Add property row button not loaded!"
  assert ui_form.addPropsCategoryPushButton is not None, "Add property category button not loaded!"
  assert ui_form.typeLabelLineEdit is not None, "Data type line edit not loaded!"
  assert ui_form.typeLinkLineEdit is not None, "Data type link line edit not loaded!"
  assert ui_form.addPropsCategoryLineEdit is not None, "Property category line edit not loaded!"
  assert ui_form.typeComboBox is not None, "Data type combo box not loaded!"
  assert ui_form.propsCategoryComboBox is not None, "Property category combo box not loaded!"
