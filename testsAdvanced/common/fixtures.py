#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: fixtures.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union
from unittest.mock import MagicMock
from xml.etree.ElementTree import Element

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication
from pytest import fixture
from pytestqt.qtbot import QtBot

from pasta_eln.GUI.data_hierarchy.attachments_tableview_data_model import AttachmentsTableViewModel
from pasta_eln.GUI.data_hierarchy.create_type_dialog import TypeDialog
from pasta_eln.GUI.data_hierarchy.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.GUI.data_hierarchy.document_null_exception import DocumentNullException
from pasta_eln.GUI.data_hierarchy.iri_column_delegate import IriColumnDelegate
from pasta_eln.GUI.data_hierarchy.key_not_found_exception import KeyNotFoundException
from pasta_eln.GUI.data_hierarchy.lookup_iri_action import LookupIriAction
from pasta_eln.GUI.data_hierarchy.mandatory_column_delegate import MandatoryColumnDelegate
from pasta_eln.GUI.data_hierarchy.metadata_tableview_data_model import MetadataTableViewModel
from pasta_eln.GUI.data_hierarchy.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.GUI.data_hierarchy.tableview_data_model import TableViewModel
from pasta_eln.GUI.data_hierarchy.terminology_lookup_dialog import TerminologyLookupDialog
from pasta_eln.GUI.data_hierarchy.terminology_lookup_dialog_base import Ui_TerminologyLookupDialogBase
from pasta_eln.GUI.data_hierarchy.terminology_lookup_service import TerminologyLookupService
from pasta_eln.dataverse.client import DataverseClient
from pasta_eln.gui import MainWindow, mainGUI
from pasta_eln.webclient.http_client import AsyncHttpClient
from testsAdvanced.common.test_utils import read_json, read_xml


@fixture()
def create_type_dialog_mock(mocker) -> TypeDialog:
  mock_callable_1 = mocker.patch('typing.Callable')
  mock_callable_2 = mocker.patch('typing.Callable')
  mocker.patch.object(TypeDialog, 'setup_slots')
  mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.logging.getLogger')
  mocker.patch('pasta_eln. GUI. data_hierarchy. type_dialog.DataTypeInfo')
  mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.QDialog')
  mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.QTAIconsFactory')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog_base.Ui_TypeDialogBase.setupUi')
  mocker.patch.object(TypeDialog, 'titleLineEdit', create=True)
  return TypeDialog(mock_callable_1, mock_callable_2)


@fixture()
def terminology_lookup_dialog_mock(mocker) -> TerminologyLookupDialog:
  mocker.patch('PySide6.QtWidgets.QDialog')
  mocker.patch.object(Ui_TerminologyLookupDialogBase, 'setupUi')
  mocker.patch.object(Ui_TerminologyLookupDialogBase, 'terminologySearchPushButton', create=True)
  mocker.patch.object(Ui_TerminologyLookupDialogBase, 'errorConsolePushButton', create=True)
  mocker.patch.object(Ui_TerminologyLookupDialogBase, 'errorConsoleTextEdit', create=True)
  mocker.patch.object(Ui_TerminologyLookupDialogBase, 'searchProgressBar', create=True)
  mocker.patch.object(Ui_TerminologyLookupDialogBase, 'buttonBox', create=True)
  mocker.patch.object(Ui_TerminologyLookupDialogBase, 'terminologyLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.terminology_lookup_dialog.QPixmap')
  return TerminologyLookupDialog(mocker.MagicMock())


@fixture()
def terminology_lookup_mock(mocker) -> TerminologyLookupService:
  mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.logging.getLogger')
  return TerminologyLookupService()


@fixture()
def http_client_mock(mocker) -> AsyncHttpClient:
  mocker.patch('pasta_eln.webclient.http_client.logging.getLogger')
  mocker.patch('pasta_eln.webclient.http_client.ClientTimeout')
  return AsyncHttpClient()


@fixture()
def dataverse_client_mock(mocker) -> DataverseClient:
  mocker.patch('pasta_eln.dataverse.client.logging.getLogger')
  mocker.patch('pasta_eln.dataverse.client.AsyncHttpClient')
  return DataverseClient("test_url", "test_token")


@fixture()
def dataverse_tree_mock(mocker) -> Element | None:
  mocked_element_tree = mocker.MagicMock()
  mocked_element_tree_root = mocker.MagicMock()
  test_tree = read_xml('dataverse_list.xml')
  mocked_element_tree.getroot.return_value = mocked_element_tree_root
  mocked_element_tree_root.findall.side_effect = test_tree.getroot().findall
  return mocked_element_tree


@fixture()
def doc_null_exception(request) -> DocumentNullException:
  return DocumentNullException(request.param['message'], request.param['errors'])


@fixture()
def key_not_found_exception(request) -> KeyNotFoundException:
  return KeyNotFoundException(request.param['message'], request.param['errors'])


@fixture()
def table_model() -> TableViewModel:
  base_model = TableViewModel()
  base_model.setObjectName("TableViewModel")
  return base_model


@fixture()
def metadata_table_model() -> MetadataTableViewModel:
  metadata_model = MetadataTableViewModel()
  metadata_model.setObjectName("MetadataTableViewModel")
  return metadata_model


@fixture()
def attachments_table_model() -> AttachmentsTableViewModel:
  attachments_model = AttachmentsTableViewModel()
  attachments_model.setObjectName("AttachmentsTableViewModel")
  return attachments_model


@fixture()
def reorder_delegate() -> ReorderColumnDelegate:
  return ReorderColumnDelegate()


@fixture()
def mandatory_delegate() -> MandatoryColumnDelegate:
  return MandatoryColumnDelegate()


@fixture()
def delete_delegate() -> DeleteColumnDelegate:
  return DeleteColumnDelegate()


@fixture()
def iri_delegate() -> IriColumnDelegate:
  return IriColumnDelegate()


@fixture()
def data_hierarchy_doc_mock(mocker) -> MagicMock:
  mock_doc = mocker.MagicMock()
  mock_doc_content = read_json('data_hierarchy_document.json')
  mocker.patch.object(mock_doc, "__len__", lambda x, y: len(mock_doc_content))
  mock_doc.__getitem__.side_effect = mock_doc_content.__getitem__
  mock_doc.__setitem__.side_effect = mock_doc_content.__setitem__
  mock_doc.__contains__.side_effect = mock_doc_content.__contains__
  mock_doc.__iter__.side_effect = mock_doc_content.__iter__
  mock_doc.__delitem__.side_effect = mock_doc_content.__delitem__
  mock_doc.pop.side_effect = mock_doc_content.pop
  mock_doc.keys.side_effect = mock_doc_content.keys
  mock_doc.types.side_effect = lambda: {data: mock_doc_content[data] for data in mock_doc_content if
                                        type(mock_doc_content[data]) is dict}
  mock_doc.types_list.side_effect = mocker.MagicMock(
    return_value=[data for data in mock_doc_content if type(mock_doc_content[data]) is dict])
  return mock_doc


@fixture()
def terminology_lookup_config_mock() -> dict:
  return read_json('../../pasta_eln/GUI/data_hierarchy/terminology_lookup_config.json')


@fixture()
def retrieved_iri_results_pasta_mock() -> dict:
  return read_json('retrieved_iri_results_pasta.json')


@fixture()
def iri_lookup_web_results_pasta_mock() -> dict:
  return read_json('iri_lookup_web_results_pasta.json')


@fixture()
def retrieved_iri_results_science_mock() -> dict:
  return read_json('retrieved_iri_results_science.json')


@fixture()
def iri_lookup_web_results_science_mock() -> dict:
  return read_json('iri_lookup_web_results_science.json')


@fixture()
def retrieved_iri_results_name_mock() -> dict:
  return read_json('retrieved_iri_results_name.json')


@fixture()
def iri_lookup_web_results_name_mock() -> dict:
  return read_json('iri_lookup_web_results_name.json')


@fixture()
def metadata_column_names():
  return {0: "name", 1: "query", 2: "list", 3: "unit", 4: "IRI", 5: "mandatory"}


@fixture()
def attachments_column_names():
  return {0: "description", 1: "type"}


@fixture()
def lookup_iri_action(mocker) -> LookupIriAction:
  mocker.patch.object(QAction, '__init__')
  mocker.patch.object(QAction, 'triggered', create=True)
  mock_icon = mocker.patch('PySide6.QtGui.QIcon')
  mocker.patch.object(QIcon, 'fromTheme', return_value=mock_icon)
  mock_parent = mocker.patch('PySide6.QtWidgets.QWidget')
  mocker.patch('pasta_eln.GUI.data_hierarchy.lookup_iri_action.TerminologyLookupDialog')
  return LookupIriAction(mock_parent)


@fixture(scope="module")
def pasta_gui(request) -> tuple[Union[QApplication, QCoreApplication, None], MainWindow, QtBot]:
  app, image_viewer = mainGUI()
  qtbot = QtBot(app)
  return app, image_viewer, qtbot
