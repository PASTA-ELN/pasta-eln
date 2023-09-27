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
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QDialog
from cloudant.document import Document
from pytest import fixture
from pytestqt.qtbot import QtBot

from pasta_eln.GUI.ontology_configuration.create_type_dialog_extended import CreateTypeDialog
from pasta_eln.GUI.ontology_configuration.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.GUI.ontology_configuration.iri_column_delegate import IriColumnDelegate
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
from pasta_eln.GUI.ontology_configuration.retrieve_iri_action import RetrieveIriAction
from pasta_eln.database import Database
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
  mock_pasta_db = mocker.patch('pasta_eln.database')
  mock_couch_db = mocker.patch('cloudant.couchdb')
  mock_couch_db['-ontology-'] = mock_document
  mock_pasta_db = mocker.patch.object(mock_pasta_db, 'db', create=True)
  mocker.patch('pasta_eln.GUI.ontology_configuration.create_type_dialog_extended.logging.getLogger')
  mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration.Ui_OntologyConfigurationBaseForm.setupUi')
  mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.adjust_ontology_data_to_v3')
  mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.RetrieveIriAction')
  mocker.patch.object(QDialog, '__new__')
  mocker.patch.object(OntologyPropsTableViewModel, '__new__')
  mocker.patch.object(OntologyAttachmentsTableViewModel, '__new__')
  mocker.patch.object(RequiredColumnDelegate, '__new__', lambda _: mocker.MagicMock())
  mocker.patch.object(DeleteColumnDelegate, '__new__', lambda _: mocker.MagicMock())
  mocker.patch.object(ReorderColumnDelegate, '__new__', lambda _: mocker.MagicMock())
  mocker.patch.object(OntologyConfigurationForm, 'typePropsTableView', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'typeAttachmentsTableView', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'addPropsRowPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'addAttachmentPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'saveOntologyPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'addPropsCategoryPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'deletePropsCategoryPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'deleteTypePushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'addTypePushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'cancelPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'helpPushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'attachmentsShowHidePushButton', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'typeComboBox', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'propsCategoryComboBox', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'typeLabelLineEdit', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'typeIriLineEdit', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'delete_column_delegate_props_table', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'reorder_column_delegate_props_table', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'delete_column_delegate_attach_table', create=True)
  mocker.patch.object(OntologyConfigurationForm, 'reorder_column_delegate_attach_table', create=True)
  mocker.patch.object(CreateTypeDialog, '__new__')
  return OntologyConfigurationForm(mock_pasta_db)


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
def iri_delegate() -> IriColumnDelegate:
  return IriColumnDelegate()


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
  mock_doc.__delitem__.side_effect = mock_doc_content.__delitem__
  mock_doc.pop.side_effect = mock_doc_content.pop
  mock_doc.keys.side_effect = mock_doc_content.keys
  mock_doc.types.side_effect = lambda: {
    data: mock_doc_content[data]
    for data in mock_doc_content if type(mock_doc_content[data]) is dict
  }
  mock_doc.types_list.side_effect = mocker.MagicMock(return_value=[data for data in mock_doc_content
                                                                   if type(mock_doc_content[data]) is dict])
  return mock_doc


@fixture()
def pasta_db_mock(mocker, ontology_doc_mock) -> Database:
  mock_db = mocker.patch('pasta_eln.database.Database')
  mock_couch_db = mocker.patch('cloudant.client.CouchDB')
  dbs = {'-ontology-': ontology_doc_mock}
  mock_couch_db.__getitem__.side_effect = dbs.__getitem__
  mocker.patch.object(mock_db, 'db', mock_couch_db, create=True)
  return mock_db


@fixture()
def ontology_editor_gui(request, pasta_db_mock) -> tuple[QApplication,
QtWidgets.QDialog,
OntologyConfigurationForm,
QtBot]:
  app, ui_dialog, ui_form_extended = get_gui(pasta_db_mock)
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


@fixture()
def retrieve_iri_action(mocker) -> RetrieveIriAction:
  mocker.patch.object(QAction, '__init__')
  mocker.patch.object(QAction, 'triggered', create=True)
  mock_icon = mocker.patch('PySide6.QtGui.QIcon')
  mocker.patch.object(QIcon, 'fromTheme', return_value=mock_icon)
  mock_parent = mocker.patch('PySide6.QtWidgets.QWidget')
  return RetrieveIriAction(mock_parent)


@fixture(scope="module")
def pasta_gui(request) -> tuple[Union[QApplication, QCoreApplication, None],
MainWindow,
QtBot]:
  app, image_viewer = mainGUI()
  qtbot = QtBot(app)
  return app, image_viewer, qtbot
