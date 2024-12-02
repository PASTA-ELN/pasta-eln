.. _dodonts:

Guidelines for Data Management in Research
******************************************

Regardless of whether PASTA-ELN is used to manage ongoing research or to store existing data, it is crucial to establish a project structure during the planning stage. This involves defining and updating metadata definitions for the project, which may be inspired by agile project planning methodologies. By doing so, scientists can ensure that their data is organized in a logical and coherent manner, facilitating ease of access and comprehension.

Data Organization and Labelling
-------------------------------

To ensure the accessibility and comprehensibility of data, files and entries should be assigned clear and descriptive names, accompanied by comments, tags, and other relevant metadata. PASTA-ELN enables users to add tags, thereby enhancing the searchability of data. By implementing these practices, scientists can guarantee that their data is easily understandable not only by themselves but also by their colleagues in collaborative research projects.

Here is a rewritten version of the text:

Retention of Data
-----------------

It is essential to maintain data integrity by avoiding the deletion of research data. Deleting data can lead to the manipulation of results, falsification of conclusions, and ultimately, scientific misconduct. Furthermore, data deletion compromises the reproducibility of scientific studies, rendering them unreliable and unverifiable.

PASTA-ELN offers a "Hide" function, which enables users to temporarily conceal data files and other items within a project, thereby maintaining a clear overview while preventing any loss of data. This approach adheres to the principles of a good Electronic Laboratory Notebook (ELN), ensuring the preservation of data and promoting transparent research practices.

Here is a rewritten version of the text with a more professional tone:

Raw Data as the Foundation of Truth
-----------------------------------

In many cases, raw data is compressed or stored in formats that sacrifice metadata in order to conserve disk space. For example, images may be converted from high-resolution TIF files to lower-resolution JPEG files, which omit valuable metadata that TIF files contain. While this approach may seem efficient, it can lead to issues with data analysis, as the JPEG format alters the image when zoomed in, compromising its accuracy. To mitigate these problems, PASTA-ELN extracts data, metadata, and images from raw files, discouraging the use of compressed or secondary formats.

Limitations of Graphical Output
-------------------------------

Instrument software often provides a graphical interface for displaying measurements, which can be useful for gaining a quick overview of results. However, this approach has limitations when it comes to publications, data analysis, and other applications that require accurate and reliable data. Unlike raw data files, these graphical outputs lack the provenance and metadata necessary for rigorous analysis.

Exported Data: A Second-Best Option
-----------------------------------

While instrument software may allow researchers to export data in CSV format, this approach is not ideal. Exported data may contain pre-processed or modified data, which can complicate analysis and obscure the accuracy of the original measurements. Moreover, this approach often excludes the corresponding metadata, making it difficult to track the provenance of the data. In contrast, raw binary files contain the full accuracy of the data, along with calibration and metadata settings, providing a more reliable foundation for data analysis.

Retaining Raw Data in Excel Files
---------------------------------

When it comes to data storage, Excel files (.xlsx and .xls) have both advantages and disadvantages compared to CSV files. While Excel files use high-precision data, they also group experiments into separate sheets, which can increase the context and convenience of the data. However, researchers should be aware that Excel is not a scientific tool, and data in Excel files should be treated with caution.

Additional Considerations
-------------------------

* Note-taking apps, such as Microsoft OneNote, are not suitable substitutes for Electronic Laboratory Notebooks (ELNs). ELNs are designed to facilitate structured research data, while note-taking apps are better suited for personal notes and ideas.
* Researchers should be mindful of the need to exclude personal information from public research data, ensuring compliance with European data protection legislation.
* A key principle in data management is to **share as much as possible**: procedures, metadata, and other relevant information.
