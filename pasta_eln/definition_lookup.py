from PySide6.QtWidgets import QListWidget, QDialogButtonBox, QDialog, QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QScrollArea, QCheckBox, QPushButton
from PySide6.QtCore import QSize 
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
            #self.sort_for_weight(self.outputList)

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

    """def sort_for_weight(self, def_list):
        self.source_counter = Counter()
        for definition in def_list:
            a = definition.rfind("(")
            b = definition.rfind(")")
            print(definition[a+1:b])
            self.source_counter[definition[a+1:b]] += 1"""


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
        self.search_term = searchterm
        
        #Widget setup
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Choose any Definitions")

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
        for cb in self.listCB:
            self.scrollLayout.addWidget(cb[0])

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
                self.listCB.append((QCheckBox(page["title"]+": "+page["description"]+" (Wikipedia)"),"https://en.wikipedia.org/w/index.php?curid="+str(page["id"])))
                #https://en.wikipedia.org/w/index.php?curid=82974 link to each article using the id parameter

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
                self.listCB.append((QCheckBox(label['value']+": "+description['value']+" (Wikidata)"), result["concepturi"]))

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
                self.listCB.append((QCheckBox(result["label"]+": "+"".join(result["description"])+" ("+result["ontology_name"]+")"), result["iri"]))

    def tib_search(self):#some Ontologies do not provide a description in the json, this is handled by the devs of tib
        base_url = "https://service.tib.eu/ts4tib/api/search"
        response = requests.get(base_url, params={"q": self.search_term})
        print(response)
        if response.status_code != 200: #useless for some errors because requests.get raises exceptions
            print("TIB Terminology Service: Request failed with status Code:"+ response.status_code)
            return
        response = response.json()
        response = response["response"]
        #ontologies that are both found in ols and tib:
        duplicate_ontos = ["afo", "bco", "bto", "chiro", "chmo", "duo", "edam", "efo", "fix", "hp", "iao", "mod", "mop", "ms", "nmrcv", "ncit", "obi", "om", "pato", "po", "proco", "prov", "rex", "ro", "rxno", "sbo", "sepio", "sio", "swo", "t4fs", "uo"]
        for result in response['docs']:
            if 'description' in result and result['description'] is not None and not result["ontology_name"] in duplicate_ontos:
                self.listCB.append((QCheckBox(result["label"]+": "+"".join(result["description"])+" ("+result["ontology_name"]+")"), result["iri"]))

app = QApplication()
window = MainWindow()
window.show()
app.exec()