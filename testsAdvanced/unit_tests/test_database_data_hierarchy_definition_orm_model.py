#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_database_data_hierarchy_definition_orm_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pasta_eln.database.models.data_hierarchy_definition_orm_model import DataHierarchyDefinitionOrmModel


# Setup an in-memory SQLite database for testing
@pytest.fixture(scope='module')
def db_session():
  engine = create_engine('sqlite:///:memory:')
  DataHierarchyDefinitionOrmModel.metadata.create_all(engine)
  Session = sessionmaker(bind=engine)
  session = Session()
  yield session
  session.close()


class TestDatabaseDataHierarchyDefinitionOrmModel:

  @pytest.mark.parametrize(
    'doc_type, doc_class, index, name, query, unit, IRI, mandatory, meta_list, expected_columns',
    [
      ('type1', 'class1', 'index1', 'name1', 'query1', 'unit1', 'IRI1', 'mandatory1', 'meta_list1',
       ['doc_type', 'doc_class', 'index', 'name', 'query', 'unit', 'IRI', 'mandatory', 'meta_list']),
      ('type2', None, None, None, None, None, None, None, None,
       ['doc_type', 'doc_class', 'index', 'name', 'query', 'unit', 'IRI', 'mandatory', 'meta_list']),
    ],
    ids=['all_fields_provided', 'only_primary_keys_provided']
  )
  def test_data_hierarchy_definition_orm_model(self, db_session, doc_type, doc_class, index, name, query, unit, IRI,
                                               mandatory, meta_list, expected_columns):
    # Act
    instance = DataHierarchyDefinitionOrmModel(
      doc_type=doc_type,
      doc_class=doc_class,
      index=index,
      name=name,
      query=query,
      unit=unit,
      IRI=IRI,
      mandatory=mandatory,
      meta_list=meta_list
    )
    db_session.add(instance)
    db_session.commit()

    # Assert
    assert instance.doc_type == doc_type
    assert instance.doc_class == doc_class
    assert instance.index == index
    assert instance.name == name
    assert instance.query == query
    assert instance.unit == unit
    assert instance.IRI == IRI
    assert instance.mandatory == mandatory
    assert instance.meta_list == meta_list
    assert DataHierarchyDefinitionOrmModel.get_table_columns() == expected_columns

  @pytest.mark.parametrize(
    'doc_type, doc_class, index',
    [
      (None, 'class1', 'index1'),
      ('type1', None, 'index1'),
      ('type1', 'class1', None),
    ],
    ids=['missing_doc_type', 'missing_doc_class', 'missing_index']
  )
  def test_data_hierarchy_definition_orm_model_primary_key_constraints(self, db_session, doc_type, doc_class, index):
    # Act & Assert
    with pytest.raises(Exception):
      instance = DataHierarchyDefinitionOrmModel(
        doc_type=doc_type,
        doc_class=doc_class,
        index=index
      )
      db_session.add(instance)
      db_session.commit()
