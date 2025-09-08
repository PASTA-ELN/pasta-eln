"""example add-on: use a csv file to input data in rows

THIS IS A VERY ADVANCED ADD-ON TUTORIAL
This tutorial teaches
- how to group import metadata
"""
from pathlib import Path
import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox
from pasta_eln.backendWorker.sqlite import MAIN_ORDER
from pasta_eln.backendWorker.worker import Task

# The following two variables are mandatory
description  = 'Import csv-data'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}

## Example csv file
# "type","name","comment",".chemistry","geometry.height","geometry.width"
# "sample","sample A","some text","A2B2C3",4,2
# "sample","sample B","other text","A2B2C4",4,4
# "sample","sample C","more text","A2B2C5",4,4

def main(comm, hierStack, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        comm (Communicate): communicate-backend
        hierStack (list): node in hierarchy to start the creation
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        bool: success
    """
    # Read csv file as a dataframe
    if 'fileNames' not in parameter:
        res = QFileDialog.getOpenFileName(widget,'Use this file for output', str(Path.home()))
        if res is None:
            return False
    else:
        res = parameter['fileNames']
    df = pd.read_csv(res[0])

    # verify the columns are correct
    colNames = list(df.columns)
    if 'type' not in colNames or 'name' not in colNames:
        QMessageBox.critical(widget, 'Error', 'You have to have columns named "type" and "name"', 'Critical')
        return False
    if len(df['type'].unique()) > 1:
        QMessageBox.critical(widget, 'Error', 'All items in the type column have to be the same', 'Critical')
        return False
    docType = df['type'].unique()[0]
    if docType not in comm.docTypesTitles:
        QMessageBox.critical(widget, 'Error', 'The type does not exist in PASTA database', 'Critical')
        return False
    # columns that are in the Pasta-ELN
    colPasta = [f'{i["class"]}.{i["name"]}' for i in comm.dataHierarchyNodes[docType]]
    colPasta = [i[1:] if i[1:] in MAIN_ORDER+['tags','qrCodes'] else i for i in colPasta] + ['type']
    if set(colNames).difference(colPasta):
        QMessageBox.critical(widget, 'Error', f'All columns must exist in the data schema. Offending: {set(colNames).difference(colPasta)}', 'Critical')
        return False

    # Loop all rows
    for _, row in df.iterrows():
        data = row.to_dict()
        del data['type']
        comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':hierStack.split('/'), 'docType':docType, 'doc':data})

    comm.uiRequestHierarchy.emit(widget.projID, widget.showAll)                    # update with new hierarchy
    return True
