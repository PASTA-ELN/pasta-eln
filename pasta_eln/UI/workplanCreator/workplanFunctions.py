import json
import re
from pathlib import Path

import pandas as pd

from ..guiCommunicate import Communicate
from ...backendWorker.worker import Task


def generateAndSaveWorkplan(comm: Communicate, workplan: dict, filename: str) -> None:
  """
  Write the given parameters of a workplan in a file with the format of the common workplan description.
  """
  jsonWorkplan = json.dumps(workplan, indent=2)
  print("SAVED:", jsonWorkplan)
  comm.uiRequestTask.emit(Task.ADD_DOC, {
    'hierStack': [comm.projectID],
    'docType': "workflow/workplan",
    'doc': {'name': filename, 'content': jsonWorkplan}})


class Storage:
  """
  TODO
  """

  def __init__(self, comm: Communicate, projectID: str):
    self.comm = comm
    self.procedureTable = pd.DataFrame()

    self.updateStorage(projectID)

  def updateStorage(self, projectID: str):
    def onGetTable(table: pd.DataFrame, docType: str):
      if docType == "workflow/procedure":
        self.procedureTable = table
        self.comm.storageUpdated.emit(projectID)

    self.comm.backendThread.worker.beSendTable.connect(onGetTable)
    self.comm.uiRequestTable.emit("workflow/procedure", projectID, True)

  def getProcedureIDs(self) -> list[str]:
    return self.procedureTable["id"].to_list()

  def getProcedureTitle(self, procedureID: str) -> str:
    title = ""
    row = self.procedureTable.loc[self.procedureTable["id"] == procedureID]
    if not row.empty:
      title = row["name"].iloc[0]
    return title

  def getProcedureTags(self, procedureID: str) -> list[str]:
    tags = self.procedureTable[self.procedureTable["id"] == procedureID]["tags"].to_list()
    return tags

  def requestProcedureText(self, procedureID: str) -> str:
    """
    Reads the file where the procedure is stored and replaces content in Storage with complete content
    emits self.comm.storageUpdated(procedureID) to notify when it is ready (with procedureID as identifier)
    """
    def onGetDoc(doc: dict):
      if procedureID == doc["id"]:
        docPath = doc['branch'][0]['path']
        if docPath:
          path = self.comm.basePath / docPath
        else:
          path = Path()
        if path.is_file():
          with open(path, "r", encoding="utf-8") as file:
            text = file.read()
          self.procedureTable.loc[self.procedureTable["id"] == procedureID, "content"] = text
        self.comm.storageUpdated.emit(procedureID)
    self.comm.backendThread.worker.beSendDoc.connect(onGetDoc)
    self.comm.uiRequestDoc.emit(procedureID)

  def getProcedureText(self, procedureID: str) -> str:
    """
    get Text/Content of procedure, if the content is cut off because of character-limit, call requestProcedureText()
    first
    """
    text = ""
    row = self.procedureTable.loc[self.procedureTable["id"] == procedureID]
    if not row.empty:
      text = row["content"].iloc[0]
    return text

  def getProcedureDefaultParameters(self, procedureID: str) -> dict[str, str]:
    parameters = {}
    text = self.getProcedureText(procedureID)
    params = re.findall(r"\|[^|]+\|[^|]+\|", text)
    try:
      parameters = {s.split("|")[1]: s.split("|")[2] for s in params}
    except Exception as e:
      print(e, "This exception should thrown, when no parameters are in a procedure, fix it!")
    return parameters

  def getProcedureShortDescription(self, procedureID: str) -> str:
    comment = ""
    row = self.procedureTable.loc[self.procedureTable["id"] == procedureID]
    if not row.empty:
      comment = row["comment"].iloc[0]
    return comment
