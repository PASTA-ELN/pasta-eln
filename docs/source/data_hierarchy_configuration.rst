.. |EditorWindow| image:: _static/data_hierarchy_editor.png
  :width: 700
  :alt: The screen capture of the data hierarchy editor main window

.. |TypesComboBox| image:: _static/types_combo_box.png
  :width: 200
  :alt: The screen capture of the types list in data hierarchy editor main window

.. |MetadataGroupComboBox| image:: _static/metadata_group_combobox.png
  :width: 200
  :alt: The screen capture of the metadata group list in data hierarchy editor main window


Data Hierarchy Configuration
****************************

Data hierarchy editor tool allows the user to adapt the existing data types in the database used by PASTA Application.
User can enter/edit two **types** in general using the tool:

- Structure level type for which the title is reserved (x0, x1, x2, ... xn) and cannot be used for normal types
- A generic type for which the title and label can be defined by the user without any restriction

Data Hierarchy editor tool displays all the available types in a combo list and user can select/add/delete the necessary one.

|TypesComboBox|

User can also select/add/delete a new metadata group associated with the selected type. Once selected, the metadata from the group will be displayed in the metadata table. A "default" group will always be present and the user can add new ones as needed.

|MetadataGroupComboBox|

A metadata table is also displayed in UI which lists all the associated metadata for the selected metadata group in UI for the respective type. Every group should contain two minimum required metadata which are **-name** and **-tags**. If any group miss them, the save operation will not succeed prompting with an error message. Users can add as many as needed metadata to the group.

For every type, there is also an associated attachment table shown in UI, which allows user to enter/delete new/existing associated attachment to the type.

Once when all the edits are done by the user, the changes can be saved by clicking the **save** button or to discard all the changes the **cancel** button can be used.

For more information, refer the user documentation attached below.

Usage
=====

Inorder to open the data hierarchy tool, follow the below given steps:

- Run the PASTA Application
- Go to **System | Data Hierarchy Editor** or press **F8**
- An                editor will be opened with the loaded data from the database as shown in the picture below

|EditorWindow|

- For the detailed user manual, please refer the document below

.. raw:: html

    <object width="700" height="400" type="application/pdf" data="_static/Data_Hierarchy_Editor_Manual.pdf?#zoom=50&scrollbar=0&toolbar=1&navpanes=0">
        <p>Failed to display the user manual, <a href = "_static/Data_Hierarchy_Editor_Manual.pdf">Click here to download the document.</a></p>
    </object>
