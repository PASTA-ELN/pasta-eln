.. _gui:

Using the PASTA-ELN GUI
=======================

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Using the PASTA-ELN GUI</h2>
      </div>
   </div>

PASTA-ELN is organized around the currently selected project. The main window
contains four areas:

* **Projects**: Select a project, create a project with **+**, or show hidden
  projects.
* **Home**: Browse the selected project's folder and item hierarchy.
* **Common Lists**: Open lists of measurements, samples, workflows, devices,
  tags, and unidentified items. Available item types may depend on the project
  group configuration.
* **Details**: View or edit the selected item. Select an item again to close
  the details pane.

Common actions
--------------

The following table gives the shortest route to the most common tasks.

.. csv-table::
   :widths: 35, 65
   :header-rows: 1

   Goal,Where to find it
   Add a project,Click **+** in the Projects area
   Add a folder,Use **Add subfolder** or the project-tree context menu
   Add an item,Use the project-tree context menu: **Add item**
   Import files,Use **Project > Import file(s)** or drag files onto a folder
   Scan files,Use the project **More > Scan** menu
   Edit metadata,Select an item and choose **Edit** in the Details pane
   Configure data types,Use **Project group > Configure > Item type editor**
   Configure definitions,Use **Project group > Configure > Definitions editor**
   Publish a project,Use **Project > Upload to repository**

Project visibility and files
----------------------------

The **Display** menu in the project view controls whether hidden items and
project details are shown, and whether the hierarchy is displayed compactly or
in full. The **More** menu also contains project editing and project-specific
add-ons.

Files can be imported directly into a selected folder by drag-and-drop. The
project **Scan** action checks the project directory for files and folders that
are not yet represented in the database and runs applicable extractors.

Important and advanced actions
------------------------------

Some operations affect stored data or external services:

* **Project > Export project to .eln** and **Import .eln into project** exchange
  complete project packages.
* **Project > Delete current project** permanently removes the project from the
  database and should be used only after checking the project selection.
* **Project group > Synchronize** exchanges data with a configured elabFTW
  server. The available send/get actions depend on the installation.
* **Other > Configuration > Repository** stores and verifies Zenodo or Dataverse
  connection details. The upload dialog allows the metadata and item types to
  be reviewed before uploading.

For table-specific operations such as filtering, CSV export, sequential editing,
or rerunning extractors, use the **Actions**, **View**, and **More** menus above
the relevant list. These controls are intentionally kept close to the list
because they apply only to that item type.

Configuration
-------------

Open **Other > Configuration** to change the following:

* **Project group**: local data paths, add-on paths, common folders, and
  optional elabFTW settings.
* **Interface**: theme, hidden-item behavior, window sizes, logging, upload,
  and extractor limits.
* **Author**: author and organization information used in metadata.
* **Repository**: Zenodo and Dataverse URLs, API keys, and Dataverse selection.
* **Add-on parameters**: settings required by installed add-ons.
* **Setup**: installation repair, shortcut creation, and example data.

The **Item type editor** and **Definitions editor** are intended for users who
maintain a project group's data structure. Changes to these settings affect
forms and list columns for subsequent use.
