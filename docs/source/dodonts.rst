.. _dodonts:

Guidelines for data management in PASTA-ELN
*******************************************

There are a few guidelines that apply to research data management and storage. PASTA-ELN supports scientists in adhering to those ideas.

Plan and maintain a project structure
---------------------------------------
Good research data management practices resemble those of the actual paper laboratory notebooks and aim to keep the entries structured and well-organized.

Whether one uses PASTA-ELN with a task-based approach for ongoing research or to store existing data (:ref:`see user stories<Planning based research>`), it is helpful to decide on the project's structure during the planning stage. For this purpose, a scientist may update the metadata definitions of a project. The default project structure is inspired by agile project planning (:ref:`...<motivation>`).

Data files and other entries should have self-explanatory names, comments and tags and possibly other metadata to describe their context. PASTA-ELN allows users to add tags to increase the search-ability of data. These practices make the data accessible and comprehensible for the author and other scientists in collaborative research projects.

Do not delete data
------------------

Data should never be deleted because one could use that process to get to a particular result: if one deletes all data that show 'swans can be black', the result will be 'all swans are white'. Such deletion can cause misrepresentation of results and falsification of conclusions and, therefore, can be classified as scientific misconduct. Moreover, the deletion of data hinders the reproducibility of scientific studies.

PASTA-ELN  has the "Hide" option, which only allows the user to hide data files and other items within the projects to achieve a better overview. As such, any data loss is prevented, as in any good ELN.

Raw data is the source of truth
-------------------------------

Sometimes raw data is compressed to save disc space. For example, users convert Tif images to low-resolution Jpeg files because that saves storage. Those Jpeg files lack metadata that Tif images have - some vendors put 500 entries in Tif images. To omit such a drawback, one could separately save the Jpeg image and the associated metadata. However, the Jpeg format works with wavelets to save space, altering the image when zooming in. Compared to the original Tif images, Jpeg images do not allow for data analysis because the results are affected by those waves. To this end, PASTA-ELN extracts data, metadata, and image always from the raw images and discourages the use of jpeg.

Graphical output of the instrument software has little use
----------------------------------------------------------

Software that is provided by the instrument manufacturer, and used during an experiment, often allows a scientist to save measurements as images or graphs. While this method is convenient for getting a fast overview of results, it is not helpful for publications, data analysis, etc., because it lacks the accuracy and 'provenance' of data. PASTA-ELN only extracts data and metadata from raw data files, not exported images.

Exported data from instrument software is only the second-best option
---------------------------------------------------------------------

Software that is provided by the instrument manufacturer also often allows a scientist to export data to the csv-format. Sometimes, there is no other option, and the scientist can only use that exported data that is still better than the output image or graph. However, one should always remember that the exported data files often contain pre-processed data instead of raw data, complicating data analysis. Moreover, the data files produced from an experiment often exclude the possibility of extracting and managing the corresponding metadata.

Reading and analyzing the raw binary files provides better input for the following data analysis because raw binary files contain the full accuracy of data, calibration, and other metadata settings. Thus, raw data allows the scientist to identify outliers, and trends, and have full freedom for its processing. PASTA aims to extract raw data from the data files, which is similar to MARBLE, the software for deciphering proprietary binary datafiles that scientists from IAS-9 and IEK-2 developed.

Data in Excel files has advantages / disadvantages compared to .csv files
-------------------------------------------------------------------------

Microsoft Excel is not scientific tool, however .xlsx and .csv are acceptable data formats as they use a high precision, compared to many .csv formats, that have less precision but allow the user to look into the file header. Moreover, .xls(x) files group experiments into different sheets which packages similar experiments into one file thereby increasing the context of each test resulting in convenience.

Smaller topics:
---------------


- Note-taking apps like Microsoft One-Note are no replacements for ELNs: Note-taking apps do not lead to structured research data.
- Personal information should not be inside public research data. European privacy legislation is pretty strict in that.
- One should follow the simple rule: share as much as possible: procedures, metadata, etc.
