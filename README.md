[![pypi-total-downloads](https://img.shields.io/pypi/dm/mangadex-downloader?label=DOWNLOADS&style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![python-ver](https://img.shields.io/pypi/pyversions/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![pypi-release-ver](https://img.shields.io/pypi/v/mangadex-downloader?style=for-the-badge)](https://pypi.org/project/mangadex-downloader)
[![](https://dcbadge.limes.pink/api/server/NENvQ5b5Pt)](https://discord.gg/NENvQ5b5Pt)

# mangadex-downloader

[![Indonesian](https://img.shields.io/badge/Language-Indonesian-blue.svg)](https://github.com/mansuf/mangadex-downloader/blob/main/README.id.md)
[![Turkish](https://img.shields.io/badge/Language-Turkish-blue.svg)](https://github.com/mansuf/mangadex-downloader/blob/main/README.tr.md)

A command-line tool to download manga from [MangaDex](https://mangadex.org/), written in [Python](https://www.python.org/).

## Table of Contents

- [Key Features](#key-features)
- [Image Upscaling](#image-upscaling)
- [Supported formats](#supported-formats)
- [Installation](#installation)
    - [Python Package Index (PyPI)](#installation-pypi)
    - [Bundled executable](#installation-bundled-executable)
    - [Docker](#installation-docker)
    - [Development version](#installation-development-version)
- [Usage](#usage)
    - [PyPI version](#usage-pypi-version)
    - [Bundled executable version](#usage-bundled-executable-version)
    - [Docker version](#usage-docker-version)
- [Contributing](#contributing)
- [Donation](#donation)
- [Support](#support)
- [Links](#links)
- [Disclaimer](#disclaimer)

## Key Features <a id="key-features"></a>

- Download manga, cover manga, chapter, or list directly from MangaDex
- Download manga or list from user library
- Find and download MangaDex URLs from MangaDex forums ([https://forums.mangadex.org/](https://forums.mangadex.org/))
- Download manga in each chapters, each volumes, or wrap all chapters into single file
- Search (with filters) and download manga
- Filter chapters with scalantion groups or users
- Manga tags, groups, and users blacklist support
- Batch download support
- Authentication (with cache) support
- Control how many chapters and pages you want to download
- Multi languages support
- Legacy MangaDex url support
- Save as raw images, EPUB, PDF, Comic Book Archive (.cbz or .cb7)
- Respect API rate limit
- **Optional image upscaling (2x or 4x) using Real-ESRGAN with hardware acceleration.**
- Hash-based verification and caching for upscaled images to avoid unnecessary reprocessing

***And ability to not download oneshot chapter***

## Image Upscaling <a id="image-upscaling"></a>

This tool supports optional 2x or 4x image upscaling using Real-ESRGAN. The implementation is optimized for different platforms to provide the best performance.

### Backends
- **macOS (Apple Silicon):** Uses a native Core ML backend that leverages the Apple Neural Engine for hardware acceleration. This results in extremely fast and efficient upscaling with minimal CPU/GPU usage.
  - 2x model: `RealESRGAN_x2plus`
  - 4x model: `RealESRGAN_x4plus_anime_6B` (optimized for anime/manga, default)
- **Linux / Windows:** Uses a PyTorch-based backend that can leverage CUDA-enabled NVIDIA GPUs for acceleration, with a fallback to CPU if a compatible GPU is not available.
  - 2x model: `RealESRGAN_x2plus`
  - 4x model: `RealESRGAN_x4plus_anime_6B` (optimized for anime/manga, default)

### How to Use
To enable upscaling, simply add the `--upscale` flag to your download command. The tool will automatically select the best backend for your system and use 4x scaling by default.

**Basic usage:**
```shell
mangadex-dl "insert MangaDex URL here" --upscale                     # 4x upscaling (default)
mangadex-dl "insert MangaDex URL here" --upscale --upscale-scale 2   # 2x upscaling
mangadex-dl "insert MangaDex URL here" --upscale --upscale-scale 4   # 4x upscaling (explicit)
```

The upscaler will perform scaling on all downloaded images. The process is cached, so running the command again on the same images will not re-upscale them unless the original files have changed.

For the best experience, especially on macOS, ensure you have the optional dependencies installed:
```shell
pip install "mangadex-downloader[optional,upscale]"
```

## Supported formats <a id="supported-formats"></a>

[Read here](https://mangadex-dl.mansuf.link/en/latest/formats.html) for more info.

## Installation <a id="installation"></a>

What will you need:

- Python 3.10.x or up with Pip (if you are in Windows, you can download bundled executable. [See this instructions how to install it](#installation-bundled-executable))
- If you plan to use the optional upscaling feature, install with Python > 3.10.x <= 3.12.x where the Real-ESRGAN toolkit currently provides wheels.

That's it.

### Python Package Index (PyPI) <a id="installation-pypi"></a>

Installing mangadex-downloader is easy, as long as you have requirements above.

```shell
# For Windows
py -3 -m pip install mangadex-downloader

# For Linux / Mac OS
python3 -m pip install mangadex-downloader
```

You can also install optional dependencies

- [py7zr](https://pypi.org/project/py7zr/) for cb7 support
- [orjson](https://pypi.org/project/orjson/) for maximum performance (fast JSON library)
- [lxml](https://pypi.org/project/lxml/) for EPUB support
- Real-ESRGAN upscaling (requires Python > 3.10.x, <= 3.12.x):
  - **macOS**: `coremltools>=7.0`
  - **Linux/Windows**: `torch`, `torchvision`, `opencv-python`, `realesrgan`

Or you can install all optional dependencies together. For upscaling we recommend installing both the regular optional extras and the upscaling extras:

```shell
# For Windows
py -3 -m pip install "mangadex-downloader[optional,upscale]"

# For Mac OS / Linux
python3 -m pip install "mangadex-downloader[optional,upscale]"
```

There you go, easy ain't it ?.

### Bundled executable <a id="installation-bundled-executable"></a>

**NOTE:** This installation only apply to Windows.

Because this is bundled executable, Python are not required to install.

Steps:

- Download latest version here -> https://github.com/mansuf/mangadex-downloader/releases
- Extract it.
- That's it ! You have successfully install mangadex-downloader. 
[See this instructions to run mangadex-downloader](#usage-bundled-executable-version)

### Docker <a id="installation-docker"></a>

Available at:
- https://hub.docker.com/r/mansuf/mangadex-downloader
- https://gallery.ecr.aws/mansuf/mangadex-downloader

```sh
# Dockerhub
docker pull mansuf/mangadex-downloader

# AWS ECR (Alternative)
docker pull public.ecr.aws/mansuf/mangadex-downloader
```

If you want to get optional features such as image upscaling (Real-ESRGAN), `EPUB` support, `cb7` support, etc.
You can use tag ending with `-optional`

```sh
# Dockerhub
docker pull mansuf/mangadex-downloader:latest-optional
docker pull mansuf/mangadex-downloader:v3.1.4-optional

# AWS ECR (Alternative)
docker pull public.ecr.aws/mansuf/mangadex-downloader:latest-optional
docker pull public.ecr.aws/mansuf/mangadex-downloader:v3.1.4-optional
```

**NOTE**: If you're wondering why optional tags doesn't have arm/v6 platform support. 
That's because some dependencies (most notably `orjson`) require rust compiler 
and i give up installing rust compiler in arm/v6 platform, there is too much errors for me. 

### Development version <a id="installation-development-version"></a>

**NOTE:** You must have git installed. If you don't have it, install it from here https://git-scm.com/.

```shell
git clone https://github.com/mansuf/mangadex-downloader.git
cd mangadex-downloader
python setup.py install # or "pip install ."
```

## Usage <a id="usage"></a>

### PyPI version <a id="usage-pypi-version"></a>

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

To upscale images after download, see the [Image Upscaling](#image-upscaling) section for more details.

### Bundled executable version <a id="usage-bundled-executable-version"></a>

- Navigate to folder where you downloaded mangadex-downloader
- Open "start cmd.bat" (don't worry it's not a virus, it will open a command prompt)

![example_start_cmd](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_start_cmd.png)

- And then start using mangadex-downloader, see example below:

```shell
mangadex-dl.exe "insert MangaDex URL here" 
```

![example_usage_executable](https://raw.githubusercontent.com/mansuf/mangadex-downloader/main/assets/example_usage_executable.png)

### Docker version <a id="usage-docker-version"></a>

The downloaded files in the container are stored in `/downloads` directory

```sh
# Dockerhub
docker run --rm -v /home/sussyuser/sussymanga:/downloads mansuf/mangadex-downloader "insert MangaDex URL"

# AWS ECR (alternative)
docker run --rm -v /home/sussyuser/sussymanga:/downloads public.ecr.aws/mansuf/mangadex-downloader "insert MangaDex URL"
```

For more example usage, you can [read here](https://mangadex-dl.mansuf.link/en/stable/cli_usage/index.html)

For more info about CLI options, you can [read here](https://mangadex-dl.mansuf.link/en/stable/cli_ref/index.html)

## Contributing <a id="contributing"></a>

See [CONTRIBUTING.md](https://github.com/mansuf/mangadex-downloader/blob/main/CONTRIBUTING.md) for more info

## Donation <a id="donation"></a>

If you like this project, please consider donate to one of these websites:

- [Sociabuzz](https://sociabuzz.com/mansuf/donate)
- [Ko-fi](https://ko-fi.com/rahmanyusuf)
- [Github Sponsor](https://github.com/sponsors/mansuf)

Any donation amount will be appreciated 💖

## Support <a id="support"></a>

Need help ? Have questions or you just wanna chat ?

[Come join to discord server](https://discord.gg/NENvQ5b5Pt)

Please note, that the Discord server is really new and it doesn't have anything on it. So please be respect and kind.

## Links <a id="links"></a>

- [PyPI](https://pypi.org/project/mangadex-downloader/)
- [Docs](https://mangadex-dl.mansuf.link)
- [Discord Server (Mostly for questions and support)](https://discord.gg/NENvQ5b5Pt)

## Disclaimer <a id="disclaimer"></a>

mangadex-downloader are not affiliated with MangaDex. Also, the current maintainer ([@mansuf](https://github.com/mansuf)) is not a MangaDex dev
