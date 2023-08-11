import pytest
from pytestqt.exceptions import capture_exceptions
from pytestqt.qtbot import QtBot

from pasta_eln.gui import main_gui


@pytest.fixture(scope="module")
def qtbot_session(qapp, request):
    print("Setting up QTBOT.....")
    result = QtBot(qapp)
    with capture_exceptions():
        yield result
    print("Tearing down QTBOT.....")


@pytest.fixture(scope="module")
def gui(request):
    print("Setting up GUI...")

    app, image_viewer = main_gui()
    qtbot = QtBot(app)
    # QTest.qWait(0.5 * 1000)

    return app, image_viewer, qtbot


def test_app_launch(gui):
    print("Running test_app_launch....")
    app, imageViewer, qtbot = gui
    assert imageViewer.sidebar is not None, "Sidebar not loaded!"
    assert imageViewer.sidebar.widgetsList is not None, "Widgets not loaded!"
    assert len(imageViewer.sidebar.widgetsList) == 1, "Widgets count does not match"
