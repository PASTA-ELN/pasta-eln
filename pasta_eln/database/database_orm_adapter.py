""" Adapter for converting between ORM models and domain models. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_orm_adapter.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_orm_adapter.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Tuple

from pasta_eln.database.models.config_model import ConfigModel
from pasta_eln.database.models.config_orm_model import ConfigOrmModel
from pasta_eln.database.models.data_hierarchy_definition_model import DataHierarchyDefinitionModel
from pasta_eln.database.models.data_hierarchy_definition_orm_model import DataHierarchyDefinitionOrmModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.database.models.data_hierarchy_orm_model import DataHierarchyOrmModel
from pasta_eln.database.models.main_orm_model import MainOrmModel
from pasta_eln.database.models.project_model import ProjectModel
from pasta_eln.database.models.upload_model import UploadModel
from pasta_eln.database.models.upload_orm_model import UploadOrmModel


class DatabaseOrmAdapter:
  """Adapter for converting between ORM models and domain models.

  This class provides static methods to convert various domain models to their
  corresponding ORM representations and vice versa. It facilitates the interaction
  between the application layer and the database layer by handling the necessary
  transformations.
  """

  @staticmethod
  def get_orm_config_model(model: ConfigModel) -> ConfigOrmModel:
    """Converts a ConfigModel to a DatabaseOrmConfigModel.

    This method takes a ConfigModel instance and transforms it into a
    DatabaseOrmConfigModel instance, adjusting the necessary fields.

    Args:
        model (ConfigModel): The configuration model to convert.

    Returns:
        ConfigOrmModel: The converted ORM configuration model.
    """
    model_dict = dict(model)
    model_dict['metadata_info'] = model_dict.pop('metadata')
    return ConfigOrmModel(**model_dict)

  @staticmethod
  def get_orm_upload_model(model: UploadModel) -> UploadOrmModel:
    """Converts an UploadModel to a DatabaseOrmUploadModel.

    This method takes an UploadModel instance and transforms it into a
    DatabaseOrmUploadModel instance.

    Args:
        model (UploadModel): The upload model to convert.

    Returns:
        UploadOrmModel: The converted ORM upload model.
    """
    model_dict = dict(model)
    return UploadOrmModel(**model_dict)

  @staticmethod
  def get_orm_project_model(model: ProjectModel) -> MainOrmModel:
    """Converts a ProjectModel to a DatabaseOrmMainModel.

    This method takes a ProjectModel instance and transforms it into a
    DatabaseOrmMainModel instance, adjusting the necessary fields.

    Args:
        model (ProjectModel): The project model to convert.

    Returns:
        MainOrmModel: The converted ORM project model.
    """
    model_dict = dict(model)
    model_dict['dateCreated'] = model_dict.pop('date_created')
    model_dict['dateModified'] = model_dict.pop('date_modified')
    model_dict.pop('status')
    model_dict.pop('objective')
    return MainOrmModel(**model_dict)

  @staticmethod
  def get_orm_data_hierarchy_model(model: DataHierarchyModel) -> DataHierarchyOrmModel:
    """Converts a DataHierarchyModel to a DatabaseOrmDataHierarchyModel.

    This method takes a DataHierarchyModel instance and transforms it into a
    DatabaseOrmDataHierarchyModel instance.

    Args:
        model (DataHierarchyModel): The data hierarchy model to convert.

    Returns:
        DataHierarchyOrmModel: The converted ORM data hierarchy model.
    """
    model_dict = dict(model)
    model_dict.pop('id')
    definitions = model_dict.pop('definitions')
    model_dict['definitions'] = [DatabaseOrmAdapter.get_data_hierarchy_definition_orm_model(definition) for definition
                                 in definitions]
    return DataHierarchyOrmModel(**model_dict)

  @staticmethod
  def get_config_model(model: ConfigOrmModel) -> ConfigModel:
    """Converts a DatabaseOrmConfigModel to a ConfigModel.

    This method takes a DatabaseOrmConfigModel instance and transforms it into a
    ConfigModel instance, adjusting the necessary fields.

    Args:
        model (ConfigOrmModel): The ORM configuration model to convert.

    Returns:
        ConfigModel: The converted configuration model.
    """
    model_dict = dict(model)
    model_dict['metadata'] = model_dict.pop('metadata_info')
    model_dict['_id'] = model_dict.pop('id')
    return ConfigModel(**model_dict)

  @staticmethod
  def get_upload_model(model: UploadOrmModel) -> UploadModel:
    """Converts a DatabaseOrmUploadModel to an UploadModel.

    This method takes a DatabaseOrmUploadModel instance and transforms it into an
    UploadModel instance.

    Args:
        model (UploadOrmModel): The ORM upload model to convert.

    Returns:
        UploadModel: The converted upload model.
    """
    model_dict = dict(model)
    model_dict['_id'] = model_dict.pop('id')
    return UploadModel(**model_dict)

  @staticmethod
  def get_project_model(model: Tuple[MainOrmModel, str, str]) -> ProjectModel:
    """Converts a tuple of DatabaseOrmMainModel and additional fields (status, objective) to a ProjectModel.

    This method takes a tuple containing a DatabaseOrmMainModel instance and
    additional fields, transforming it into a ProjectModel instance.

    Args:
        model (Tuple[MainOrmModel, str, str]): The tuple containing the ORM
        main model and additional fields.

    Returns:
        ProjectModel: The converted project model.
    """
    main_model_dict = dict(model[0])
    main_model_dict['_id'] = main_model_dict.pop('id')
    main_model_dict['date_created'] = main_model_dict.pop('dateCreated')
    main_model_dict['date_modified'] = main_model_dict.pop('dateModified')
    main_model_dict.pop('type')
    return ProjectModel(**main_model_dict, status=model[1], objective=model[2])

  @staticmethod
  def get_data_hierarchy_model(model: DataHierarchyOrmModel) -> DataHierarchyModel:
    """Converts a DatabaseOrmDataHierarchyModel to a DataHierarchyModel.

    This method takes a DatabaseOrmDataHierarchyModel instance and transforms it
    into a DataHierarchyModel instance.

    Args:
        model (DataHierarchyOrmModel): The ORM data hierarchy model to convert.

    Returns:
        DataHierarchyModel: The converted data hierarchy model.
    """
    model_dict = dict(model)
    definitions = model_dict.pop('definitions')
    model_dict['definitions'] = [DatabaseOrmAdapter.get_data_hierarchy_definition_model(definition) for definition in
                                 definitions]
    return DataHierarchyModel(**model_dict)

  @staticmethod
  def get_data_hierarchy_definition_model(model: DataHierarchyDefinitionOrmModel) -> DataHierarchyDefinitionModel:
    """Converts a DatabaseOrmDataHierarchyDefinitionsModel to a DataHierarchyDefinitionsModel.

    This method takes a DatabaseOrmDataHierarchyDefinitionsModel instance and transforms it
    into a DataHierarchyDefinitionsModel instance.

    Args:
        model (DatabaseOrmDataHierarchyDefinitionsModel): The ORM data hierarchy definitions model to convert.

    Returns:
        DataHierarchyDefinitionModel: The converted data hierarchy definitions model.
    """
    model_dict = dict(model)
    meta_list: str = model_dict.pop('meta_list')
    model_dict['meta_list'] = meta_list.split(',') if meta_list else []
    return DataHierarchyDefinitionModel(**model_dict)

  @staticmethod
  def get_data_hierarchy_definition_orm_model(model: DataHierarchyDefinitionModel) -> DataHierarchyDefinitionOrmModel:
    model_dict = dict(model)
    model_dict.pop('id')
    meta_list = model_dict.pop('meta_list')
    model_dict['meta_list'] = ",".join(meta_list) if meta_list and isinstance(meta_list, list) else ''
    return DataHierarchyDefinitionOrmModel(**model_dict)
