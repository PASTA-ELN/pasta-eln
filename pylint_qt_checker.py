from pylint.checkers import BaseChecker
import astroid

class QtLocalWidgetChecker(BaseChecker):
  name = 'qt-local-widget-checker'
  priority = -1
  msgs = {'W0001': ('"%s" assigned as local variable — use self.%s to avoid GC issues.',
                  'qt-local-widget',
                  'Qt widgets used beyond construction should be assigned to instance variables.')}
  qt_classes = {'QPushButton', 'QLineEdit', 'QCheckBox', 'QComboBox', 'QSlider', 'QTextEdit', 'QTableView',
                'QTreeView', 'QTimer', 'QShortcut'}

  def visit_assign(self, node: astroid.nodes.Assign):
    try:
      rhs = node.value
      if isinstance(rhs, astroid.Call):
        if isinstance(rhs.func, astroid.Attribute) or isinstance(rhs.func, astroid.Name):
          widget_type = rhs.func.attrname if isinstance(rhs.func, astroid.Attribute) else rhs.func.name
          if widget_type in self.qt_classes:
            for target in node.targets:
              if isinstance(target, astroid.AssignName) and not target.name.startswith("self."):
                self.add_message('qt-local-widget', node=node, args=(widget_type, target.name))
    except Exception:
      pass
