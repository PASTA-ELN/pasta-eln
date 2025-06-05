"""example addon: plot data from a table

THIS IS A VERY ADVANCED ADDON TUTORIAL
This tutorial teaches
- how to plot the metadata from a table
"""
import matplotlib.pyplot as plt
import pandas as pd

# The following two variables are mandatory
description  = 'Default metadata plot'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}

def main(backend, df, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        backend (pasta backend): allow to extract data
        df (Dataframe): dataframe with the data to plot
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        bool: success
    """
    for col in df.columns:
        numeric_series = pd.to_numeric(df[col], errors='coerce')
        if numeric_series.notna().any():
            plt.plot(df[col],'o')
            plt.xlabel('Index')
            plt.ylabel(col)
            plt.show()
            break
    return True
