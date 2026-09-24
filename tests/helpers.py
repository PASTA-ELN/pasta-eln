""" Shared helpers for the GUI/backend tests """
from typing import Any


def waitForBackend(qtbot:Any, comm:Any, timeout:int=30_000) -> None:
  """ Wait until the backend worker has finished initialize()

  Args:
    qtbot (QtBot): pytest-qt fixture
    comm (Communicate): communication object whose backend is started
    timeout (int): maximum waiting time in ms
  """
  qtbot.waitUntil(lambda: bool(comm.docTypesTitles) and
                  set(comm.dataHierarchyNodes) >= set(comm.docTypesTitles), timeout=timeout)
