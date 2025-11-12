from PySide6.QtCore import QMimeData
from PySide6.QtGui import QMouseEvent, Qt, QDrag, QPixmap, QPalette, QColor
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QPushButton, QStyle, QFrame, QVBoxLayout, QHBoxLayout

from .central_text_widget import CentralTextWidget
from .param_widget import ParamWidget
from .workplan_functions import get_procedure_default_paramaters, get_procedure_text
from ..guiCommunicate import Communicate


class StepWidget(QWidget):
    """
    A single Step containing Procedure Name, Parameters and buttons.
    """

    def __init__(self, comm: Communicate, count: int, procedure_name: str, textfield: CentralTextWidget,
                 parameters: dict[str, str] = None):
        super().__init__()
        self.comm = comm
        self.storage = self.comm.storage
        self.procedure_name = procedure_name
        self.textfield = textfield
        self.params_visible = False
        self.param_widgets = []

        # procedure_name label
        self.procedure_label = QLabel(self.procedure_name)
        self.procedure_label.setFixedWidth(150)
        self.procedure_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.procedure_label.setToolTip(self.procedure_name)

        # view text of procedure Button
        view_button = QPushButton()
        view_button.clicked.connect(self.onViewButtonClicked)
        view_button.setToolTip("View Procedure")
        view_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        view_button.setFixedSize(30, 30)
        view_button.click()

        # parameter button
        self.parameter_button = QPushButton()
        self.parameter_button.clicked.connect(self.onParameterButtonClicked)
        self.parameter_button.setToolTip(
            "View Parameters: \n Red: at least 1 missing Parameter \n Yellow: at least 1 default Parameter \n Green: "
            "All Parameters filled")
        self.parameter_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarContextHelpButton))
        self.parameter_button.setFixedSize(30, 30)

        # Delete Button
        delete_button = QPushButton()
        delete_button.clicked.connect(self.onDeleteButtonClicked)
        delete_button.setToolTip("Delete this Step")
        delete_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserStop))
        delete_button.setFixedSize(30, 30)

        # step-label
        self.label = QLabel(f"Step {count}:")
        self.label.setFixedWidth(55)

        # frame
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setFrameShadow(QFrame.Shadow.Sunken)
        frame.setLineWidth(1)
        self.vertical_layout = QVBoxLayout()
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.label)
        frame_layout.addWidget(self.procedure_label)
        frame_layout.addWidget(view_button)
        frame_layout.addWidget(self.parameter_button)
        frame_layout.addWidget(delete_button)
        self.vertical_layout.addLayout(frame_layout)
        frame.setLayout(self.vertical_layout)

        # layout
        layout = QHBoxLayout()
        layout.addWidget(frame)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setLayout(layout)

        # add Parameter-Widgets to the layout and hide them
        if not self.param_widgets:
            default_parameters = get_procedure_default_paramaters(self.procedure_name, self.comm)
            if parameters is None:
                parameters = default_parameters
            for key in default_parameters:
                param_widget = ParamWidget(key, default_parameters[key], parameters[key])
                param_widget.setVisible(False)
                param_widget.line_edit.textChanged.connect(self.highlight_param_button)
                self.param_widgets.append(param_widget)
                self.vertical_layout.addWidget(param_widget)

        # check for parameters and highlight button, if there are any
        self.highlight_param_button()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Override to create a visual effect of dragging.
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())

            drag.exec(Qt.DropAction.MoveAction)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Override to display the text of a step on click.
        """
        self.onViewButtonClicked()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """
        Override to display parameters of a step on double click.
        """
        self.onParameterButtonClicked()

    def onViewButtonClicked(self) -> None:
        """
        Click View Button to display text in TextWidget.
        """
        self.textfield.textedit.setMarkdown(get_procedure_text(self.procedure_name, self.comm))

    def onParameterButtonClicked(self) -> None:
        """
        Click Parameter Button to display parameters in StepWidget.
        """
        if self.params_visible:
            self.params_visible = False
            for widget in self.param_widgets:
                widget.setVisible(False)
        else:
            self.params_visible = True
            for widget in self.param_widgets:
                widget.setVisible(True)

    def onDeleteButtonClicked(self) -> None:
        """
        Click Delete Button to delete StepWidget.
        """
        self.parent().remove_step(self)

    def highlight_param_button(self) -> None:
        """
        Highlights the parameter_button green/yellow/red depending on filled/default/empty parameters
        """
        color = '#8fce00'
        for widget in self.param_widgets:
            if not widget.line_edit.text():
                color = '#f1c232'
                if not widget.line_edit.placeholderText():
                    color = "#cc0000"
                    break
        self.parameter_button.setStyleSheet(f'background-color: {color}')
