#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: sql_queries.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: sql_queries.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: sql_queries.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

class SqlQueries:
  insert_statements = {
    "": "INSERT INTO users (username, password, created_on, created_by) VALUES (%s, %s, %s, %s)",
    "insert_project": "INSERT INTO projects (name, description, created_on, created_by) VALUES (%s, %s, %s, %s)",
    "insert_dataset": "INSERT INTO datasets (name, description, created_on, created_by) VALUES (%s, %s, %s, %s)",
    "insert_document": "INSERT INTO documents (name, description, created_on, created_by) VALUES (%s, %s, %s, %s)",
    "insert_upload": "INSERT INTO uploads (name, description, created_on, created_by) VALUES (%s, %s, %s, %s)",
    "insert_upload_status": "INSERT INTO upload_status (name, description, created_on, created_by) VALUES (%s, %s, %s, %s)",
    "insert_dataset_upload": "INSERT INTO dataset_uploads (dataset_id, upload_id, created_on, created_by) VALUES (%s, %s, %s, %s)",
  }
