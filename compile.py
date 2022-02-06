import sys
from subprocess import run

output_one_folder = 'mangadex-dl'

run([
    'pyinstaller',
    'run.py',
    '-n',
    output_one_folder
])