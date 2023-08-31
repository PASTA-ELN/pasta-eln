from PySide6.QtWidgets import QLabel, QHBoxLayout, QListWidget, QDialogButtonBox, QDialog, QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QScrollArea, QCheckBox, QPushButton
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from rdflib import Graph, Namespace, URIRef
import requests, json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.desc_list = []

        self.setWindowTitle("Work in Progress!")
        self.setMinimumSize(QSize(400,400))

        #mainWidget
        mainWidget = QWidget()
        mainLayout = QVBoxLayout()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        #InputLine
        self.inputLine = QLineEdit()
        self.inputLine.returnPressed.connect(self.execute_button) # Press enter to search
        self.inputLine.setClearButtonEnabled(True)
        self.inputLine.setPlaceholderText("Search for Definitions in Wikis/Ontologies")
        mainLayout.addWidget(self.inputLine)

        #outputList
        self.outputList = QListWidget()
        mainLayout.addWidget(self.outputList)

        #executeButton
        executeButton = QPushButton("Start Execution")
        executeButton.clicked.connect(self.execute_button)
        mainLayout.addWidget(executeButton)


    def execute_button(self):
        """
        Function for the executeButton
        """
        if self.inputLine.text() != "":
            self.outputList.clear()
            
            x = self.inputLine.text().split(sep=",")
            searchterms = [s.strip() for s in x]

            nested_def_list = self.definition_search(searchterms)
            for def_list in nested_def_list:
                self.outputList.addItems(def_list)

    def definition_search(self, searchterms):
        """Opens the Definition Dialog and returns a nested list
        of the links to all chosen definitions (as str) for each term 

        Args:
            searchterms (list(str)): a list of search terms
        """
        returned_definitions = []
        self.temp_def_list = [] #list of chosen definitions for single searchterm; filled by dialog
        for searchterm in searchterms:
            def_dialog = DefinitionDialog(searchterm, self)
            if def_dialog.exec():
                returned_definitions.append(self.temp_def_list)
                self.temp_def_list = []
            else:
                break      
        return returned_definitions


class DefinitionDialog(QDialog):
    def __init__(self, searchterm, parent=None):
        """ Opens a Dialog which displays definitions for the given searchterm
            and returns chosen definitions as a list
        Args:
            searchterm (str): The term you search for
        """
        super().__init__(parent)
        
        #variables
        self.parent = parent
        self.listCB = []
        self.nested_widgets = []
        self.search_term = searchterm
        
        #icons
        self.wikipedia_pixmap = self.pixmap_from_url("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Wikipedia_Logo_Mini.svg/240px-Wikipedia_Logo_Mini.svg.png")
        self.wikidata_pixmap = self.pixmap_from_url("https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Wikidata-logo.png/234px-Wikidata-logo.png")
        self.ols_pixmap = self.pixmap_from_url("https://www.ebi.ac.uk/ols/img/OLS_logo_2017.png")
        self.tib_pixmap = self.pixmap_from_url("https://service.tib.eu/ts4tib/img/TIB_Logo_en.png")

        #Widget setup
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Choose any Definitions")
        self.setMinimumSize(QSize(600,200))

        #ScrollArea
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout.addWidget(self.scrollArea)

        #Ok and Cancel Buttons
        btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.finalize)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)

        if self.search_term != "":
            self.wikipedia_search()
            self.wikidata_search()
            self.ols_search()
            self.tib_search()

        
        for widget in self.nested_widgets:
            self.scrollLayout.addWidget(widget)


    def finalize(self):
        for cb in self.listCB:
            if cb[0].isChecked():
                self.parent.temp_def_list.append(cb[1])
        self.accept()
    
    def wikipedia_search(self):
        number_of_results = 5
        base_url = "https://en.wikipedia.org/w/rest.php/v1/search/page"
        response = requests.get(base_url, params={'q': self.search_term, 'limit': number_of_results})
        if response.status_code != 200:
            print("Wikidata: Request failed with status Code:"+ response.status_code)
            return
        response = json.loads(response.text)
        for page in response["pages"]:
            if page['description'] is not None and page['description'] != "Topics referred to by the same term":
                self.listCB.append((QCheckBox(page["title"]+": "+page["description"]),
                                    "https://en.wikipedia.org/w/index.php?curid="+str(page["id"])))
                current = self.listCB[-1]
                self.nested_widgets.append(self.cb_and_image_widget(current[0], self.wikipedia_pixmap))

    def wikidata_search(self):
        base_url = "https://www.wikidata.org/w/api.php"
        response = requests.get(base_url, params={"search": self.search_term, "action":"wbsearchentities", "format":"json","language":"en","type":"item","continue":"0",})
        if response.status_code != 200:
            print("Wikidata: Request failed with status Code:"+ response.status_code)
            return
        response = json.loads(response.text)
        response = response["search"]
        for result in response:
            a = result['display']
            if 'description' in a:
                label = a['label']
                description = a["description"]
                self.listCB.append((QCheckBox(label['value']+": "+description['value']), 
                                    result["concepturi"]))
                current = self.listCB[-1]
                self.nested_widgets.append(self.cb_and_image_widget(current[0], self.wikidata_pixmap))

    def ols_search(self): #some Ontologies do not provide a description in the json
        base_url = "http://www.ebi.ac.uk/ols/api/search"
        response = requests.get(base_url, params= {"q": self.search_term})
        if response.status_code != 200:
            print("Ontology Lookup Service: Request failed with status Code:"+ response.status_code)
            return
        response = response.json()
        response = response["response"]
        for result in response['docs']:
            if 'description' in result and result['description'] is not None:
                self.listCB.append((QCheckBox(result["label"]+": "+"".join(result["description"])+" ("+result["ontology_name"]+")"),
                                    result["iri"]))
                current = self.listCB[-1]
                self.nested_widgets.append(self.cb_and_image_widget(current[0], self.ols_pixmap))

    def tib_search(self):#some Ontologies do not provide a description in the json, this is handled by the devs of tib
        base_url = "https://service.tib.eu/ts4tib/api/search"
        response = requests.get(base_url, params={"q": self.search_term})
        if response.status_code != 200: #useless for some errors because requests.get raises exceptions
            print("TIB Terminology Service: Request failed with status Code:"+ response.status_code)
            return
        response = response.json()
        response = response["response"]
        #ontologies that are both found in ols and tib:
        duplicate_ontos = ["afo", "bco", "bto", "chiro", "chmo", "duo", "edam", "efo", "fix", "hp", "iao", "mod", "mop", "ms", "nmrcv", "ncit", "obi", "om", "pato", "po", "proco", "prov", "rex", "ro", "rxno", "sbo", "sepio", "sio", "swo", "t4fs", "uo"]
        for result in response['docs']:
            if 'description' in result and result['description'] is not None and not result["ontology_name"] in duplicate_ontos:
                self.listCB.append((QCheckBox(result["label"]+": "+"".join(result["description"])+" ("+result["ontology_name"]+")"), 
                                    result["iri"]))
                current = self.listCB[-1]
                self.nested_widgets.append(self.cb_and_image_widget(current[0], self.tib_pixmap))

    def pixmap_from_url(self, url):
        image = requests.get(url)
        pixmap = QPixmap()
        pixmap.loadFromData(image.content)
        pixmap = pixmap.scaled(40,40, Qt.KeepAspectRatio)
        return pixmap

    def cb_and_image_widget(self, checkbox, pixmap):
        nested_widget = QWidget()
        nested_widget.setStyleSheet("font-size: 17px")
        nested_layout = QHBoxLayout()
        nested_label = QLabel()
        nested_label.setPixmap(pixmap)
        nested_widget.setLayout(nested_layout)
        nested_layout.addWidget(checkbox)
        nested_layout.addWidget(nested_label)
        return nested_widget


app = QApplication()
window = MainWindow()
window.show()
app.exec()