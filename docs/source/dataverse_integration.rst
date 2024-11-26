.. |DataverseUploadUI| image:: _static/dataverse_ui.png
  :width: 700
  :alt: Dataverse upload UI Screenshot.

.. |DataverseConfigurationUI| image:: _static/dataverse_config_ui.png
  :width: 700
  :alt: Dataverse Configuration UI Screenshot.

.. |DataverseUploadMainUI| image:: _static/dataverse_upload_main_ui.png
  :width: 700
  :alt: Dataverse main upload UI Screenshot.

.. |DataverseUploadHistoryUI| image:: _static/dataverse_upload_history.png
  :width: 700
  :alt: Dataverse upload history UI Screenshot.

.. |DataverseMetadataEditorUI| image:: _static/dataverse_metadata_editor.png
  :width: 700
  :alt: Dataverse metadata editor UI Screenshot.

.. |DataverseUploadConfigurationUI| image:: _static/dataverse_upload_config.png
  :width: 700
  :alt: Dataverse metadata editor UI Screenshot.


Dataverse Integration
*********************

|DataverseUploadUI|

Dataverse integration feature enables user to publish the PASTA projects on the `Dataverse platform <https://dataverse.org/>`_. The feature allows the user to configure a particular dataverse instance on which the projects will be published. The dataverse instance can be configured in the user preferences.

The main intend behind this integration is to bring data `FAIR-ness <https://dataverse.org/presentations/fair-data-management-and-fair-data-sharing>`_ in the PASTA Application and to provide a way for users to make their data available to other researchers.

PASTA projects will be packaged as part of the ELN file and uploaded to the dataverse instance. User can configure the number of parallel uploads and the number of items to be packaged as part of the ELN file. Also the user can configure the metadata used for the creation of datasets in the dataverse instance. Once the required configuration is done, the user can start uploading the PASTA projects to the dataverse instance. There is also a possibility to upload multiple projects at a time. Make sure to configure at least the minimal set of metadata (subject, author, dataset contact & dataset description) required for the dataverse upload. Otherwise the upload will lead to an appropriate error message.

An individual upload process will be composed of the following steps:

- *Generate ELN file for the project*
- *Create a dataset in dataverse*
- *Publish the dataset in dataverse with the metadata configured by the user*
- *Upload the ELN file to the published dataset*



The following features are available as part of the dataverse integration:

- **Dataverse Configuration UI**: The user can configure the dataverse instance (server url, api token and dataverse id) on which the projects will be published. The screen capture of the dataverse Configuration UI |DataverseConfigurationUI|
- **Dataverse Upload UI**: The main UI where the user can upload the PASTA projects to the dataverse instance. The screen capture of the dataverse UI |DataverseUploadMainUI|
- **Dataverse Upload History UI**: The user can view the history of the uploaded projects to the dataverse instance. The screen capture of the dataverse upload history UI |DataverseUploadHistoryUI|
- **Dataverse Metadata Editor UI**: The user can edit the metadata used for the creation of datasets in dataverse which are associated with the PASTA projects. The screen capture of the dataverse upload history UI |DataverseMetadataEditorUI|
- **Dataverse Upload Configuration UI**: The user can define the configuration parameters (number of parallel uploads, items to pe packaged as part of the ELN file etc. ) used for dataverse upload. The screen capture of the dataverse upload history UI |DataverseUploadConfigurationUI|

Upload Usage
=============

Inorder to open the dataverse upload tool, follow the below given steps:

- Run the PASTA Application
- Go to **Project group | Upload to dataverse** or press **F11**
- An upload dialog will be opened with the loaded PASTA projects

|DataverseUploadUI|

- For the detailed user manual, please refer the document below

.. raw:: html

    <object width="700" height="400" type="application/pdf" data="_static/Dataverse_Integration_Manual.pdf?#zoom=50&scrollbar=0&toolbar=1&navpanes=0">
        <p>Failed to display the user manual, <a href = "_static/Dataverse_Integration_Manual.pdf">Click here to download the document.</a></p>
    </object>
