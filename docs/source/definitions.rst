.. _definitions:

Definitions in PASTA-ELN
************************

Definition overview
-------------------

In scientific contexts, properties are often defined with specific details. For instance, a temperature measurement might be represented as:

.. code-block::

    temperature_A : 97

Here, **temperature_A** is referred to as the **key**, while 97 represents the **value**, which in this example is a numerical figure. However, this representation lacks essential information, such as:

- **Scientific unit**: Units may vary across measurements.
- **Description**: Could include text in the user's language, an official explanation, or other clarifying details.
- **IRI/URL**: A reference to an authoritative online resource, such as an ontology node or standardized definition.

To address these gaps, the entry could be restructured as follows:

.. code-block::

    temperature_A : {
        'value': 97,
        'unit': 'C',
        'description': 'Temperature inside the instrument’s right side',
        'IRI': 'https://www.wikidata.org/wiki/Q11466'}

Additional metadata can further enrich each property, such as:

- **Uncertainty**: To account for the margin of error in values.
- **Data type**: For example, integer, text, date, etc.
- **Allowable values**: For instance, temperatures cannot be less than 0 K.

While including this information enhances the metadata's richness, it also increases complexity for both users and developers. PASTA-ELN seeks to strike a balance between usability—minimizing bugs by keeping things straightforward—and offering users the flexibility to include necessary details. Most additional metadata can be incorporated within the **value** or **description** fields.

Handling Multiple Datasets and Data Types
-----------------------------------------

When a specific definition is used across multiple database locations, duplicating the associated information is inefficient. To optimize this, PASTA-ELN stores the **description** and **IRI** for each **key** in a centralized table (referred to as *definitions*). However, the **value** and **unit** can either be stored independently or inherit from the master definition. In cases where both individual and master definitions specify a unit, precedence is logically given to the individual value's unit.

This approach ensures that each **key** is unique and appears only once. For example:

- If "height" is defined for instruments, the same "height" key applies to samples, sharing the same **description** and **IRI** but potentially differing in units.
- If distinct descriptions are required, unique **keys** must be assigned to differentiate them.
