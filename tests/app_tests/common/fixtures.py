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
from PySide6.QtWidgets import QApplication, QDialog
from cloudant.document import Document
from pytest import fixture
from pytestqt.qtbot import QtBot

from pasta_eln.gui import main_gui, MainWindow
from pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog_extended import CreateTypeDialog
from pasta_eln.ontology_configuration.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.ontology_configuration.exceptions.ontology_document_null_exception import OntologyDocumentNullException
from pasta_eln.ontology_configuration.ontology_attachments_tableview_data_model import OntologyAttachmentsTableViewModel
from pasta_eln.ontology_configuration.ontology_configuration_extended import OntologyConfigurationForm, get_gui
from pasta_eln.ontology_configuration.ontology_props_tableview_data_model import OntologyPropsTableViewModel
from pasta_eln.ontology_configuration.ontology_tableview_data_model import OntologyTableViewModel
from pasta_eln.ontology_configuration.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.ontology_configuration.required_column_delegate import RequiredColumnDelegate
from tests.app_tests.common.test_utils import get_ontology_document


@fixture()
def create_type_dialog_mock(request, mocker) -> CreateTypeDialog:
  mock_logger = mocker.patch('logging.Logger')
  mock_callable_1 = mocker.patch('typing.Callable')
  mock_callable_2 = mocker.patch('typing.Callable')
  mock_dialog = mocker.patch('PySide6.QtWidgets.QDialog')
  mock_type_dialog_base_setup = mocker.patch(
    'pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog_extended.Ui_CreateTypeDialog.setupUi')
  mocker.patch.object(CreateTypeDialog, 'setup_slots', mocker.MagicMock())
  mocker.patch('pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog_extended.logging.getLogger',
               return_value=mock_logger)
  mocker.patch(
    'pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog_extended.Ui_CreateTypeDialog.setupUi',
    return_value=mock_type_dialog_base_setup)
  mocker.patch.object(QDialog, '__new__', return_value=mock_dialog)
  dialog_instance = CreateTypeDialog(mock_callable_1, mock_callable_2)
  return dialog_instance


@fixture()
def doc_null_exception(request) -> OntologyDocumentNullException:
  return OntologyDocumentNullException(request.param['message'],
                                       request.param['errors'])


@fixture()
def table_model() -> OntologyTableViewModel:
  base_model = OntologyTableViewModel()
  base_model.setObjectName("OntologyTableViewModel")
  return base_model


@fixture()
def props_table_model() -> OntologyPropsTableViewModel:
  props_model = OntologyPropsTableViewModel()
  props_model.setObjectName("OntologyPropsTableViewModel")
  return props_model


@fixture()
def attachments_table_model() -> OntologyAttachmentsTableViewModel:
  attachments_model = OntologyAttachmentsTableViewModel()
  attachments_model.setObjectName("OntologyAttachmentsTableViewModel")
  return attachments_model


@fixture()
def reorder_delegate() -> ReorderColumnDelegate:
  return ReorderColumnDelegate()


@fixture()
def required_delegate() -> RequiredColumnDelegate:
  return RequiredColumnDelegate()


@fixture()
def delete_delegate() -> DeleteColumnDelegate:
  return DeleteColumnDelegate()


@fixture()
def ontology_doc_mock(mocker) -> Document:
  mock_doc = mocker.patch('cloudant.document.Document')
  mock_doc_content = get_ontology_document('ontology_document.json')
  mocker.patch.object(mock_doc, "__len__",
                      lambda x, y: len(mock_doc_content))
  mock_doc.__getitem__.side_effect = mock_doc_content.__getitem__
  mock_doc.__iter__.side_effect = mock_doc_content.__iter__
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
  return app, image_viewer, qtbot
