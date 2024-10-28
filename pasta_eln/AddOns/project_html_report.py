import re, base64
from io import BytesIO
from pathlib import Path
from anytree import PreOrderIter
from PIL import Image
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QTextDocument
from pasta_eln.stringChanges import markdownEqualizer
import pasta_eln
from pasta_eln.Resources import Icons as icons

description  = "Create html report"  #short description that is shown in the menu; has to be included in all project-addons

HTML_HEADER = "<!DOCTYPE html>\n<html>\n<head>\n<style>"\
    "* {font-family: sans-serif;}"\
    ".node {border: 1px dotted #AAAAAA; background-color: #EEEEEE;}"\
    "h1,h2,h3,h4 {margin-bottom: 0;} p {margin-top: 0;}"\
    "table {width: 100%;} td {width: 50%; vertical-align: top;}"\
    ".footline {margin-top: 50px; text-align: right;}"\
    "</style>\n</head>\n<body>\n"
HTML_FOOTER = "</body>\n</html>\n"

def main(backend, hierStack, widget, parameter={}):
    """
    Args:
        filePath (Path): full path file name
        hierStack(str): stack of identifiers to this location, separated by /
        widget (QWidget): pyside6 widget, allows you to create forms
        parameters (dict): unused currently

    Returns:
        bool: success of function
    """
    # Initialize variables
    if not parameter:
        res = QFileDialog.getSaveFileName(widget,'Use this file for output', str(Path.home()))
        if res is None:
            return False
    else:
        res = parameter['fileNames']
    for i in hierStack.split('/'): #not needed here; to be in the correct folder if one wants to save something
        backend.changeHierarchy(i)
    qtDocument = QTextDocument()   #used for markdown -> html conversion

    def node2html(node):
        """
        Function that renders each node into html

        Node properties: depth, name, docType, id
        """
        hidden = not all(node.gui)        # is this node hidden?
        if hidden:
            return ''
        doc = backend.db.getDoc(node.id)  #get all information of this node
        output = '<div class="node">\n'
        # headline of each node: either as html headline or normal text, incl. the objective
        if node.depth<4 and node.docType[0][0]=='x':
            output += f'<h{node.depth+1}>{node.name}</h{node.depth+1}>'
        else:
            output += f"{node.name}&nbsp;&nbsp;{'/'.join(node.docType)}<br>\n"
        if node.docType[0]=='x0':
            output += f"<b>Objective: {doc.get('',{}).get('objective',[''])[0]}</b>"
        # create a two column table: left side: tags and comments; right side: image, content
        output += "<table><tr><td>"
        stars = ''.join('\u2605'*int(i[1]) for i in doc['tags'] if re.match(r'^_\d$',i))  # the stars are part of tags
        otherTags = ', '.join(i for i in doc['tags'] if not re.match(r'^_\d$',i))
        output += f'Tags: {stars} {otherTags}<br>' if stars or otherTags else ''
        qtDocument.setMarkdown(markdownEqualizer(doc['comment']))
        output += qtDocument.toHtml()
        output += "</td><td>"
        if 'content' in doc and doc['content']:
            qtDocument.setMarkdown(markdownEqualizer(doc['content']))
            output += qtDocument.toHtml()
        output += f'<img src="{doc["image"]}"/>' if 'image' in doc and doc['image'].startswith('data:') else ''
        output += doc["image"] if 'image' in doc and doc['image'].startswith('<?xml version="1.0"') else ''
        return f'{output}</td></tr></table></div>\n\n'

    # main function that calls the render function
    proj = backend.db.getHierarchy(hierStack)
    out = "".join(node2html(node) for node in PreOrderIter(proj))
    # add footer line with pasta-eln icon (read and converted to base64 to be inline included in html)
    iconImg = Image.open(f'{icons.__path__[0]}/favicon64.ico')
    figfile = BytesIO()
    iconImg.save(figfile, format="PNG")
    imageB64 = base64.b64encode(figfile.getvalue()).decode()
    imageB64 = f"data:image/png;base64,{imageB64}"
    out += f'<div class="footline">Created with Pasta-ELN {pasta_eln.__version__} and the default HTML export&nbsp;&nbsp;&nbsp;<image src="{imageB64}"/></div>'
    # save everything to the html file
    with open(res[0], 'w', encoding='utf-8') as f:
        f.write(f'{HTML_HEADER}{out}{HTML_FOOTER}')
    return True
