# mangadex-downloader

Download manga from Mangadex through Python

### Installation
```
pip install mangadex-downloader
```

### Features

- Download manga directly with python from mangadex
- Extract all information manga from mangadex
- [Tachiyomi](https://github.com/tachiyomiorg/tachiyomi) support

### Usage

```python
from mangadex_downloader import Mangadex

# by default, verbose is False
m = Mangadex(verbose=True)

# if you want to see all information in manga
# plus you want to download it
# do: m.extract_info('give mangadex url here')
# see example below

# this will download all chapters in manga 
info = m.extract_info('https://mangadex.org/title/43610/my-tiny-senpai-from-work')

print(info)
# Output: <MangaData title="My Tiny Senpai From Work" chapters=51 language=jp>

print(info.title)
# Output: 'My Tiny Senpai From Work'

print(info.chapters)
# Output: [{'language': 'English': 'url': ..., 'group': ..., 'uploader': ..., 'volume': ..., 'chapter': ..., 'chapter-id': ...}, ...]

# or, you want to see all information in manga
# but you don't wanna download it
# do: m.extract_info('give mangadex url here', download=False)
# see example below

# this will NOT download all chapters in manga
info = m.extract_info('https://mangadex.org/title/43610/my-tiny-senpai-from-work', download=False)

...

# Also, you can use secondary server to download manga
# by passing use_secondary_server to Mangadex.donwload()
# and Mangadex.extract_info()
# Secondary server can be used if primary server is slow to download
# in my experience using this, secondary server always fast (well sometimes...)

# by default use_secondary_server is False
info = m.extract_info('https://mangadex.org/title/43610/my-tiny-senpai-from-work', use_secondary_server=True)
m.download('https://mangadex.org/title/43610/my-tiny-senpai-from-work', use_secondary_server=True)

# New in v0.0.4
# You can pass data_saver argument in Mangdex.download()
# and Mangadex.extract_info()

# If data_saver is True
# Mangadex class will request data-saver image to Mangadex
# to use less size and low quality image

# by default, data_saver argument is False
info = m.extract_info('https://mangadex.org/title/43610/my-tiny-senpai-from-work', data_saver=True)
m.download('https://mangadex.org/title/43610/my-tiny-senpai-from-work', data_saver=True)

...

# New in v0.0.4 
# added Mangadex.extract_basic_info()
# grab all information in manga without the chapters
info = m.extract_basic_info('https://mangadex.org/title/43610/my-tiny-senpai-from-work')

print(info)
# Output: <MangaData title="My Tiny Senpai From Work" chapters=51 language=jp>

print(info.chapters)
# Output: None

# if want to download a list containing mangadex urls
# do: m.download('mangadex urls', 'mangadex urls', ...)
# see example below

# this will download all urls
m.download(
  'https://mangadex.org/title/43610/my-tiny-senpai-from-work',
  'https://mangadex.org/title/23279/wonder-cat-kyuu-chan',
  'https://mangadex.org/title/23439/tonikaku-cawaii'
)

```


### Minimum Python version
```
Python 3.x
```
