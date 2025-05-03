.. _definitions:

Definitions and Data Hierarchy
==============================

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Define Data Schema and Definitions</h2>
      </div>
   </div>

**Overview**: Users can define metadata structures and data types for their projects, referred to as a data schema. Additionally, users can define terms and specify URLs to relate to ontologies.

Data Schema Editor
------------------

The editor, located under "Project Group," allows users to adapt existing data types in the PASTA database. Users can:

1. Select, edit, or create new data types.
2. Specify metadata in a table, including:
   - **Description**
   - **Unit**
   - **Mandatory status**
   - **List** Metadata can link to fixed lists (e.g., devices: "Oven," "Fume hood") or other data types (e.g., procedures).

**Note**: All metadata must be unique and include a name, tags, and comments in the general tab.

Definition Overview
-------------------

Scientific properties often require detailed definitions. For example:

.. code-block::

    temperature_A : 97

Here, **temperature_A** is the **key**, and 97 is the **value**. However, this lacks essential details like:

- **Scientific unit**: Units may vary.
- **Description**: Text in the user's language or an official explanation.
- **IRI/URL**: Reference to an authoritative online resource.

A more complete representation:

.. code-block::

    temperature_A : {
        'value': 97,
        'unit': 'C',
        'description': 'Temperature inside the instrument’s right side',
        'IRI': 'https://www.wikidata.org/wiki/Q11466'}

Additional metadata can include:

- **Uncertainty**: Margin of error.
- **Data type**: Integer, text, date, etc.
- **Allowable values**: E.g., temperatures cannot be below 0 K.

PASTA-ELN balances usability and flexibility, allowing most metadata to be included in the **value** or **description** fields.

Handling Multiple Datasets and Data Types
-----------------------------------------

To avoid duplicating information, PASTA-ELN stores **description** and **IRI** for each **key** in a centralized table (*definitions*). The **value** and **unit** can be stored independently or inherit from the master definition. If both individual and master definitions specify a unit, the individual value's unit takes precedence.

This ensures each **key** is unique. For example:

- "Height" defined for instruments applies to samples, sharing the same **description** and **IRI** but potentially differing in units.
- Unique **keys** are required for distinct descriptions.
