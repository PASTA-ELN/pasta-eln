.. _annexmeta:

Setting git-annex metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^

`git-annex` has its own concept and implementation of file metadata, and DataLad Gooey provides a graphical user interface for querying, removing, and setting metadata.
This functionality is exposed via the ``Metadata`` tab or right-click context menue on any annexed file.

.. image:: _static/pyside.png
   :width: 75%
   :alt: Annex Metadata editor on a file with preexisting metadata


Each annexed file's content [#f1]_ can have any number of metadata *fields* attached to it to describe it, and each field can have any number of *values*.
This metadata is stored internally, in the :term:`git-annex branch`.

.. _glossary:

Central Concepts (Glossary)
---------------------------

Working with DataLad is easier if you know a few technical terms that are regularly referred to in the documentation and the GUI interface.
This glossary provides short definitions, and links relevant additional documentation, where available.


.. glossary::

   git-annex
      :term:`git-annex` concept: a different word for the internal location in a dataset that 's are version controlled in.

   git-annex branch
      Files managed by :term:`git-annex` are annotated as "annexed-file". Annexed files have access to additional commands in their context menus such as.

   branch
      Git concept: A lightweight, independent history streak of your dataset. Branches can contain less, more, or changed files compared to other branches, and one can merge the changes a branch contains into another branch. DataLad Gooey only views the currently checked out branch in your dataset, and does not support Git commands that expose branching functionality.

.. code::

   # Create and enter a new virtual environment (optional)
   python3 -m venv ~/.venvs/datalad-gooey
   source ~/.venvs/datalad-gooey/bin/activate

.. code::

   # Install from PyPI
   pip install datalad_gooey

.. admonition:: Dependencies

   Because this is an extension to ``datalad``, the installation process also installs
   the Python package, although all recursive dependencies (such as ``git-annex``)
   are not automatically installed. For complete instructions on how to install ``datalad``
   and ``git-annex``, please refer to the .


.. [#f1] Note that metadata is attached to file content, not file names, i.e. the git-annex key corresponding to the content of a file, not to a particular filename on a particular git branch. This means that all files with the same key share the same metadata, which is stored in the :term:`git-annex branch`. If a file is modified, the metadata of the previous version will be copied to the new key when git-annex adds the modified file.