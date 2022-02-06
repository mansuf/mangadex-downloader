import sys
from subprocess import run

output_one_file = 'mangadex-dl-%s' % sys.platform

run([
    'pyinstaller',
    'run.py',
    '-F',
    '-n',
    output_one_file
])

output_one_folder = 'mangadex-dl'

run([
    'pyinstaller',
    'run.py',
    '-n',
    output_one_folder
])