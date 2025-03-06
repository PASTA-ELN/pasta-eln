from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout

from pasta_eln.GUI.workflow_creator_dialog.central_text_widget import CentralTextWidget
from .common_workflow_description import Storage
from .step_widget import StepWidget


class StepList(QWidget):
    """
    Displays a list of StepWidgets which can be rearranged.
    """

    def __init__(self, storage: Storage, textfield: CentralTextWidget):
        super().__init__()
        self.storage = storage
        self.textfield = textfield

        self.setAcceptDrops(True)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """
        Override to enable dragging of the elements in the list.
        """
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """
        Override to enable dropping elements into the list. And placing them at the right position in the list.
        """
        if self.layout.count() >= 2:
            pos = event.pos()
            widget = event.source()
            self.layout.removeWidget(widget)
            n = 0
            for n in range(self.layout.count()):
                w = self.layout.itemAt(n).widget()
                if pos.y() < w.y() + w.size().height() // 2:
                    break
            else:
                n += 1
            self.layout.insertWidget(n, widget)

        event.accept()
        self.rename_steps()

    def add_new_step(self, procedure_name: str, parameters: dict[str, str] = None) -> None:
        """
        Adds a new step to the list.
        :param procedure_name: Name of the step to be added.
        :param parameters: matching parameters to be added to the step.
        """
        self.layout.addWidget(
            StepWidget(self.storage, self.layout.count() + 1, procedure_name, self.textfield, parameters))

    def rename_steps(self) -> None:
        """
        Changes the number of each step in the list, to match their position in the list.
        """
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, StepWidget):
                widget.label.setText(f"Step {i + 1}:")

    def get_procedures(self) -> list[str]:
        """
        :return: List of current procedure names currently in the StepList.
        """
        procedures = []
        for stepwidget in self.children()[1:]:
            if isinstance(stepwidget, StepWidget):
                procedures += [stepwidget.procedure_label.text()]
        return procedures

    def get_parameters(self) -> list[dict[str, str]]:
        """
        :return: List of {parameter names: value} dictionary for each procedure in the StepList.
        """
        parameters = []
        for stepwidget in self.children()[1:]:
            if isinstance(stepwidget, StepWidget):
                par = {}
                for paramwidget in stepwidget.param_widgets:
                    widget_text = paramwidget.line_edit.text()
                    if widget_text:
                        par[paramwidget.param] = widget_text
                    else:
                        par[paramwidget.param] = paramwidget.line_edit.placeholderText()
                parameters.append(par)
        return parameters

    def remove_step(self, widget_to_remove) -> None:
        """
        remove the given widget from the StepList.
        :param widget_to_remove: StepWidget to remove from the list.
        """
        self.layout.takeAt(self.layout.indexOf(widget_to_remove))
        widget_to_remove.deleteLater()
        self.rename_steps()
