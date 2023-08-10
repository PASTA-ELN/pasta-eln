""" Common functions in a number of widgets """
import platform, subprocess, os
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtWidgets import QMenu, QWidget  # pylint: disable=no-name-in-module
from PySide6.QtCore import     QPoint # pylint: disable=no-name-in-module
from ..guiStyle import Action


def initContextMenu(widget:QWidget, pos:QPoint) -> None: #TODO_P3 move all context menu of this type to separate function
  # sourcery skip: extract-method
  """
  Create a context menu

  Args:
    widget (QWidget): parent widget
    pos (position): Position to create context menu at
  """
  context = QMenu(widget)
  # for extractors
  extractors = widget.comm.backend.configuration['extractors']
  extension = Path(widget.doc['-branch'][0]['path']).suffix[1:]
  if extension.lower() in extractors:
    extractors = extractors[extension.lower()]
    baseDocType= widget.doc['-type'][0]
    choices= {key:value for key,value in extractors.items() \
                if key.startswith(baseDocType)}
    for key,value in choices.items():
      Action(value,                     widget, [CommandMenu.CHANGE_EXTRACTOR, key], context)
    context.addSeparator()
    Action('Save image',                widget, [CommandMenu.SAVE_IMAGE],            context)
  #TODO_P2 not save now: when opening text files, system can crash as default option might be 'vi'
  # Action('Open file with another application', widget.changeExtractor, context, widget, name='_openExternal_')
  Action('Open folder in file browser', widget, [CommandMenu.OPEN_FILEBROWSER],      context)
  Action('Hide',                        widget, [CommandMenu.HIDE],                  context)
  context.exec(widget.mapToGlobal(pos))
  return


def executeContextMenu(widget:QWidget, command:list[Any]) -> None:
  """
  Execute context menu command

  Args:
    widget (QWidget): parent widget
    command (list): command
  """
  filePath = Path(widget.doc['-branch'][0]['path'])
  if command[0] is CommandMenu.OPEN_FILEBROWSER or command[0] is CommandMenu.OPEN_EXTERNAL:
    filePath = widget.comm.backend.basePath/filePath
    filePath = filePath if command[0] is CommandMenu.OPEN_EXTERNAL else filePath.parent
    if platform.system() == 'Darwin':       # macOS
      subprocess.call(('open', filePath))
    elif platform.system() == 'Windows':    # Windows
      os.startfile(filePath) # type: ignore[attr-defined]
    else:                                   # linux variants
      subprocess.call(('xdg-open', filePath))
  elif command[0] is CommandMenu.SAVE_IMAGE:
    image = widget.doc['image']
    if image.startswith('data:image/'):
      imageType = image[11:14] if image[14]==';' else image[11:15]
    else:
      imageType = 'svg'
    saveFilePath = widget.comm.backend.basePath/filePath.parent/f'{filePath.stem}_PastaExport.{imageType.lower()}'
    path = widget.doc['-branch'][0]['path']
    if not path.startswith('http'):
      path = (widget.comm.backend.basePath/path).as_posix()
    widget.comm.backend.testExtractor(path, recipe='/'.join(widget.doc['-type']), saveFig=str(saveFilePath))
  elif command[0] is CommandMenu.HIDE:
    widget.comm.backend.db.hideShow(widget.docID)
    widget.comm.changeTable.emit('','')
    widget.comm.changeDetails.emit(widget.doc['_id'])
  elif command[0] is CommandMenu.CHANGE_EXTRACTOR:
    #TODO_P1 bug occurs
    widget.doc['-type'] = command[1]
    widget.comm.backend.useExtractors(filePath, widget.doc['shasum'], widget.doc)  #any path is good since the file is the same everywhere; data-changed by reference
    if len(widget.doc['-type'])>1 and len(widget.doc['image'])>1:
      widget.doc = widget.comm.backend.db.updateDoc({'image':widget.doc['image'], '-type':widget.doc['-type']}, widget.doc['_id'])
      widget.comm.changeTable.emit('','')
      widget.comm.changeDetails.emit(widget.doc['_id'])
  else:
    print(f'**ERROR: command not found in _contextMenu {command}')
  return


class CommandMenu(Enum):
  """ Commands used in this file """
  CHANGE_EXTRACTOR = 2
  SAVE_IMAGE       = 3
  OPEN_FILEBROWSER = 4
  OPEN_EXTERNAL    = 5
  HIDE             = 6
