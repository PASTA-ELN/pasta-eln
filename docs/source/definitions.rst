.. _definitions:

Definitions in PASTA-ELN
************************

General concept
---------------

In science, properties have a definition. For example, a temperature measurement is might be represented as:

.. code-block::

    temperature_A : 97

where "temperature_A" is called the **key** and 97 the **value** which is a number in this case. This information is missing
crutial information:

- scientific unit; might / might-not differ from measurement to measurement
- description; might be a text in the user's language, an official description, etc.
- IRI / URL: link to a resource on the internet that represents an offcial definition, ontology node, ...

As such, the previous entry should be rewritten as, where () are used to symbolize a tuple:

.. code-block::

    temperature_A : (97, C, "temperature inside the instruments right side",  https://www.wikidata.org/wiki/Q11466)


Multiple datasets / data-types
------------------------------

If the same definition is used in multiple locations of the database, it would be not sensible to store repeated
information multiple times. Hence, PASTA-ELN stores the description and IRI for each *key* only once (in a table called definitions).
However, the *value* and the unit can be stored each time separately or the master definition is used.

A result of this concept is that each *key* is unique and only should occur once. If a "height" exists in instruments, "height" in sample has the same
description and IRI. If the user wants to have different descriptions, then a different *key* should be used.


