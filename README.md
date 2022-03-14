[![pypi-total-downloads](https://img.shields.io/pypi/dm/mangadex-downloader?label=DOWNLOADS&style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![python-ver](https://img.shields.io/pypi/pyversions/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![pypi-release-ver](https://img.shields.io/pypi/v/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)

# mangadex-downloader

A command-line tool to download manga from [MangaDex](https://mangadex.org/), written in [Python](https://www.python.org/).

## Key Features

- Download manga, chapter, or list directly from MangaDex
- Authentication support
- Control how many chapters and pages you want to download
- Compressed images support
- HTTP / SOCKS proxy support
- Multi languages support
- Save as PDF, Comic Book Archive (.cbz) or [Tachiyomi](https://github.com/tachiyomiorg/tachiyomi) local manga

***And ability to not download oneshot chapter***

## Supported formats

mangadex-downloader can download in different formats, here a list of supported formats.

- tachiyomi (the default)
- tachiyomi-zip
- pdf
- pdf-single
- cbz
- cbz-single

For more info about supported formats, you can [read here](https://mangadex-downloader.readthedocs.io/en/latest/formats.html)

## Installation

What will you need:

- Python 3.8.x or up with Pip (if you are in Windows, you can download standalone executable [here](https://github.com/mansuf/mangadex-downloader/releases))

That's it.

### How to (PyPI)

Installing mangadex-downloader is easy, as long as you have requirements above.

```shell
# For Windows
py -3 -m install mangadex-downloader

# For Linux / Mac OS
python3 -m pip install mangadex-downloader
```

You can also install optional dependencies

- [Pillow](https://pypi.org/project/pillow/), for PDF support

There you go, easy ain't it ?.

### How to (Standalone executable)

**NOTE:** This installation only apply to Windows.

Because this is standalone executable, Python are not required to install.

Steps:

- Download latest version here -> https://github.com/mansuf/mangadex-downloader/releases
- Extract it.
- And, run it !.

### How to (Development version)

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
git clone https://github.com/mansuf/mangadex-downloader.git
cd mangadex-downloader
```

## Usage

### Command-Line Interface (PyPI version)

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

### Command-Line Interface (Standalone executable version)

- Navigate to folder where you downloaded mangadex-downloader
- Open "start cmd.bat" (don't worry it's not a virus, it will open a command prompt)

![example_start_cmd](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_start_cmd.png)

- And then start using mangadex-downloader, see example below:

```shell
mangadex-dl.exe "insert MangaDex URL here" 
```

![example_usage_executable](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_usage_executable.png)

For more example usage, you can [read here](https://mangadex-downloader.readthedocs.io/en/latest/cli_usage.html)

For more info about CLI options, you can [read here](https://mangadex-downloader.readthedocs.io/en/latest/cli_ref.html)

### Embedding (API)

```python
from mangadex_downloader import download

download("insert MangaDex URL here")
```

For more information, you can [read here](https://mangadex-downloader.readthedocs.io/en/stable/usage_api.html)
