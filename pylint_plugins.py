def register(linter):
  from pylint_qt_checker import QtLocalWidgetChecker
  linter.register_checker(QtLocalWidgetChecker(linter))