#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6.QtWidgets import QLabel
from qtawesome import icon

from pasta_eln.dataverse.upload_status_values import UploadStatusValues


def update_status(status: str,
                  statusIconLabel: QLabel,
                  statusLabel: QLabel) -> None:
  """
  Updates the status and status icon of the upload.

  Explanation:
      This function updates the status and status icon of the upload based on the given status.
      It sets the text of the statusLabel and the pixmap of the statusIconLabel based on the status value.

  Args:
      status (str): The status of the upload.
      statusIconLabel (QLabel): The label to display the status icon.
      statusLabel (QLabel): The label to display the status text.

  Returns:
      None
  """
  statusLabel.setText(status)
  match status:
    case UploadStatusValues.Queued.name:
      statusIconLabel.setPixmap(icon('ph.queue-bold').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Uploading.name:
      statusIconLabel.setPixmap(icon('mdi6.progress-upload').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Cancelled.name:
      statusIconLabel.setPixmap(icon('mdi.cancel').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Finished.name:
      statusIconLabel.setPixmap(icon('fa.check-circle-o').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Error.name:
      statusIconLabel.setPixmap(icon('msc.error-small').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Warning.name:
      statusIconLabel.setPixmap(icon('fa.warning').pixmap(statusIconLabel.size()))
