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

from pasta_eln.GUI.ontology_configuration.create_type_dialog_extended import CreateTypeDialog
from pasta_eln.GUI.ontology_configuration.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.GUI.ontology_configuration.ontology_attachments_tableview_data_model import \
  OntologyAttachmentsTableViewModel
from pasta_eln.GUI.ontology_configuration.ontology_config_key_not_found_exception import \
  OntologyConfigKeyNotFoundException
from pasta_eln.GUI.ontology_configuration.ontology_configuration_extended import OntologyConfigurationForm, get_gui
from pasta_eln.GUI.ontology_configuration.ontology_document_null_exception import OntologyDocumentNullException
from pasta_eln.GUI.ontology_configuration.ontology_props_tableview_data_model import OntologyPropsTableViewModel
from pasta_eln.GUI.ontology_configuration.ontology_tableview_data_model import OntologyTableViewModel
from pasta_eln.GUI.ontology_configuration.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.GUI.ontology_configuration.required_column_delegate import RequiredColumnDelegate
from pasta_eln.gui import mainGUI, MainWindow
from tests.app_tests.common.test_utils import get_ontology_document


@fixture()
def create_type_dialog_mock(mocker) -> CreateTypeDialog:
  mock_callable_1 = mocker.patch('typing.Callable')
  mock_callable_2 = mocker.patch('typing.Callable')
  mocker.patch.object(CreateTypeDialog, 'setup_slots')
  mocker.patch('pasta_eln.GUI.ontology_configuration.create_type_dialog_extended.logging.getLogger')
  mocker.patch(
    'pasta_eln.GUI.ontology_configuration.create_type_dialog_extended.Ui_CreateTypeDialog.setupUi')
  mocker.patch.object(QDialog, '__new__')
  mocker.patch.object(CreateTypeDialog, 'titleLineEdit', create=True)
  return CreateTypeDialog(mock_callable_1, mock_callable_2)


@fixture()
def configuration_extended(mocker) -> OntologyConfigurationForm:
  mock_document = mocker.patch('cloudant.document.Document')
  mocker.patch('pasta_eln.GUI.ontology_configuration.create_type_dialog_extended.logging.getLogger')
  mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration.Ui_OntologyConfigurationBaseForm.setupUi')
  mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.adjust_ontology_data_to_v3')
  mocker.patch.object(QDialog, '__new__')
  mocker.patch.object(OntologyPropsTableViewModel, '__new__')
  mocker.patch.object(OntologyAttachmentsTableViewModel, '__new__')
  mocker.patch.object(RequiredColumnDelegate, '__new__', lambda _: mocker.MagicMock())
  mocker.patch.object(DeleteColumnDelegate, '__new__', lambda _: mocker.MagicMock())
  mocker.patch.object(ReorderColumnDelegate, '__new__', lambda _: mocker.MagicMock())
  mocker.patch.object(OntologyConfigurationForm, 'typePropsTableView', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'typeAttachmentsTableView', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'loadOntologyPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'addPropsRowPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'addAttachmentPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'saveOntologyPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'addPropsCategoryPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'deletePropsCategoryPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'deleteTypePushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'addTypePushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'cancelPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'typeComboBox', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'propsCategoryComboBox', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'typeLabelLineEdit', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'typeIriLineEdit', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'delete_column_delegate_props_table', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'reorder_column_delegate_props_table', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'delete_column_delegate_attach_table', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'reorder_column_delegate_attach_table', create=True)
  mocker.patch.object(CreateTypeDialog, '__new__')
  return OntologyConfigurationForm(mock_document)


@fixture()
def doc_null_exception(request) -> OntologyDocumentNullException:
  return OntologyDocumentNullException(request.param['message'],
                                       request.param['errors'])


@fixture()
def key_not_found_exception(request) -> OntologyConfigKeyNotFoundException:
  return OntologyConfigKeyNotFoundException(request.param['message'],
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
  mock_doc.__setitem__.side_effect = mock_doc_content.__setitem__
  mock_doc.__contains__.side_effect = mock_doc_content.__contains__
  mock_doc.__iter__.side_effect = mock_doc_content.__iter__
  mock_doc.keys.side_effect = mock_doc_content.keys
  mock_doc.types.side_effect = mocker.MagicMock(return_value=dict((data, mock_doc_content[data])
                                                                  for data in mock_doc_content
                                                                  if type(mock_doc_content[data]) is dict))
  mock_doc.types_list.side_effect = mocker.MagicMock(return_value=[data for data in mock_doc_content
                                                                   if type(mock_doc_content[data]) is dict])
  return mock_doc


@fixture()
def ontology_editor_gui(request, ontology_doc_mock) -> tuple[QApplication,
QtWidgets.QDialog,
OntologyConfigurationForm,
QtBot]:
  app, ui_dialog, ui_form_extended = get_gui(ontology_doc_mock)
  qtbot: QtBot = QtBot(app)
  return app, ui_dialog, ui_form_extended, qtbot


@fixture()
def props_column_names():
  return {
    0: "name",
    1: "query",
    2: "list",
    3: "unit",
    4: "IRI",
    5: "required"
  }


@fixture()
def attachments_column_names():
  return {
    0: "description",
    1: "type"
  }


@fixture(scope="module")
def pasta_gui(request) -> tuple[Union[QApplication, QCoreApplication, None],
MainWindow,
QtBot]:
  app, image_viewer = mainGUI()
  qtbot = QtBot(app)
  return app, image_viewer, qtbot
