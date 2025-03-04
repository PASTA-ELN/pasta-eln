"""
Common workflow description
MIT - License

Part of the NFDI-Matwerk and the Task area Workflow and software development

Authors: Steffen Brinckmann, Liam Huber, Sarath Menon
"""
import hashlib, json, logging, re, functools
from inspect import signature
from typing import Union, Any, Optional
from pathlib import Path
from urllib.parse import ParseResult, urlunparse, urlparse
from urllib.request import urlopen
from urllib.error import HTTPError
import tkinter as tk
from tkinter import font as tkFont
from tkinter import filedialog
try:
    from pyiron_workflow import Workflow
    print('Started pyiron workflow engine')
except ImportError:
    class RShiftableOutput:
        """ Output of the wrapper / decorator function """
        def __init__(self, value):
            self.value = value

        def __rshift__(self, other):
            return other


    class WorkflowOutputs(dict):
        """ Output of the entire workflow """
        def to_value_dict(self):
            """ return workflow output as dictionary """
            return self


    class Wrap():
        """ Wrapper class that defines the decorator """
        def as_function_node(self, _):
            """ decorator function """
            def decorator_inner(func):
                """ inner decorator, that is returned """
                @functools.wraps(func)
                def wrapper(self, *args, **kwargs):
                    wrapped_params = signature(func).parameters
                    kwargs = {k: v for k, v in kwargs.items() if k in wrapped_params}
                    # wrapper that can access the local variables of the wrapped function
                    out = func(self, *args, **kwargs)
                    return RShiftableOutput(out)
                return wrapper
            return decorator_inner


    class Workflow():
        """ Boilerplate = minimalistic workflow engine"""
        wrap = Wrap()

        def __init__(self, *args, **kwargs) -> None:
            self.outputs = WorkflowOutputs()

        def draw(self):
            """ Dummy method to mimic pyiron-workflow"""
            obj = Picture()
            return obj

        def __setattr__(self, key, value):
            if isinstance(value, RShiftableOutput):
                self.outputs[key] = value.value
            super().__setattr__(key, value)


    class Picture():
        """ Dummy picture class that does nothing """
        def render(self, *args, **kwargs):
            """ render the workflow as a picture """
        print('Started minimalistic workflow engine')
#### END of minimalistic workflow ####


class Storage():
    """Storage for procedures"""

    def __init__(self, procedures) -> None:
        """Storage of procedures

        Args:
          procedures (): location or list of procedures to choose from
        """
        self.procedures: dict[str, Union[str, Path]] = {}
        if isinstance(procedures, dict):
            self.add_procedures(procedures)
        elif isinstance(procedures, Path):
            self.add_procedure_directory(procedures)
        elif isinstance(procedures, ParseResult):
            self.add_remote_procedure_directory(procedures)
        else:
            raise ValueError('Procedures ill defined')
        logging.basicConfig(
            filename="workflow.log",
            level=logging.INFO,
            datefmt="%m-%d %H:%M:%S",
            format="%(asctime)s|%(levelname)s:%(message)s",
        )
        logging.info("Start workflow")


    def add_procedures(self, procedures: dict[str, Union[str, Path]]) -> None:
        """Add procedures to local copy

        Args:
          procedures (dict): dictionary of procedures (text), or files-of-procedures
        """
        for key, value in procedures.items():
            if isinstance(value, str):
                if Path(value).exists():
                    self.procedures[key] = Path(value)
                    continue
            self.procedures[key] = value


    def add_procedure_directory(self, path: Path) -> None:
        """Add directory with procedures to local copy
        - index.json file in that directory defines names

        Args:
          path (Path): directory with procedure files
        """
        with open(path / "index.json", encoding="utf-8") as file_input:
            procedures = json.load(file_input)
        for key, value in procedures.items():
            if (path / value).exists():
                self.procedures[key] = path / value
                continue
            self.procedures[key] = value


    def add_remote_procedure_directory(self, path: ParseResult) -> None:
        """Add remote directory with procedures

        Args:
          path (Path): directory with procedure files
        """
        path = urlunparse(path)
        path += '' if path.endswith('/') else '/'
        index_path = path + 'index.json'
        procedures = json.loads(urlopen(index_path).read())
        for key, rel_path in procedures.items():
            self.procedures[key] = urlparse(path + rel_path)
        # print(json.dumps(self.procedures))


    def list_parameters(self, name: str) -> dict[str, str]:
        """list all the parameters in this procedure

        Args:
          name (str): name of procedure

        Returns:
          dict: key,default pairs of parameters
        """
        text = self.get_text(name)
        params = re.findall(r"\|\w+\|.*\|", text)
        return {i.split("|")[1]: i.split("|")[2] for i in params}


    def get_text(self, name: str) -> str:
        """get text of this procedure

        Args:
          name (str): name of procedure

        Returns:
          str: its text
        """
        if name not in self.procedures:
            raise ValueError("Name of step not in procedures:", name)
        procedure = self.procedures[name]
        if isinstance(procedure, str):
            text = procedure
        elif isinstance(procedure, Path):
            with open(procedure, encoding="utf-8") as file_input:
                text = file_input.read()
        elif isinstance(procedure, ParseResult):
            try:
                text = urlopen(urlunparse(procedure)).read().decode()
            except HTTPError:
                print(f'IRI not found: {urlunparse(procedure)}')
        else:
            raise ValueError(f'Procedure content invalid: {procedure}')
        return text


class Sample:
    """ Sample with a name """
    def __init__(self, name: str) -> None:
        """Sample with a name: most basic sample

        Args:
          name (str): human readable name of sample
        """
        self.name = name

    def __repr__(self) -> str:
        return f'Name: {self.name}'

    def print(self) -> None:
        """ Print sample name to screen """
        print(f'Name: {self.name}')


class RichText(tk.Text):
    """ Class to display the markdown text in the window
    based on https://stackoverflow.com/questions/63099026/fomatted-text-in-tkinter
    """
    def __init__(self, *args, **kwargs):
        """Init rich text field in TK"""
        super().__init__(*args, **kwargs)
        self.text_width = kwargs.get('width',40)
        # fonts
        default = tkFont.nametofont(self.cget("font"))
        default_size = default.cget("size")
        bold = tkFont.Font(**default.configure())
        bold.configure(weight="bold")
        self.tag_configure("bold", font=bold)
        italic = tkFont.Font(**default.configure())
        italic.configure(slant="italic")
        self.tag_configure("italic", font=italic)
        h1 = tkFont.Font(**default.configure())
        h1.configure(size=int(default_size * 1.2), weight="bold")
        self.tag_configure("h1", font=h1, spacing3=default_size)
        # bullet lists
        em = default.measure("m")
        lmargin2 = em + default.measure("\u2022 ")
        self.tag_configure("bullet", lmargin1=em, lmargin2=lmargin2)


    def insert_item(self, text: str, index: str = "end") -> None:
        """insert an item to the bullet point list

        Args:
          text (str): text to add
          index (str): location where to add
        """
        self.insert(index, f"\u2022 {text}\n", "bullet")


    def insert_text(self, text: str, style: str = "", index: str = "end") -> None:
        """insert rich text into window

        Args:
          text (str): text to add
          style (str): its style or format
          index (str): location where to add
        """
        self.insert(index, text, style)


    def parse_markdown(self, text: str) -> None:
        """Poor mans markdown parser by SB
        Markdown features understood:
        - headline #
        - items -
        - bold **text**
        - italics *text*
        - comments <--- text --->

        Args:
          text (str): markdown text
        """
        for line in text.split("\n"):
            if line.startswith("<!---") and line.endswith("-->"):  # comment
                continue
            style = ""
            if line.startswith("# "):
                style = "h1"
                line = line[2:int(self.text_width/1.3)]
            elif line.startswith("**") and line.endswith("**"):
                style = "bold"
                line = line[2:-2]
            elif line.startswith("*") and line.endswith("*"):
                style = "italic"
                line = line[1:-1]
            if line.startswith("- "):
                self.insert_item(f"{line[2:self.text_width-1]}")
            else:
                self.insert_text(f"{line[:self.text_width]}\n", style)


def main_window(text, parameter_all, param):
    """ Main window

    Args:
      text (str): text in the text area
      parameter_all (dict): all parameters
      param (dict): specific parameter

    Returns:
      tuple of file name, parameter
    """
    window = tk.Tk()
    window.geometry("500x750")  # set starting size of window
    window.title('Common workflow description')
    window.maxsize(1000, 1200)  # width x height
    widget = RichText(window, width=60, height=30)
    widget.parse_markdown(text)
    widget.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
    # question fields below
    padding = {"ipadx": 10, "ipady": 10, "padx": 5, "pady": 5, "sticky": "ew"}
    text_fields = []
    parameter_all |= param
    file_name = ''
    metadata = {}

    def done():
        nonlocal metadata
        metadata = dict(parameter_all)
        for idx, key in enumerate(parameter_all):
            if key == 'filename':
                metadata.pop('filename')
                continue
            metadata[key] = text_fields[idx].get()
        logging.info("Save step file-name:%s  metadata:\n%s", file_name,
                     json.dumps(metadata, indent=2))
        window.destroy()
        return file_name, metadata

    def select_file():
        reply = filedialog.askopenfilename()
        if reply is not None:
            nonlocal file_name
            file_name = reply

    for idx, (key, value) in enumerate(parameter_all.items()):
        name = tk.Label(window, text=key)
        name.grid(**padding, row=1 + idx, column=0)  # type: ignore[arg-type]
        if key == 'filename':
            file_button = tk.Button(window, text="select file", command=select_file)
            file_button.grid(**padding, row=1 + idx, column=1)
        else:
            text_fields.append(tk.Entry(window))
            text_fields[-1].insert(10, str(value))
            text_fields[-1].grid(**padding, row=1 + idx, column=1)  # type: ignore[arg-type]
    button = tk.Button(window, text="done", command=done)
    button.grid(**padding, row=4, column=1)  # type: ignore[arg-type]
    window.mainloop()
    return file_name, metadata


@Workflow.wrap.as_function_node("y")
def step(storage:Storage, sample: Sample, name: str, param: Optional[dict[str, Any]] = None):
    """Render in TkInter

    Args:
      sample (Sample): sample to do step on
      name (str): name of procedure
      param (dict): parameter to change from default procedure

    Returns:
      Sample: changed sample / child sample
      str: file name of result
      dict: metadata collected during step
    """
    if param is None:
        param = {}
    text = storage.get_text(name)
    m = hashlib.sha256()
    m.update(text.encode("utf-8"))
    shasum256 = m.hexdigest()
    if param is not None:
        for value in param.values():
            text = re.sub(r"\|{key}\|.+\|", value, text)
    text = re.sub(r"\|\w+\|(.+)\|", r"\1", text)
    text = f"# Execute the following action with sample: {sample.name}\n{text}"
    logging.info("Start step sample:{%s}  procedure-name:{%s}  sha256:{%s}  parameters:\n{%s}",
                 sample.name, name, shasum256, json.dumps(param, indent=2))
    parameter_all = storage.list_parameters(name)
    file_name, metadata = main_window(text, parameter_all, param)
    logging.info("End step ")
    return [sample, file_name, metadata]


