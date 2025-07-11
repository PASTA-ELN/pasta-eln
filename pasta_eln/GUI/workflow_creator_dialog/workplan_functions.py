from pathlib import Path
from typing import Tuple

from .workplan_template import WORKPLAN_TEMPLATE
from ...guiCommunicate import Communicate


def generate_workplan(comm: Communicate, workplan_name: str, library_url: str, sample_name: str, procedures: list[str],
                      parameters: list[dict[str, str]], docType: str) -> None:
    """
    Write the given parameters of a workplan in a file with the format of the common workplan description.
    """
    # Read Template
    template = WORKPLAN_TEMPLATE

    # Generate Common Workflow Description
    step_string1 = "".join(
        [f"wf.step{i} = step(storage, sample, '{step}', {parameters[i]}, run_after_init = True)\n" for i, step in
         enumerate(procedures)])
    step_string2 = ''
    for i in range(len(procedures)):
        if i < len(procedures) - 1:
            step_string2 += f'wf.step{i} >> '
        else:
            step_string2 += f'wf.step{i}'
    cwd_string = ''.join(template[0:14]).format(**locals()) + step_string1 + "\n" + step_string2 + "\n" + "".join(template[14:])
    comm.backend.addData(docType, {'name':workplan_name, 'content':cwd_string}, [comm.projectID])


def get_db_procedures(comm: Communicate) -> dict[str, str | Path]:
    return comm.storage.procedures


def get_procedure_default_paramaters(procedure: str, comm: Communicate) -> dict[str, str]:
    parameters = {}
    try:
        parameters = comm.storage.list_parameters(procedure)
    finally:
        return parameters


def get_procedure_text(procedure: str, comm: Communicate) -> str:
    try:
        text = comm.storage.get_text(procedure)
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

def get_db_samples(comm: Communicate):
    samples = {}
    df = comm.backend.db.getView('viewDocType/sample')
    for row in df.itertuples(index=False):
        name = row.name
        id = row.id
        doc = comm.backend.db.getDoc(id)
        docPath = doc['branch'][0]['path']
        if docPath:
            path = comm.backend.basePath/docPath
        else:
            path = Path()
        if path.is_file():
            samples[name] = path
        else:
            try:
                samples[name] = doc['content']
            except KeyError:
                samples[name] = ""
    return samples