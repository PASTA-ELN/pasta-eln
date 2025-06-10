"""example addon: adds to the form content.

**This file has to be called form_auto.py and only this file is called from form.**

**In its default form, the description is commented out to disable this addon and not show in the GUI**

THIS IS A ADVANCED ADDON TUTORIAL
This tutorial teaches
- do not use chatgpt library, but use the requests library in order to employ less dependencies
- the structure of documents
"""
import requests

# The following two variables are mandatory
# description  = 'Use Gemini LLM to generate content'  #short description that is shown in the menu
reqParameter = {'key':'API key of google'} #possibility for required parameters: like API-key, etc. {'API': 'text'}
helpText = 'To get API key, you have to register at https://aistudio.google.com/app/apikey and create a new key.'

def main(backend, doc, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        backend (pasta backend): allow to extract data
        doc (dict): dictionary of the content: comment, title, image might be helpful
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        str: content to add
    """
    apiKey = parameter.get('key')
    if not apiKey:
        return "API key not provided in parameters. Please configure it in the addon settings."
    if not doc['comment']:
        return "No comment provided in the document. Please add a comment to expand."
    promptText = f"Expand the following text: '{doc['comment']}'."
    url        = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={apiKey}'
    headers    = {"Content-Type": "application/json"}
    data       = {"contents": [{"parts": [{"text": promptText}]}]}
    # main try block: if it fails, it will return an error message
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        result = response.json()
        # text might be result['candidates'][0]['content']['parts'][0]['text']
        reply = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Could not extract text.")
        return reply
    except Exception as e:
        return f"Error calling Gemini API: {e}"
