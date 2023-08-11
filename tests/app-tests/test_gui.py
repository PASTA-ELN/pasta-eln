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


def test_app_launch(gui: object) -> object:
    """
    Testing the application launch
    @type gui: object
    @param gui: Gui fixture passed during the test
    """
    print("Running test_app_launch....")
    app, image_viewer, qtbot = gui
    assert image_viewer.sidebar is not None, "Sidebar not loaded!"
    assert image_viewer.sidebar.widgetsList is not None, "Widgets not loaded!"
    assert len(image_viewer.sidebar.widgetsList) == 3, "Widgets count does not match"

