# Installation

## Stable version

### With PyPI

```shell
# For Windows
py -3 -m pip install mangadex-downloader

# For Linux / Mac OS
python3 -m pip install mangadex-downloader
```

### Compiled app (for Windows only)

Go to latest release in https://github.com/mansuf/mangadex-downloader/releases and download it.

**NOTE**: According to [`pyinstaller`](https://github.com/pyinstaller/pyinstaller) it should support Windows 7,
but its recommended to use it on Windows 8+.


## Development version

```{warning}
This version is not stable and may crash during run.
```

### With PyPI & Git

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
# For Windows
py -3 -m pip install git+https://github.com/mansuf/mangadex-downloader.git

# For Linux / Mac OS
python3 -m pip install git+https://github.com/mansuf/mangadex-downloader.git
```

### With Git only

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
git clone https://github.com/mansuf/mangadex-downloader.git
cd mangadex-downloader
python setup.py install
```