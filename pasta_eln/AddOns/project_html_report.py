import re
from pathlib import Path
from anytree import PreOrderIter
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QTextDocument
from pasta_eln.stringChanges import markdownEqualizer

description  = "Create html report"  #short description that is shown in the menu
pastaVersion = "2.6.0"

HTML_HEADER = "<!DOCTYPE html>\n<html>\n<head>\n<style>"\
    "* {font-family: sans-serif;}"\
    ".node {border: 1px dotted #AAAAAA; background-color: #EEEEEE;}"\
    "h1,h2,h3,h4 {margin-bottom: 0;} p {margin-top: 0;}"\
    "table {width: 100%;} td {width: 50%; vertical-align: top;}"\
    ".footline {margin-top: 50px; text-align: right;}"\
    "</style>\n</head>\n<body>\n"
HTML_FOOTER = "</body>\n</html>\n"
PASTA_ICON = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAgCAYAAADqgqNBAAAFUklEQVR4nLWXzW8bRRTAf7P2ZO3Ejb+SunWctPTTVVSnpapoufTSQ0GUSpw4cIAKCQmEEH8HJy5ckGhVriCgVKKHVkJwKFAotKGEViF1EyfNdxx7nV1n1zsctl7biZt+qHnSSrMz773fe29mR2+FUkoBuIWrMPEN2r73cEcvYOz+EC2UgFoVAjoAEV2A7OJ5SRBgdHQUdeULdhw8jFz4jampAjfnh1sUdV0nFouRzWaJRCJPBTEMA2CdXRAg2Rli7Mu/mXvtAOlXp5HJQXb27gHXASCfz2MYBoZhUK1WSaVSVKvVFkemaa6DNuvU1w3DQEpJLpfz4LIrTOatPUSP7IHAJGDS1RkGpXAcu8VhsVhkbm6ubYZSSmzbXvdez7xcMcBVACwtLXlwc9WFwcPogWGIvkzH2OcU5DGUjK0DtHPebq0OtCwLu+b40LqUK4YHD4fDVLadwM5/itzxBtF4kt1xAzs5hGVZFItF37GUklgs5pdS13W/vPUsHwVEE/7cQKbfg88vLDIyMskx4RAD6EiQH/mVyQ7pOXVspJTous7Q0BC9vb0t2dXFNE1qLhjlZcDb8/pe18f1M5PNZj14TzLBwf0ZusaDnpfVRTI7TxCduMFKcojugSMAxOPxlhO79vT676lenkSCdaMu7Q4q+gLKKoKqkejtI/7fRbQDbyIS/U/k7GnFS9WuoBb+RGReYeXmL1QnI0S776O6BxCJvZsCBtD8kW0g9G6Wb0wz8/1d3OI8IpzYNDDUM5ddoPeiindJnT7M1pckWmoX7uhlsCvP9UptlkbmfadQ0z8TSO9FkzNoyRQ4Jmr2j00Bt8C15CGo2SitEzrTqJU5RM8B1NTwBubPCd40Anf9Pb258OV/GrPWEioYRRXzkNy/+XA1cRmROg7F29CZhpUKOCZa+ugmw+0K5ug9qlYGVc4j4llYnkD0HIBQtL2ltQzmgvc12JVnggfrg8JXc8j0FXae3e6dctkJpUKrdmWK2tiPqAe/I0rjKLeK0HTYksYoDuCE9pI8c+Yp4bKLvndPIcw8JA6hCj+g7X0H1T3gZ+Xeu4q6dQG1PAIhUJbnQIWA6giliwuY853EdlUIZB8G8Jj7QdR7OJbvoEYvILIfgFNG1TTcyeswO4wqjcPSHVAmhAALxi5MEd6ms/31ZMObBYgwxPcjugdg60G0vqOPvKIbcPCzrP37HWr4PJiT3nyoyflDKd41CEYCRHaFG/Nt9Aj3IQ6+7VVjTSXWwd2/zuMOnwPdxBgzmb2yRN/pHvR4hw8QUqBs5UFCDWfm2CoPrsyz9WScSDrcWKuGES++T+DQ2RZ489WCO3ENd/gcIuKFrtUEHQmJ1hloKFmgyk1gq/FoYS8wGQ401gARsVA3PvPa87aZ2xWcyx9B6VqjdCFalaXAGq+yeL1Mz4kYMhp4ZBWag/Xt0ycInPzEL38j89IYs1//xPSlWSi7rfv38FG2F2f5dhl71uvpVLmpTyu7LfrgBTR1cZbCt9MwexNVnvLVg/n74wQ0QWn8HityH65rY0e2InSBshToILscnJpEWQq526HjY40FXWNRFyilQAE6vi5AqayorXg/O/PpEspVlFcTaCMjkHDBdRCXLl1StmMjgw+bRbu1T0esKeOahtRfb5o3DMPr0duJq0ATyECQYCqVojBZWA9dK2uhbdY2bJvXBLA9sx0t07/Dz3pDWVsBvB6+Lj7YtjcGA1u2bCGXyyHUqqEmphe5deuWZygambSMm4D1KrX7DXqcSCk5fvw4g4ODjU9temaOwsR9ZmZmsB17wzI/CxRNMJDpJ5fL0d/vteL/Ax2ToEnExn5DAAAAAElFTkSuQmCC"

def main(backend, projID, widget, parameter={}):
    # Initialize variables
    if not parameter:
        res = QFileDialog.getSaveFileName(widget,'Use this file for output', str(Path.home()))
        if res is None:
            return False
    else:
        res = parameter['fileNames']
    backend.changeHierarchy(projID)
    qtDocument = QTextDocument()

    def node2html(node):
        """
        Function that renders each node into html

        Node properties: depth, name, docType, id
        """
        hidden = not all(node.gui)  # is this node hidden
        if hidden:
            return ''
        doc = backend.db.getDoc(node.id)
        output = '<div class="node">\n'
        if node.depth<4 and node.docType[0][0]=='x':
            output += f'<h{node.depth+1}>{node.name}</h{node.depth+1}>'
        else:
            output += f'{node.name}&nbsp;&nbsp;{'/'.join(node.docType)}<br>\n'
        if node.docType[0]=='x0':
            output += f"<b>Objective: {doc.get('',{}).get('objective',[''])[0]}</b>"
        output += "<table><tr><td>"
        stars = ''.join('\u2605'*int(i[1]) for i in doc['tags'] if re.match(r'^_\d$',i))
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
    proj = backend.db.getHierarchy(projID)
    out = "".join(node2html(node) for node in PreOrderIter(proj))
    out += f'<div class="footline">Created with Pasta-ELN {pastaVersion} and the default HTML export <image src="{PASTA_ICON}"/></div>'
    with open(res[0], 'w', encoding='utf-8') as f:
        f.write(f'{HTML_HEADER}{out}{HTML_FOOTER}')
    return True
