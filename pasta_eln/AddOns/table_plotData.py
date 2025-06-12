"""example addon: plot data from files

THIS IS A VERY ADVANCED ADDON TUTORIAL
This tutorial teaches
- how to plot the data from files
"""
import matplotlib.pyplot as plt
import pandas as pd
from pasta_eln.miscTools import callDataExtractor

# The following two variables are mandatory
description  = 'Default data plot'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}

def main(backend, df, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        backend (pasta backend): allow to extract data
        df (Dataframe): dataframe with the data to plot. The docIDand path columns are of most interest
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        bool: success
    """
    # no cleaning needed since we only use id and path columns
    for idx, row in df.iterrows():
        if not row['path'].endswith('.csv'):          #by default, only the csv file extractor has a data function; you can change that
            continue
        res = callDataExtractor(row['path'], backend)
        if res is None:
            continue
        # Here you can process the extracted data further, e.g., plot it
        if isinstance(res, pd.DataFrame):
            res.plot()
            plt.show()
        else:
            print(f"Extracted data is not a DataFrame. {row['path']}")
    return True
