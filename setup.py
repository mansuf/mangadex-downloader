import pathlib
import re
from setuptools import setup, find_packages

# Root directory
# (README.md, mangadex_downloader/__init__.py)
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
init_file = (HERE / "mangadex_downloader/__init__.py").read_text()

def get_version():
    """Get version of the app"""
    re_version = r'__version__ = \"([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})\"'
    _version = re.search(re_version, init_file)

    if _version is None:
        raise RuntimeError("Version is not set")

    return _version.group(1)

def get_description():
    """Get description of the app"""
    re_description = r'__description__ = \"(.{1,})\"'
    _description = re.search(re_description, init_file)

    if _description is None:
        raise RuntimeError("Description is not set")

    return _description.group(1)

def get_license():
    """Get license of the app"""
    re_license = r'__license__ = "(.{1,})"'
    _license = re.search(re_license, init_file)

    if _license is None:
        raise RuntimeError("License is not set")
    
    return _license.group(1)

def get_author():
    """Get author of the app"""
    re_author = r'__author__ = "(.{1,})"'
    _author = re.search(re_author, init_file)

    if _author is None:
        raise RuntimeError("Author is not set")
    
    return _author.group(1)

def get_repository():
    """get git repository of the app"""
    re_repo = r'__repository__ = "(.{1,})"' 
    _repo = re.search(re_repo, init_file)

    if _repo is None:
        raise RuntimeError("Repository is not set")
    
    return _repo.group(1)

def get_requirements():
    """Return tuple of library needed for app to run"""
    main = []
    try:
        with open('./requirements.txt', 'r') as r:
            main = r.read().splitlines()
    except FileNotFoundError:
        raise RuntimeError("requirements.txt is needed to build mangadex-downloader")

    if not main:
        raise RuntimeError("requirements.txt have no necessary libraries inside of it")

    docs = []
    try:
        with open('./requirements-docs.txt', 'r') as r:
            docs = r.read().splitlines()
    except FileNotFoundError:
        # There is no docs requirements
        # Developers can ignore this error and continue to install without any problem.
        # However, this is needed if developers want to create documentation in readthedocs.org or local device.
        pass

    optional = []
    try:
        with open('./requirements-optional.txt', 'r') as r:
            optional = r.read().splitlines()
    except FileNotFoundError:
        raise RuntimeError("requirements-optional.txt is needed to build mangadex-downloader")

    if not optional:
        raise RuntimeError("requirements-optional.txt have no necessary libraries inside of it")

    return main, {
        "docs": docs,
        "optional": optional
    }

# Get requirements needed to build app
requires_main, extras_require = get_requirements()

# Get all modules
packages = find_packages('.')

# Get repository
repo = get_repository()

# Finally run main setup
setup(
    name = 'mangadex-downloader',         
    packages = packages,   
    version = get_version(),
    license=get_license(),
    description = get_description(),
    long_description= README,
    long_description_content_type= 'text/markdown',
    author = get_author(),              
    author_email = 'danipart4@gmail.com',
    url = f'https://github.com/{repo}',
    download_url = f'https://github.com/{repo}/releases',
    keywords = ['mangadex'], 
    install_requires=requires_main,
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
