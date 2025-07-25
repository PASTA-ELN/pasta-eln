"""example addon: create a report from within the project view

THIS IS A VERY ADVANCED ADDON TUTORIAL
This tutorial teaches
- the basic structure of project-view-addons (header, function for each node, body, footer)
"""
import base64
import re
import time
from io import BytesIO
from pathlib import Path
from anytree import PreOrderIter, Node
from PIL import Image
from PySide6.QtGui import QTextDocument  # This is used for html-markdown conversion: works fine here
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Slot
import pasta_eln
from pasta_eln.Resources import Icons as icons
from pasta_eln.textTools.stringChanges import markdownEqualizer

# The following two variables are mandatory
description  = 'Create html report'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}

HTML_HEADER = '<!DOCTYPE html>\n<html>\n<head>\n<style>'\
    '* {font-family: sans-serif;}'\
    '.node {border: 1px dotted #AAAAAA; background-color: #EEEEEE;}'\
    'h1,h2,h3,h4 {margin-bottom: 0;} p {margin-top: 0;}'\
    'table {width: 100%;} td {width: 50%; vertical-align: top;}'\
    '.footline {margin-top: 50px; text-align: right;}'\
    '</style>\n</head>\n<body>\n'
HTML_FOOTER = '</body>\n</html>\n'

def main(comm, hierStack, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        comm (pasta communicate): communicate layer
        hierStack (list): node in hierarchy to start the creation
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        bool: success
    """
    # get filename to wirte into
    if 'fileNames' not in parameter:
        res = QFileDialog.getSaveFileName(widget,'Use this file for output', str(Path.home()))
        if res is None:
            return False
    else:
        res = parameter['fileNames']
    # Collect the hierarchy first, once you have it, collect all the docs
    hierarchy = comm.getHierarchy(hierStack.split('/')[0])
    docs = comm.getDocs([i.id for i in PreOrderIter(hierarchy)]) # Collect all the documents that belong to this hierarchy
    # All data is known in this function, process the data
    qtDocument = QTextDocument()   #used for markdown -> html conversion

    # function to handle each data entry
    def node2html(node):
        """
        Function that renders each node into html
        - Node properties: depth, name, docType, id

        Args:
            node (anyNode): anytree node to process

        Returns:
            str: conversion of node into html string
        """
        hidden = not all(node.gui)        # is this node hidden?
        if hidden:
            return ''
        doc = docs[node.id]  # GET ALL INFORMATION OF THIS NODE
        output = '<div class="node">\n'
        # headline of each node: either as html headline or normal text, incl. the objective
        if node.depth<4 and node.docType[0][0]=='x':
            output += f'<h{node.depth+1}>{node.name}</h{node.depth+1}>'
        else:
            output += f"{node.name}&nbsp;&nbsp;{'/'.join(node.docType)}<br>\n"
        if node.docType[0]=='x0':
            output += f"<b>Objective: {doc.get('',{}).get('objective',[''])[0]}</b>"
        # create a two column table: left side: tags and comments; right side: image, content
        output += '<table><tr><td>'
        stars = ''.join('\u2605'*int(i[1]) for i in doc['tags'] if re.match(r'^_\d$',i))  # the stars are part of tags
        otherTags = ', '.join(i for i in doc['tags'] if not re.match(r'^_\d$',i))
        output += f'Tags: {stars} {otherTags}<br>' if stars or otherTags else ''
        qtDocument.setMarkdown(markdownEqualizer(doc['comment']))
        output += qtDocument.toHtml()
        output += '</td><td>'
        if 'content' in doc and doc['content']:
            qtDocument.setMarkdown(markdownEqualizer(doc['content']))
            output += qtDocument.toHtml()
        output += f'<img src="{doc["image"]}"/>' if 'image' in doc and doc['image'].startswith('data:') else ''
        output += doc['image'] if 'image' in doc and doc['image'].startswith('<?xml version="1.0"') else ''
        return f'{output}</td></tr></table></div>\n\n'

    # main function that calls the render function
    out = ''.join(node2html(node) for node in PreOrderIter(hierarchy))

    # add footer line with pasta-eln icon (read and converted to base64 to be inline included in html)
    iconImg = Image.open(f'{icons.__path__[0]}/favicon64.ico')
    figfile = BytesIO()
    iconImg.save(figfile, format='PNG')
    imageB64 = base64.b64encode(figfile.getvalue()).decode()
    imageB64 = f"data:image/png;base64,{imageB64}"
    out += f'<div class="footline">Created with Pasta-ELN {pasta_eln.__version__} and the default HTML export&nbsp;&nbsp;&nbsp;<image src="{imageB64}"/></div>'

    # save everything to the html file
    with open(res[0], 'w', encoding='utf-8') as f:
        f.write(f'{HTML_HEADER}{out}{HTML_FOOTER}')
    print(f'Wrote a html file with {len(HTML_HEADER)+len(out)+len(HTML_FOOTER)} bytes')
    QMessageBox.information(widget, 'Information', f'Wrote a html file with {len(HTML_HEADER)+len(out)+len(HTML_FOOTER)} bytes',
                            QMessageBox.StandardButton.Ok)
    return True
