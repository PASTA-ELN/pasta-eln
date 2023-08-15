#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from pytestqt.exceptions import capture_exceptions
from pytestqt.qtbot import QtBot

from pasta_eln.ontology_configuration.ontology_configuration_extended import get_gui


@pytest.fixture(scope="module")
def qtbot_session(qt_app, request):
  print("Setting up QTBOT.....")
  result = QtBot(qt_app)
  with capture_exceptions():
    yield result
  print("Tearing down QTBOT.....")


@pytest.fixture(scope="module")
def gui(request):
  print("Setting up GUI...")
  app, _, ui = get_gui()
  qtbot: QtBot = QtBot(app)
  return app, ui, qtbot


def test_form_launch(gui: object):
  """
      Args:
  """
  app, ui, qtbot = gui
  assert ui.headerLabel is not None, "Header not loaded!"
  assert ui.dataTypeLabel is not None, "Data type label not loaded!"
  assert ui.loadPushButton is not None, "Bush button not loaded!"
  assert ui.savePushButton is not None, "Save button not loaded!"
  assert ui.helpPushButton is not None, "Help button not loaded!"
  assert ui.cancelPushButton is not None, "Cancel button not loaded!"
  assert ui.structuralPropsTableView is not None, "Table view not loaded!"
  assert ui.addRowPushButton is not None, "Add row button not loaded!"
  assert ui.headingAddpushButton is not None, "Heading Add button not loaded!"
  assert ui.dataTypeLabel is not None, "Data type label not loaded!"
  assert ui.typeComboBox is not None, "Data type combo box not loaded!"
  assert ui.structureNameLineEdit is not None, "Data type name edit not loaded!"
  assert ui.typeDeletePushButton is not None, "Delete button not loaded!"
  assert ui.structureAddPushButton is not None, "Structure add button not loaded!"
  assert ui.structureAddPushButton is not None, "Structure add button not loaded!"

def test_form_launch2(gui: object):
  """
      Args:
  """
  app, ui, qtbot = gui
  assert ui.headerLabel is not None, "Header not loaded!"
  assert ui.dataTypeLabel is not None, "Data type label not loaded!"
  assert ui.loadPushButton is not None, "Bush button not loaded!"
  assert ui.savePushButton is not None, "Save button not loaded!"
  assert ui.helpPushButton is not None, "Help button not loaded!"
  assert ui.cancelPushButton is not None, "Cancel button not loaded!"
  assert ui.structuralPropsTableView is not None, "Table view not loaded!"
  assert ui.addRowPushButton is not None, "Add row button not loaded!"
  assert ui.headingAddpushButton is not None, "Heading Add button not loaded!"
  assert ui.dataTypeLabel is not None, "Data type label not loaded!"
  assert ui.typeComboBox is not None, "Data type combo box not loaded!"
  assert ui.structureNameLineEdit is not None, "Data type name edit not loaded!"
  assert ui.typeDeletePushButton is not None, "Delete button not loaded!"
  assert ui.structureAddPushButton is not None, "Structure add button not loaded!"
  assert ui.structureAddPushButton is not None, "Structure add button not loaded!"