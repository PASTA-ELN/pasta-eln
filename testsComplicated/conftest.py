"""Make add-on siblings importable by plain name, as in a PASTA add-on folder"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def pytest_configure():
    """Read the user's configuration, but write only to a copy in a temporary home"""
    tempHome = Path(tempfile.mkdtemp(prefix='pastaTestHome'))
    for name in ('.pastaELN.json', '.pastaELN_testing.json'):
        if (Path.home()/name).exists():
            shutil.copy2(Path.home()/name, tempHome/name)
    os.environ['HOME'] = os.environ['USERPROFILE'] = str(tempHome)         # Path.home(): Linux/macOS, Windows
