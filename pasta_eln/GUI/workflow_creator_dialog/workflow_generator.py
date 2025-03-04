from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

from .common_workflow_description import Storage


def generate_workflow(output_file: str, workflow_name: str, library_url: str, sample_name: str, procedures: list[str],
                      parameters: list[dict[str, str]]) -> None:
    """
    Write the given parameters of a workflow in a file with the format of the common workflow description.
    """
    # Read Template
    with open("workflow_template.txt", 'r') as reader:
        template = reader.readlines()
    # Generate Common Workflow Description
    with open(output_file, 'w') as writer:
        # Header always the same
        for line in template[0:8]:
            writer.write(line)
        writer.write("")

        # Stuff inbetween
        writer.write(f"wf = Workflow('{workflow_name}', automate_execution=False)\n")
        writer.write(f"proceduresLibrary = urlparse('{library_url}')\n")
        writer.write(f"storage=Storage(proceduresLibrary)\n")
        writer.write("\n")
        writer.write(f"sample = Sample('{sample_name}')\n")
        writer.write("\n")
        for i, step in enumerate(procedures):
            writer.write(f"wf.step{i} = step(storage, sample, '{step}', {parameters[i]}, run_after_init = True)\n")
        writer.write("\n")
        string = ''
        for i in range(len(procedures)):
            if i < len(procedures) - 1:
                string += f'wf.step{i} >> '
            else:
                string += f'wf.step{i}'
        writer.write(string + "\n")
        writer.write("wf.starting_nodes = [wf.step0] \n")

        # Footer always the same
        writer.write("")
        for line in template[9:]:
            writer.write(line)


def get_db_procedures() -> dict[str, str | Path]:
    proceduresLibrary = urlparse(
        'https://raw.githubusercontent.com/SteffenBrinckmann/common-workflow-description_Procedures/main')
    storage = Storage(proceduresLibrary)

    return storage.procedures


def get_procedure_default_paramaters(procedure: str) -> dict[str, str]:
    proceduresLibrary = urlparse(
        'https://raw.githubusercontent.com/SteffenBrinckmann/common-workflow-description_Procedures/main')
    storage = Storage(proceduresLibrary)
    parameters = {}
    try:
        parameters = storage.list_parameters(procedure)
    finally:
        return parameters


def get_procedure_text(procedure: str) -> str:
    proceduresLibrary = urlparse(
        'https://raw.githubusercontent.com/SteffenBrinckmann/common-workflow-description_Procedures/main')
    storage = Storage(proceduresLibrary)

    try:
        text = storage.get_text(procedure)
    except UnboundLocalError:
        text = procedure
    return text


def get_steps_from_file(filename: str) -> Tuple[list[str], list[dict[str, str]]]:
    names = []
    parameters = []
    with open(filename, 'r') as reader:
        lines = reader.readlines()
        for line in lines[14:]:
            if line.startswith('wf.step'):
                line = line.split(', ', 3)
                names.append(eval(line[2]))
                parameters.append(eval(line[3].rsplit(", ", 1)[0]))
            else:
                break
    return names, parameters


def get_sample_name_from_file(filename: str) -> str:
    with open(filename, 'r') as reader:
        lines = reader.readlines()
        line = lines[12]
        line = line.split('\'')[1]
        return line
