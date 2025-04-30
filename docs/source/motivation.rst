.. _faqs:

MAIN TITLE
**********

Motivation for PASTA-ELN
========================

**What is the primary objective of the software?**
    PASTA is designed to provide researchers with the flexibility to collect and manage data from two distinct sources:

    * Local hard drives, allowing for the free exchange and analysis of research data
    * Links to stored data repositories, facilitating collaboration and access to existing research materials

    In line with industry best practices, PASTA adopts an agile project management approach, as outlined in [agile Projects](agileProjects.md).

    By providing an open-source alternative to commercial platforms such as Labfolder and SciNote, PASTA offers a unique combination of features and benefits that cater to the needs of researchers seeking a flexible and collaborative data management solution.


**What are the limitations of PASTA?**
    * PASTA is not intended to serve as a persistent database for published data. Instead, it is designed to integrate with existing solutions, such as Dataverse, which provides a robust and scalable platform for data archiving and sharing.
    * Similarly, PASTA is not a primary repository for large-scale raw data storage. Instead, it will facilitate the linking and data extraction from existing large storage solutions, including those handling giga-, tera-, and peta-bytes of data.
    * PASTA is also not intended to replace or replicate data management databases, such as Data Management Plans (DMPs), which are available through tools like RDMO on GitHub. Instead, PASTA will provide a complementary service by linking to and integrating with these databases.

**How is privacy (German Datenschutz) protected?**
    The lead designer of PASTA-ELN, along with many of their immediate colleagues, takes data protection seriously and demands privacy when using software. PASTA was designed to support privacy on multiple levels:

    * All data and metadata are collected and stored exclusively on the desktop or laptop of the researcher, with no centralized data collection. Data is only uploaded to the research group's database if the researcher explicitly chooses to share it.
    * A strict decoupling of authorization and authorship is implemented, ensuring that only authorized members of the research group can write to the database (authorization). The identity of the author of each entry can be recorded or remain anonymous (authorship).
    * Researchers have the option to choose whether they wish to be identified as the author of a particular entry in the research group's database. If they decline, their identity will be replaced with an underscore (_), making it impossible for even another user or the system administrator to identify the author.
    * Once data and metadata are shared in accordance with the FAIR principles of research, all user identification is intentionally removed, rendering all entries anonymous.
    * This approach relies on researchers avoiding the entry of personal data into any database field, which is strongly discouraged in order to maintain the highest level of data protection.


**Who is responsible for violations or rules? Who owns the data?**
    The assignment of data ownership and responsibility for adherence to rules is a critical consideration that should be addressed by both the user and their respective institutional stakeholders (e.g. supervisor). This decision should be made in a manner that is flexible and adaptable to changes in user or stakeholder affiliation.


Implementation
==============

**Why does PASTA not use a web-based interface for its database?**
    While web-based interfaces have become increasingly common, they also present several drawbacks. Specifically:

    * They often incur performance overhead, resulting in slower data access and manipulation compared to native applications.
    * Synchronizing local files with their cloud-based counterparts can be a cumbersome and error-prone process, requiring users to manually update files in multiple locations.
    * Consequently, maintaining two versions of each file (one on the user's local machine and another in the cloud) can lead to inconsistencies and version control issues.

    To mitigate these challenges, PASTA adopts a more streamlined approach, where local files are maintained on the user's hard drive and synchronized with a server for the purpose of persistence and collaboration. This design decision allows users to leverage their existing workflow with popular scientific software tools, such as ImageJ, Gwyddion, and Origin, which are optimized for local file handling.


**Comparison of Web-Based and Desktop-Based Software**
    * Web-Based Software
        * Offers the advantage of operating system independence
        * Ensures seamless compatibility across various screen sizes
        * Provides automatic software updates, ensuring users always have the latest version
    * Desktop-Based Software
        * Offers faster typing and interaction, allowing for a more fluid and intuitive user experience
        * Provides users with full control and flexibility to express their ideas and thoughts freely
        * Does not require internet access, making it ideal for offline use
        * Offers greater freedom from vendor lock-in, allowing users to choose the best software architecture for their needs
        * Enables users to work with the best version of the software, optimized for their specific requirements
    * Hybrid Approach
        * A scientist may use a desktop-based version to collect and upload data to central servers
        * Supervisors and guests can access a web-based version to view metadata
        * The database can be populated using the desktop program, or mobile device
        * This approach is similar to that of distributed version control systems, such as Git, which is widely used in software development.


**Why does the software exhibit varying performance levels among users?**
    We are aware of disparate execution times across different operating systems, as reflected in our backend testing. Specifically, we have observed the following run-time discrepancies:

	* Windows (Thinkpad E495): 57.9 seconds
	* macOS (Macbook Air 2020): 20.8 seconds
	* Linux (Thinkpad E495): 14.8 seconds

    While the graphical user interface appears to function at a similar pace across all operating systems, we are committed to investigating and addressing performance optimization opportunities for Windows users in future development cycles.

**Why do you not package PASTA-ELN as a flatpak or snap?**
    While containerization is a valuable concept for isolating software from the host operating system, it is not suitable for PASTA-ELN. Our framework requires the ability to extend and modify existing add-ons, which necessitates the use of additional libraries not included in the default package. These libraries cannot be added to a container without compromising its self-sufficiency and encapsulation. As such, a traditional installation approach allows for greater flexibility and customization is preferred.


Why does PASTA-ELN work in the way it does?
===========================================

**When a folder is moved within the project hierarchy or deleted through the file system explorer, the original folder may persist in the project view, causing errors during scanning and integrity checks.**
    To prevent data loss, it's essential to avoid removing or moving folders through the file system explorer. We maintain existing database entries to preserve the error messages. In future updates, this solution may be revised to accommodate changes in our system architecture.

    This approach fosters transparency by enabling users to clearly visualize the consequences of file removal or relocation on the project. To minimize potential disruptions, we recommend modifying or duplicating unrelated files rather than deleting the project as a whole.

.. _dodonts:

Guidelines for Data Management in Research
==========================================

Regardless of whether PASTA-ELN is used to manage ongoing research or to store existing data, it is crucial to establish a project structure during the planning stage. This involves defining and updating metadata definitions for the project, which may be inspired by agile project planning methodologies. By doing so, scientists can ensure that their data is organized in a logical and coherent manner, facilitating ease of access and comprehension.

Data Organization and Labelling
-------------------------------

To ensure the accessibility and comprehensibility of data, files and entries should be assigned clear and descriptive names, accompanied by comments, tags, and other relevant metadata. PASTA-ELN enables users to add tags, thereby enhancing the searchability of data. By implementing these practices, scientists can guarantee that their data is easily understandable not only by themselves but also by their colleagues in collaborative research projects.

Retention of Data
-----------------

It is essential to maintain data integrity by avoiding the deletion of research data. Deleting data can lead to the manipulation of results, falsification of conclusions, and ultimately, scientific misconduct. Furthermore, data deletion compromises the reproducibility of scientific studies, rendering them unreliable and unverifiable.

PASTA-ELN offers a "Hide" function, which enables users to temporarily conceal data files and other items within a project, thereby maintaining a clear overview while preventing any loss of data. This approach adheres to the principles of a good Electronic Laboratory Notebook (ELN), ensuring the preservation of data and promoting transparent research practices.

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
