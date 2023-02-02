.. _dodonts:

Dos and Do-nots
***************

There are a few ideas that should be followed when it comes to research data. PASTA-ELN support the scientists in adhering to those ideas.

Do not delete data
  Data should never be deleted because one could use that to get to a particular result: if one deletes all the data that show 'swans can be black', the result will show that 'all swans are white'.

  PASTA-ELN allows the user to hide data to allow the user to get a better overview. But data is never deleted, as in any good ELN.


Raw data is the source of truth
  Sometimes raw data is converted to a low resolution to save space: users convert Tif images to Jepg files because that saves storage.

  That Jepg data lacks generally the metadata that Tif images have - some vendors put 500 entires in them. One could separately save the metadata and the Jepg image. Jepg works with waves to save space which alters the image if you zoom in. Compared to original Tif images, Jepg images do not allow for data analysis because the results are affected by those waves. To this end, PASTA-ELN extracts the data, metadata and image always from the raw images.


Diagrams of the instrument software have little use
  Software that is connected to the instrument often allows you to save plots in image formats. While this is convenient for getting a fast overview, it is not helpful for publications, data analysis, etc. because it lacks the accuracy and 'provenace' of the data.

  PASTA-ELN should only extract from data files, not exported images.


Exported data from instrument software is only the second best option
  Software that is connected to the instrument often allows you to export the data to the csv format. Sometimes, there is no other option and the scientist should use that exported data, which is better than the diagram image.

  However, better is reading the binary raw data because that data contains the full accuracy of the data, it contains calibration and other metadata settings which can help you greatly when identifying why one experiment was an outlier.



