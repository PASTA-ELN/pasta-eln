"""example addon: use a csv file to input data in rows

THIS IS A VERY ADVANCED ADDON TUTORIAL
This tutorial teaches
- how to group import metadata
"""
from pathlib import Path
import pandas as pd
from PySide6.QtWidgets import QFileDialog
from pasta_eln.guiStyle import showMessage
from pasta_eln.sqlite import MAIN_ORDER

# The following two variables are mandatory
description  = 'Import csv-data'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}

## Example csv file
# "type","name","comment",".chemistry","geometry.height","geometry.width"
# "sample","sample A","some text","A2B2C3",4,2
# "sample","sample B","other text","A2B2C4",4,4
# "sample","sample C","more text","A2B2C5",4,4

def main(backend, hierStack, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        backend (pasta backend): allow to extract data
        hierStack (list): node in hierarchy to start the creation
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        bool: success
    """
    # Read csv file as a dataframe
    if 'fileNames' not in parameter:
        res = QFileDialog.getSaveFileName(widget,'Use this file for output', str(Path.home()))
        if res is None:
            return False
    else:
        res = parameter['fileNames']
    df = pd.read_csv(res[0])

    # verify the columns are correct
    colNames = list(df.columns)
    if 'type' not in colNames or 'name' not in colNames:
        showMessage(widget, 'Error', 'You have to have columns named "type" and "name"', 'Critical')
        return False
    if len(df['type'].unique()) > 1:
        showMessage(widget, 'Error', 'All items in the type column have to be the same', 'Critical')
        return False
    docType = df['type'].unique()[0]
    if docType not in backend.db.dataHierarchy('',''):
        showMessage(widget, 'Error', 'The type does not exist in PASTA database', 'Critical')
        return False
    # columns that are in the Pasta-ELN
    colPasta = [f'{i["class"]}.{i["name"]}' for i in backend.db.dataHierarchy(docType,'meta')]
    colPasta = [i[1:] if i[1:] in MAIN_ORDER+['tags','qrCodes'] else i for i in colPasta] + ['type']
    if set(colNames).difference(colPasta):
        showMessage(widget, 'Error', f'All columns must exist in the data schema. Offending: {set(colNames).difference(colPasta)}', 'Critical')
        return False

    # Move into that folder
    for i in hierStack.split('/'):
        backend.changeHierarchy(i)

    # Loop all rows
    for index, row in df.iterrows():
        data = row.to_dict()
        del data['type']
        backend.addData(docType, data)
    return True
