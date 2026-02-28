"""Extracts the version line from pyproject.toml and inserts it into __version__.py"""

import sys
from pathlib import Path
import re

regx = r'version = "(\d*\.\d*\.\d*).+"'

with Path("pyproject.toml").resolve().open(mode="r", encoding="utf-8") as infile:
    for line in infile:
        if match := re.search(regx, line):
            print(line.upper())

            with (Path(__file__).parent.parent / "__version__.py").resolve().open(mode="w", encoding="utf-8") as outfile:
                outfile.write(line.upper())

            sys.exit()
