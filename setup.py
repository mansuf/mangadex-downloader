import pathlib
import re
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

init_file = (HERE / "mangadex_downloader/__init__.py").read_text()

re_version = r'__version__ = \"([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})\"'
_version = re.search(re_version, init_file)

if _version is None:
  raise RuntimeError("Version is not set")

version = _version.group(1)

# Read description
re_description = r'__description__ = \"(.{1,})\"'
_description = re.search(re_description, init_file)

if _description is None:
  raise RuntimeError("Description is not set")

description = _description.group(1)

requirements = []
with open('./requirements.txt', 'r') as r:
  requirements = r.read().splitlines()

requirements_docs = []
with open('./requirements-docs.txt', 'r') as r:
  requirements_docs = r.read().splitlines()

requirements_optional = []
with open('./requirements-optional.txt', 'r') as r:
  requirements_optional = r.read().splitlines()

extras_require = {
  'docs': requirements_docs,
  'optional': requirements_optional
}

packages = find_packages('.')

setup(
  name = 'mangadex-downloader',         
  packages = packages,   
  version = version,
  license='MIT',     
  description = description,
  long_description= README,
  long_description_content_type= 'text/markdown',
  author = 'Rahman Yusuf',              
  author_email = 'danipart4@gmail.com',
  url = 'https://github.com/mansuf/mangadex-downloader',  
  download_url = 'https://github.com/mansuf/mangadex-downloader/releases',
  keywords = ['mangadex'], 
  install_requires=requirements,
  extras_require=extras_require,
  entry_points = {
    'console_scripts': [
      'mangadex-downloader=mangadex_downloader.__main__:main',
      'mangadex-dl=mangadex_downloader.__main__:main'
    ]
  },
  classifiers=[
    'Development Status :: 5 - Production/Stable',  
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10'
  ],
  python_requires='>=3.8'
)
