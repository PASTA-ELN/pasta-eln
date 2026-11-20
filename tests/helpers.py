""" Shared helpers for the GUI/backend tests """
from typing import Any
from collections.abc import Callable
from PySide6.QtCore import QObject, Qt, SignalInstance


class Receiver(QObject):
  """ Collect the arguments of a signal in the thread of this object: the main thread """
  def __init__(self) -> None:
    super().__init__()
    self.received:list[tuple[Any, ...]] = []

  def receive(self, *args:Any) -> None:
    """ Slot for any signal
    Args:
      args (Any): signal arguments
    """
    self.received.append(args)


def waitForWorker(qtbot:Any, signal:SignalInstance, trigger:Callable[[], Any],
                  check:Callable[..., bool]=lambda *_: True, timeout:int=30_000) -> tuple[Any, ...]:
  """ Run trigger and wait for a matching worker signal
  - unlike qtbot.waitSignal, which handles a worker signal in the worker thread and cannot stop its timer

  Args:
    qtbot (QtBot): pytest-qt fixture
    signal (SignalInstance): signal of the backend worker
    trigger (Callable): action that causes the signal
    check (Callable): receives the signal arguments; True if this is the awaited signal
    timeout (int): maximum waiting time in ms

  Returns:
    tuple: arguments of the matching signal
  """
  receiver = Receiver()
  signal.connect(receiver.receive, Qt.ConnectionType.QueuedConnection)
  trigger()
  qtbot.waitUntil(lambda: any(check(*args) for args in receiver.received), timeout=timeout)
  signal.disconnect(receiver.receive)
  return next(args for args in receiver.received if check(*args))


def waitForBackend(qtbot:Any, comm:Any, timeout:int=30_000) -> None:
  """ Wait until the backend worker has finished initialize()
  - create a MainWindow before calling this: it builds its tabs on docTypesChanged, which is sent during the wait
  - Do not inline this function, contradicting the rule in AGENTS.md

  Args:
    qtbot (QtBot): pytest-qt fixture
    comm (Communicate): communication object whose backend is started
    timeout (int): maximum waiting time in ms
  """
  qtbot.waitUntil(lambda: bool(comm.docTypesTitles) and
                  set(comm.dataHierarchyNodes) >= set(comm.docTypesTitles), timeout=timeout)
