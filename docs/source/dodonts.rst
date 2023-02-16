.. _dodonts:

Dos and Do-nots
***************

There are a few ideas that apply to research data. PASTA-ELN support the scientists in adhering to those ideas.

Do not delete data
  Data should never be deleted because one could use that process to get to a particular result: if one deletes all data that show 'swans can be black', the result will be 'all swans are white'.

  PASTA-ELN allows the user to hide data to achive a better overview. But data is never deleted, as in any good ELN.


Raw data is the source of truth
  Sometimes raw data is converted to low resolution to save space: users convert Tif images to Jpeg-files because that saves storage.

  That Jpeg-files lack metadata that Tif images have - some vendors put 500 entires in Tif images. One could separately save metadata and the Jpeg-image. However, Jpeg works with wavelets to save space which alters the image if you zoom in. Compared to original Tif images, Jpeg images do not allow for data analysis because the results are affected by those waves. To this end, PASTA-ELN extracts data, metadata and image always from the raw images.


Diagrams of the instrument software have little use
  Software that is connected to the instrument often allows you to save plots as images. While this method is convenient for getting a fast overview, it is not helpful for publications, data analysis, ... because it lacks the accuracy and 'provenace' of data.

  PASTA-ELN should only extract from raw data files, not exported images.


Exported data from instrument software is only the second best option
  Software that is connected to the instrument often allows you to export data to the csv-format. Sometimes, there is no other option and the scientist should use that exported data that is better than the diagram-image.

  Even better, reading the binary raw data because that data contains the full accuracy of data, it contains calibration and other metadata settings which can help you to identify outliers, trends...
