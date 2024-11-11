#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_orm_adapter.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Tuple

from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_orm_config_model import DatabaseOrmConfigModel
from pasta_eln.dataverse.database_orm_main_model import DatabaseOrmMainModel
from pasta_eln.dataverse.database_orm_properties_model import DatabaseOrmPropertiesModel
from pasta_eln.dataverse.database_orm_upload_model import DatabaseOrmUploadModel
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel


class DatabaseOrmAdapter:

  @staticmethod
  def get_orm_config_model(model: ConfigModel) -> DatabaseOrmConfigModel:
    model_dict = dict(model)
    model_dict['metadata_info'] = model_dict.pop('metadata')
    return DatabaseOrmConfigModel(**model_dict)

  @staticmethod
  def get_orm_upload_model(model: UploadModel) -> DatabaseOrmUploadModel:
    model_dict = dict(model)
    return DatabaseOrmUploadModel(**model_dict)

  @staticmethod
  def get_orm_project_model(model: ProjectModel) -> DatabaseOrmMainModel:
    model_dict = dict(model)
    return DatabaseOrmMainModel(**model_dict)

  @staticmethod
  def get_config_model(model: DatabaseOrmConfigModel) -> ConfigModel:
    model_dict = dict(model)
    model_dict['metadata'] = model_dict.pop('metadata_info')
    model_dict['_id'] = model_dict.pop('id')
    return ConfigModel(**model_dict)

  @staticmethod
  def get_upload_model(model: DatabaseOrmUploadModel) -> UploadModel:
    model_dict = dict(model)
    model_dict['_id'] = model_dict.pop('id')
    return UploadModel(**model_dict)

  @staticmethod
  def get_project_model(model: Tuple[DatabaseOrmMainModel, str, str]) -> ProjectModel:
    main_model_dict = dict(model[0])
    main_model_dict['_id'] = main_model_dict.pop('id')
    main_model_dict['date_created'] = main_model_dict.pop('dateCreated')
    main_model_dict['date_modified'] = main_model_dict.pop('dateModified')
    main_model_dict.pop('type')
    return ProjectModel(**main_model_dict, status=model[1], objective=model[2])
