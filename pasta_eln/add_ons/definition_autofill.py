"""example add-on: fill definitions table with first entry from wikidata

**This file has to be called definition_autofill.py and only this file is called from the definitions GUI.**

**In its default form, the description is commented out to disable this add-on and not show in the GUI**

THIS IS A ADVANCED ADD-ON TUTORIAL
This tutorial teaches
- the structure of the definitions table
- how to fill the definitions table with the first entry from wikidata
- these add-ons can have multiple functions inside them
"""
import requests

# The following two variables are mandatory
# description  = 'Fill the definitions table by the first entry from wikidata'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}


def getFirstWikidataEntry(definition):
    """Get the first Wikidata entry for a given definition
    Args:
        definition (str): The definition to search for
    Returns:
        str: The URL of the first Wikidata entry, or '' if not found
    """
    url = f'https://www.wikidata.org/w/api.php?action=wbsearchentities&search={definition}&language=en&format=json'
    headers = {'User-Agent': 'PASTA-ELN (https://github.com/PASTA-ELN/pasta-eln)'}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:  # success
        data = response.json()
        if 'search' in data and len(data['search']) > 0: # check if search results exist
            return data['search'][0]['concepturi']
    print('Error in html request:', response.status_code, response.text)
    return ''


def main(comm, df, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        comm (Communicate): communicate-backend
        df (DataFrame): pandas dataframe with data
           Columns are: 'key', 'long', 'PURL', 'defType' with the PURL being filled
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        Dataframe: modified dataframe
    """
    if df.empty:
        return df
    emptyPURLmask = df['PURL'].isnull() | (df['PURL'] == '')  # only fill empty PURLs
    df.loc[emptyPURLmask, 'PURL'] = df.loc[emptyPURLmask, 'key'].apply(getFirstWikidataEntry)
    return df
