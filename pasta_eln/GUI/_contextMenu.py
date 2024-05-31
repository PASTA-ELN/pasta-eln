""" Common functions in a number of widgets """
import platform, subprocess, os
from enum import Enum
from pathlib import Path
from typing import Any, Union
from PySide6.QtWidgets import QMenu, QWidget  # pylint: disable=no-name-in-module
from PySide6.QtCore import     QPoint # pylint: disable=no-name-in-module
from ..guiStyle import Action
from .details import Details
from .form import Form


def initContextMenu(widget:Union[Details,Form], pos:QPoint) -> None:
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
    choices= {key:value for key,value in extractors.items() if key.startswith(baseDocType)}
    for key,value in choices.items():
      Action(value,                     widget, [CommandMenu.CHANGE_EXTRACTOR, key], context)
    context.addSeparator()
    Action('Save image',                widget, [CommandMenu.SAVE_IMAGE],            context)
  # Action('Open file with another application', widget.changeExtractor, context, widget, name='_openExternal_')
  Action('Open folder in file browser', widget, [CommandMenu.OPEN_FILEBROWSER],      context)
  Action('Hide',                        widget, [CommandMenu.HIDE],                  context)
  context.exec(widget.mapToGlobal(pos))
  return


def executeContextMenu(widget:Union[Details,Form], command:list[Any]) -> bool:
  """
  Execute context menu command

  Args:
    widget (QWidget): parent widget
    command (list): command

  Returns:
    bool: success
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
    widget.doc = widget.comm.backend.db.getDoc(widget.docID)
  elif command[0] is CommandMenu.CHANGE_EXTRACTOR:
    widget.doc['-type'] = command[1].split('/')
    #any path is good since the file is the same everywhere; data-changed by reference
    widget.comm.backend.useExtractors(filePath, widget.doc['shasum'], widget.doc)
    if len(widget.doc['-type'])>1 and len(widget.doc['image'])>1:
      widget.doc = widget.comm.backend.db.updateDoc({'image':widget.doc['image'], '-type':widget.doc['-type']}, widget.doc['_id'])
    else:
      return False
  else:
    print(f'**ERROR: command not found in _contextMenu {command}')
  return True


class CommandMenu(Enum):
  """ Commands used in this file """
  CHANGE_EXTRACTOR = 2
  SAVE_IMAGE       = 3
  OPEN_FILEBROWSER = 4
  OPEN_EXTERNAL    = 5
  HIDE             = 6
