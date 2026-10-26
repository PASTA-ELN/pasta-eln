"""Make add-on siblings importable by plain name, as in a PASTA add-on folder"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
