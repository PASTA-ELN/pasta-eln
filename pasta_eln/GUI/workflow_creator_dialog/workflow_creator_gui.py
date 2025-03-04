from PySide6.QtCore import Qt, QMimeData, QSize
from PySide6.QtGui import QDrag, QAction, QPixmap, QPalette, QColor, QFont, QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QHBoxLayout, QPushButton, \
    QSizePolicy, QVBoxLayout, QToolButton, QMenu, QScrollArea, QTabWidget, QFrame, QStyle, QTextEdit, QGridLayout, \
    QLineEdit, QFileDialog, QMessageBox, QDialog

from .workflow_generator import generate_workflow, get_db_procedures, get_procedure_text, \
    get_procedure_default_paramaters, \
    get_steps_from_file, get_sample_name_from_file


WINDOW_MIN_HEIGHT = 500
LIST_WIDTH = 400
TEXT_MIN_WIDTH = 200
TEXT_WIDTH = 400


class MainWindow(QMainWindow):
    """
    The main Window of the application, containing every other Widget.
    """

    def __init__(self):
        super().__init__()
        # Change the size of the window
        self.resize(self.screen().size())

        # Create the Menu Bar at the top of the screen
        file_menu = self.menuBar().addMenu("&File")
        action_new_sample = file_menu.addAction("New Sample")
        action_open_sample = file_menu.addAction("Open Sample")
        option_menu = self.menuBar().addMenu("&Options")
        option_menu.addAction("Configure Library")

        # Create the Tab Widget at the top of the screen
        tab_widget = QTabWidget()
        tab_widget.setMovable(True)
        tab_widget.setTabsClosable(True)
        tab_widget.tabCloseRequested.connect(tab_widget.removeTab)
        self.new_sample(tab_widget)

        action_new_sample.triggered.connect(lambda: self.new_sample(tab_widget))
        action_open_sample.triggered.connect(lambda: self.open_sample(tab_widget))

        self.setCentralWidget(tab_widget)

    def new_sample(self, tab_widget: QTabWidget) -> None:
        """
        Adds a new tab to the given tab widget.
        :param tab_widget: QTabWidget to add the new tab to.
        """
        sample_name = "Unnamed Sample"
        new_centralWidget = CentralWidget(sample_name)
        tab_widget.addTab(new_centralWidget, sample_name)

    def open_sample(self, tab_widget: QTabWidget) -> None:
        """
        Select a file to read a sample from. Opens a new tab with selected sample.
        :param tab_widget: QTabWidget to add the new tab to.
        :return:
        """
        # Select File
        filename, selectedFilter = QFileDialog.getOpenFileName(self, "Open Image", "", "Python Files (*.py)")
        # Try to get Steps and sample_name from File
        steps, parameters = get_steps_from_file(filename)
        sample_name = get_sample_name_from_file(filename)
        # Add Widgets to StepList
        new_centralWidget = CentralWidget(sample_name)
        for i, step in enumerate(steps):
            new_centralWidget.central_list_widget.step_list.add_new_step(step, parameters[i])
        tab_widget.addTab(new_centralWidget, sample_name)


class WorkflowDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Workflow Creator")
        layout = QVBoxLayout()
        main_window = MainWindow()
        layout.addWidget(main_window.centralWidget())
        self.setLayout(layout)


class CentralWidget(QWidget):
    """
    The central widget of the application. Containing a CentralListWidget (left) and a CentralTextWidget (right).
    """

    def __init__(self, sample_name: str):
        super().__init__()
        self.sample_name = sample_name

        # Widget that displays text of procedures
        self.central_text_widget = CentralTextWidget()

        # Widget that contains the Steplist
        self.central_list_widget = CentralListWidget(self.central_text_widget)

        # layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.central_list_widget, 0, 0)
        self.layout.addWidget(self.central_text_widget, 0, 1)
        self.layout.setColumnMinimumWidth(0, LIST_WIDTH)
        self.layout.setColumnMinimumWidth(1, TEXT_MIN_WIDTH)
        #self.layout.setColumnStretch(0,0)
        #self.layout.setColumnStretch(1, 1000)

        self.setLayout(self.layout)


class CentralTextWidget(QWidget):
    """
    The Widget on the right that displays the text describing the selected procedure.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(TEXT_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # text edit field
        self.textedit = QTextEdit()
        self.textedit.setReadOnly(True)  # Could be Changed later for comments

        # layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textedit)

        self.setLayout(self.layout)


class CentralListWidget(QWidget):
    """
    The Widget on the left that displays the StepList and buttons to show/create the Workflow.
    """

    def __init__(self, textfield: CentralTextWidget):
        super().__init__()
        self.setFixedWidth(LIST_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.textfield = textfield

    # step list
        self.step_list = StepList(self.textfield)

        # scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setWidget(self.step_list)

        # New Step Button
        new_step_button = NewStepButton(self.step_list)

        # Font for the buttons
        font = QFont()
        font.setPointSize(16)
        new_step_button.setFont(font)

        # export button
        export_button = QPushButton("Save / Export Workflow")
        export_button.clicked.connect(self.export_button_pressed)
        export_button.setFont(font)

        # layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(new_step_button)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(export_button)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(self.layout)

    def export_button_pressed(self):
        output_file = "workflow_output.py"  # Should be chosen by the user somehow
        workflow_name = "Sandia Fracture Challenge 3"  # Should be chosen by the user somehow
        library_url = "https://raw.githubusercontent.com/SteffenBrinckmann/common-workflow-description_Procedures/main"
        sample_name = self.parent().sample_name
        procedures = self.step_list.get_procedures()
        parameters = self.step_list.get_parameters()
        if not procedures:
            QMessageBox.warning(self.step_list,
                                "Export Failed",
                                "Cannot Export Workflow without Procedures")
        else:
            generate_workflow(output_file, workflow_name, library_url, sample_name, procedures, parameters)
            QMessageBox.information(self.step_list, "Export Successful", "Exported Workflow to " + output_file)


class StepList(QWidget):
    """
    Displays a list of StepWidgets which can be rearranged.
    """

    def __init__(self, textfield: CentralTextWidget):
        super().__init__()
        self.setAcceptDrops(True)
        self.textfield = textfield

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
        self.layout.addWidget(StepWidget(self.layout.count() + 1, procedure_name, self.textfield, parameters))

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


class StepWidget(QWidget):
    """
    A single Step containing Procedure Name, Parameters and buttons.
    """

    def __init__(self, count: int, procedure_name: str, textfield: CentralTextWidget,
                 parameters: dict[str, str] = None):
        super().__init__()
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
            default_parameters = get_procedure_default_paramaters(self.procedure_name)
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
        self.textfield.textedit.setMarkdown(get_procedure_text(self.procedure_name))

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
        palette = self.parameter_button.palette()
        color = Qt.GlobalColor.green

        for widget in self.param_widgets:
            if not widget.line_edit.text():
                color = Qt.GlobalColor.yellow
                if not widget.line_edit.placeholderText():
                    color = Qt.GlobalColor.red
                    break
        palette.setColor(QPalette.ColorRole.Button, QColor(color))
        self.parameter_button.setPalette(palette)
        self.parameter_button.setAutoFillBackground(True)


class NewStepButton(QToolButton):
    """
    The Button to add a new StepWidget to the current StepList.
    """

    # Depending on Amount of Procedures, the Dropdown Menu could be Exchanged for a dialog
    def __init__(self, parent: StepList):
        super().__init__(parent)
        self.procedures = get_db_procedures()

        # Configure Appearence of Button
        self.setText("Add new Step")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setMinimumSize(QSize(30, 30))

        # Configure Dropdown Menu
        self.menu = QMenu(self)
        for procedure in self.procedures:
            action = QAction(procedure, self)
            action.triggered.connect(lambda checked, name=procedure: parent.add_new_step(name))
            self.menu.addAction(action)
        self.setMenu(self.menu)


class ParamWidget(QWidget):
    """
    The Widget that contains the Parameters and QLineEdits in a StepWidget.
    """

    def __init__(self, param: str, default_value: str = "", value: str = ""):
        super().__init__()
        self.param = param
        # label
        label = QLabel(f"{self.param}:")

        # text-box
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(default_value)
        if value and default_value != value:
            self.line_edit.setText(value)
        elif value:
            self.line_edit.setPlaceholderText(value)

        # layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(label)
        self.layout.addWidget(self.line_edit)
        self.setLayout(self.layout)
