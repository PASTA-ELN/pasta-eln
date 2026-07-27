GUI Design:

- So viel wie möglich Standard-PySide6 und dem Theme überlassen
    - Nur Stylesheet / Farben / Größe manuell ändern, wenn es im Standard Style nicht sichtbar/lesbar genug ist.
    - In jedem Element (Sidebar, Table, Details) gibt es maximal einen Knopf der gehighlighted wird (Default-Property =
      True)
- Versuchen, das Figma-Design nachzubauen, so wie technisch möglich und nicht zu kompliziert.
    - Trotzdem jedes Element nochmal nach Notwendigkeit überprüfen.
    - Die Änderungen, die durch die PySide6 Implementierung entstehen, benutzen, um das Design anzupassen.
        - (Beispiel: Sidebar hat in Figma einen Knopf zum Öffnen/Schließen --> Pyside macht das per Slider, also kann
          man den Knopf für was anderes benutzen --> Stattdessen New-Project Knopf.)
- Wenn möglich, Icon und Text Anzeigen. Nur Icons führt zu Unsicherheit
    - Icons von "ri.iconname"
    - Wenn ein Icon ohne Text steht, dann sollte es sehr offensichtlich sein, was das Icon bedeutet.
- Farben
    - Am besten die Farben nicht manuell ändern, manchmal jedoch notwendig
    - Immer die Farben aus dem theme benutzen (siehe palette.py), ist manchmal kompliziert.
    - Icons müssen meistens manuell eingefärbt werden (Siehe project_sidebar oder table_view)
    - Light und Dark Theme ausprobieren, sollte mit dem theme jedoch immer lesbar sein.
- Beispielprojekt mit sehr sehr langen Namen in jedem Feld erstellen, um zu sehen, ob das Layout bricht.
  - Auch leere und sehr kurze Namen testen
  - Lieber durch das Layout diese probleme lösen, als hart einen String abzuschneiden, damit man im Zweifel auch den 
    ganzen Namen sich anzeigen lassen kann. (z.B. kann man in der table_view die Spalten größer ziehen.)
- Viele Aktionen, die durch Knöpfe möglich sind, sollten auch in einem Rechtsklick-Menu möglich sein.
  - Die meisten Aktionen in Rechtsklick-menus sollten auch mit Knöpfen durchführbar sein
  - Rechtsklick menus bei Projekten in der Sidebar und auf Einträge in der Table-view sind am wichtigsten.
- Umso wichtiger die Aktion, desto Sichtbarer sollte sie sein und desto weniger Klicks sollten dafür nötig sein, sie 
  zu finden.
- Es sollte immer klar sein, was man gerade editiert oder anschaut (Welches Projekt, Welche Tabelle, welche Probe)

Code Design:
- Gutes Beispiel: "project_sidebar.py"
- Pylint-Regeln befolgen.
- Lieber mehr Kommentare als weniger
- In der init zuerst die Variablen definieren, die in der Klasse benötigt werden
  - Dann die einzelnen Widgets definieren und alles setzen, wie das Widget am Anfang aussehen soll
  - Dann die Layouts erstellen in dem das Widget hinzugefügt wird
  - Dann Style von dem Widget selbst ändern, wenn nötig
  - Dann das Main-Layout erstellen und alle sublayouts hinzufügen
  - Dann die Signale erstellen und connecten
  - Am Ende den Code der ausgeführt werden soll schreiben (meistens 'signal.emit')
  - Jedes Widget und Layout bekommt eigenen Block mit Kommentar
- Veränderungen bei Runtime an widgets werden in der paint-Methode gemacht.
- Lieber mehr Code in Funktionen oder neue Klassen/Dateien verlagern, das macht den Code übersichtlicher
  - Funktions-/Variablennamen können auch sehr lang sein, hauptsache sie beschreiben gut was sie machen
- Dateien, die das gleiche Widget betreffen oder Teil eines Widgets sind, zusammen in einen Ordner
  - Gerne neue Klassen/Custom-Widgets erstellen, wenn ein Sub-Widget zu groß wird.
- Type-hints benutzen.
