def register(linter):
  """Register the repository's custom pylint checker.

  Args:
    linter (PyLinter): Pylint linter instance receiving the checker.
  """
  from pylint_qt_checker import QtLocalWidgetChecker
  linter.register_checker(QtLocalWidgetChecker(linter))
