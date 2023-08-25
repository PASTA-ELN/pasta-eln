#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: fixtures.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union

from PySide6 import QtWidgets
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from cloudant.document import Document
from pytest import fixture
from pytestqt.exceptions import capture_exceptions
from pytestqt.qtbot import QtBot

from pasta_eln.gui import main_gui, MainWindow
from pasta_eln.ontology_configuration.ontology_configuration_extended import OntologyConfigurationForm, get_gui
from tests.app_tests.common.test_utils import get_ontology_document


@fixture()
def qtbot_session(qt_app, request):
  result = QtBot(qt_app)
  with capture_exceptions():
    yield result

@fixture()
def ontology_doc_mock(mocker) -> Document:
  mock_doc = mocker.patch('cloudant.document.Document')
  mock_doc.__getitem__.side_effect = get_ontology_document('ontology_document.json').__getitem__
  return mock_doc


@fixture()
def ontology_editor_gui(request, ontology_doc_mock) -> tuple[QApplication,
                                                            QtWidgets.QDialog,
                                                            OntologyConfigurationForm,
                                                            QtBot]:
  app, ui_dialog, ui_form_extended = get_gui(ontology_doc_mock)
  qtbot: QtBot = QtBot(app)
  return app, ui_dialog, ui_form_extended, qtbot


@fixture(scope="module")
def pasta_gui(request) -> tuple[Union[QApplication, QCoreApplication, None],
                              MainWindow,
                              QtBot]:
  app, image_viewer = main_gui()
  qtbot = QtBot(app)
  # QTest.qWait(0.5 * 1000)

  return app, image_viewer, qtbot
