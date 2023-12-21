#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_pasta_app_ui.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pasta_eln.gui import MainWindow
from tests.app_tests.common.fixtures import pasta_gui


class TestPastaAppUI(object):
  @pytest.mark.skip(
    reason="Disabled until the PASTA GUI app is modified for the latest schema changes in data hierarchy data")
  def test_app_launch(self, pasta_gui: tuple[Union[QApplication, QCoreApplication, None], MainWindow, QtBot]):
    app, image_viewer, qtbot = pasta_gui
    assert image_viewer.sidebar is not None, "Sidebar not loaded!"
    assert image_viewer.sidebar.widgetsList is not None, "Widgets not loaded!"
    assert len(image_viewer.sidebar.widgetsList) == 3, "Widgets count does not match"
