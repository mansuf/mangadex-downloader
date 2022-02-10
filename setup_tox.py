import sys
from pathlib import Path

version = 'py%s%s' % (
    sys.version_info.major,
    sys.version_info.minor
)

# Test imports
test_imports = """
from mangadex_downloader import *
from mangadex_downloader.__main__ import *
"""

file_test_imports = Path('./test-imports.py')
file_test_imports.write_text(test_imports)

# Read all requirements
requirements = []
with open('./requirements.txt', 'r') as r:
    requirements = r.read().splitlines()
deps = ""
for dep in requirements:
    deps += '   ' + dep + '\n'

# Tox configuration
tox_contents = """
[tox]
envlist = {version}

[testenv]
deps = 
{deps}
commands = python test-imports.py

""".format(version=version, deps=deps)

tox_file = Path('./tox.ini')
tox_file.write_text(tox_contents)
