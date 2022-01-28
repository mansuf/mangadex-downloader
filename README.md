[![pypi-total-downloads](https://img.shields.io/pypi/dm/mangadex-downloader?label=DOWNLOADS&style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![python-ver](https://img.shields.io/pypi/pyversions/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![pypi-release-ver](https://img.shields.io/pypi/v/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)


# mangadex-downloader

Download manga from Mangadex through Python

## Key Features

- Download manga directly from MangaDex 
- Authentication support (login and logout)
- Control how many chapters you want to download
- Ability to use compressed images (if you want to)
- HTTP / SOCKS proxy support
- [Tachiyomi](https://github.com/tachiyomiorg/tachiyomi) local files support

## Minimum Python version
```
Python 3.5.x
```

## Installation

### From PyPI

```shell
# For Windows
py -3 -m install mangadex-downloader

# For Linux / Mac OS
python3 -m pip install mangadex-downloader
```

### From Git 

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
# For Windows
py -3 -m pip install git+https://github.com/mansuf/mangadex-downloader.git@v0.2.0

# For Linux / Mac OS
python3 -m pip install git+https://github.com/mansuf/mangadex-downloader.git@v0.2.0
```

## Usage

**NOTE:** This app will download manga in english language only. Other languages will be implemented soon.

### Command Line Interface (CLI)

```shell

mangadex-dl "insert MangaDex URL here" 
# or
mangadex-downloader "insert MangaDex URL here" 

# Use this if "mangadex-dl" or "mangadex-downloader" didn't work

# For Windows
py -3 -m mangadex_downloader "insert MangaDex URL here" 

# For Linux / Mac OS
python3 -m mangadex_downloader "insert MangaDex URL here" 
```

For more information, you can [read here](https://mangadex-downloader.readthedocs.io/en/latest/usage_cli.html)

### Embedding (API)

```python
from mangadex_downloader import download

download("insert MangaDex URL here")
```

For more information, you can [read here](https://mangadex-downloader.readthedocs.io/en/latest/usage_api.html)