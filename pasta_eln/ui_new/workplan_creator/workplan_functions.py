"""Write the given parameters of a workplan in a file with the format of the common workplan description."""
import json
import re
from pathlib import Path
from typing import Any, TypedDict
import pandas as pd
from PySide6.QtCore import Qt
from pasta_eln.backend_worker.worker import Task
from pasta_eln.ui.gui_communicate import Communicate


class WorkplanProcedure(TypedDict):
  """A procedure entry stored in a serialized workplan."""

  procedure: str
  sample: str
  parameters: dict[str, str]


class Workplan(TypedDict):
  """The JSON-compatible workplan format saved by the Workplan Creator."""

  name: str
  procedures: list[WorkplanProcedure]


def generateAndSaveWorkplan(comm: Communicate, workplan: Workplan, filename: str) -> None:
  """
  Write the given parameters of a workplan in a file with the format of the common workplan description.
  Args:
    comm: for Communication between widgets
    workplan: workplan dictionary that contains all important workplan information
    filename: name of the file that is saved

  Returns:

  """
  jsonWorkplan = json.dumps(workplan, indent=2)
  comm.uiRequestTask.emit(Task.ADD_DOC, {
    'hierStack': [comm.projectID],
    'docType': 'workflow/workplan',
    'doc': {'name': filename, 'content': jsonWorkplan}})


class Storage:
  """
  Stores the Procedures and their information for easier access with fewer Callbacks and proper getters
  """

  def __init__(self, comm: Communicate, projectID: str):
    self.comm = comm
    self.procedureTable = pd.DataFrame()

    self.updateStorage(projectID)

  def updateStorage(self, projectID: str) -> None:
    """
    Requests the procedureTable from Backend and saves it in self.procedureTable.
    Emits storageUpdated Signal for Callback
    Args:
      projectID: ID of the Project for which the table should be requested.

    Returns:

    """

    def onGetTable(table: pd.DataFrame, docType: str) -> None:
      if docType == 'workflow/procedure':
        self.procedureTable = table
        self.comm.storageUpdated.emit(projectID)

    self.comm.backendThread.worker.beSendTable.connect(onGetTable, type=Qt.ConnectionType.SingleShotConnection)
    self.comm.uiRequestTable.emit('workflow/procedure', projectID, True)

  def getProcedureIDs(self) -> list[str]:
    """
    Returns: IDs of all the Procedures of the current Project

    """
    return self.procedureTable['id'].to_list()

  def getProcedureTitle(self, procedureID: str) -> str:
    """
    Args:
      procedureID: docID for the procedure

    Returns: The title or name of the procedure with the given procedureID
    """
    title = ''
    row = self.procedureTable.loc[self.procedureTable['id'] == procedureID]
    if not row.empty:
      title = row['name'].iloc[0]
    return title

  def getProcedureTags(self, procedureID: str) -> list[str]:
    """
    Args:
      procedureID: docID for the procedure

    Returns: The tags of the procedure with the given procedureID
    """
    tags = self.procedureTable[self.procedureTable['id'] == procedureID]['tags'].iloc[0]
    tags = ['#' + tag for tag in tags.split(', ')]
    return tags


  def requestProcedureText(self, procedureID: str) -> None:
    """
    Reads the file where the procedure is stored and replaces content in Storage with complete content
    emits self.comm.storageUpdated(procedureID) to notify when it is ready (with procedureID as identifier)

    Args:
      procedureID: docID for the procedure
    """
    def onGetDoc(doc: dict[str, Any]) -> None:
      if procedureID == doc['id']:
        docPath = doc['branch'][0]['path']
        if docPath:
          path = self.comm.basePath / docPath
        else:
          path = Path()
        if path.is_file():
          with open(path, encoding='utf-8') as file:
            text = file.read()
          self.procedureTable.loc[self.procedureTable['id'] == procedureID, 'content'] = text
        self.comm.storageUpdated.emit(procedureID)
    self.comm.backendThread.worker.beSendDoc.connect(onGetDoc, type=Qt.ConnectionType.SingleShotConnection)
    self.comm.uiRequestDoc.emit(procedureID)


  def getProcedureText(self, procedureID: str) -> str:
    """
    get Text/Content of procedure, if the content is cut off because of character-limit, call requestProcedureText()
    first
    Args:
      procedureID: docID for the procedure

    Returns: Currently stored text of procedure with the procedureID.
    """
    text = ''
    row = self.procedureTable.loc[self.procedureTable['id'] == procedureID]
    if not row.empty:
      text = row['content'].iloc[0]
    return text


  def getProcedureDefaultParameters(self, procedureID: str) -> dict[str, str]:
    """
    Args:
      procedureID: docID for the procedure

    Returns: The default tags of the procedure with the given procedureID
    """
    parameters: dict[str, str] = {}
    text = self.getProcedureText(procedureID)
    params = re.findall(r'\|[^|]+\|[^|]+\|', text)
    try:
      parameters = {s.split('|')[1]: s.split('|')[2] for s in params}
    except Exception as e:
      print(e)
    return parameters

  def getProcedureShortDescription(self, procedureID: str) -> str:
    """
    Args:
      procedureID: docID for the procedure

    Returns: short description / comment of the procedure with the given procedureID

    """
    comment = ''
    row = self.procedureTable.loc[self.procedureTable['id'] == procedureID]
    if not row.empty:
      comment = row['comment'].iloc[0]
    return comment
