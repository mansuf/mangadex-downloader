# Command-Line Interface (CLI) example usage

## Download a manga

```shell
mangadex-dl "https://mangadex.org/title/..."
```

## Download multiple mangas from a file

```shell
mangadex-dl "insert a file here"
```

````{warning}
If you specify invalid path to file that containing MangaDex urls, the app will see it as URL. 
See example below

```shell
# Not valid path
$ mangadex-dl "not-exist-lol/lmao.txt"
# error: argument URL: Invalid MangaDex URL or manga id

# valid path
$ mangadex-dl "yes-it-exist/exist.txt"
# ...
```
````

## Download a chapter or MangaDex list

```shell
# This will download a chapter
mangadex-dl "https://mangadex.org/chapter/..."

# This will download a list
mangadex-dl "https://mangadex.org/list/..."
```

````{warning}
If you want to download private list and you own that list, you must login by using `--login` option. Otherwise
you will get error "List ... cannot be found"

```shell
mangadex-dl "https://mangadex.org/list/..." --login
# You will be prompted to input username and password
```
````

## Download manga and store it in different folder

```shell
mangadex-dl "https://mangadex.org/title/..." --folder "insert folder here"
```

## Replace manga if exist

```shell
mangadex-dl "https://mangadex.org/title/..." --replace
```

## Download manga in different translated language

```shell
# By default, the app will download in english language
# To view all available languages, use --list-languages option
mangadex-dl "--list-languages"

# Indonesian langauge
mangadex-dl "https://mangadex.org/title/..." --language "id"
mangadex-dl "https://mangadex.org/title/..." --language "Indonesian"
```

## Download manga from chapter 20 to 69

```shell
mangadex-dl "https://mangadex.org/title/..." --start-chapter 20 --end-chapter 69
```

````{warning}
This option will not work if you download a list, it will throw a error if you try to do it.

For example

```shell
mangadex-dl "https://mangadex.org/list/..." --start-chapter 20 --end-chapter 69
# Output: [ERROR] --start-chapter is not allowed when download a list
```
````

## Download chapter with page from 5 to 20

```shell
mangadex-dl "https://mangadex.org/chapter/..." --start-page 5 --end-page 20
```

You can do this too when downloading manga

```shell
mangadex-dl "https://mangadex.org/title/..." --start-page 5 --end-page 20 
```


```{warning}
If you use that when downloading manga it will download all chapter with page from 5 to 20
```

````{warning}
This option will not work if you download a list, it will throw a error if you try to do it.

For example

```shell
mangadex-dl "https://mangadex.org/list/..." --start-page 5 --end-page 20
# Output: [ERROR] --start-page is not allowed when download a list
```
````

# Manga cover related

```shell
# Download manga with original quality cover (the default)
mangadex-dl "https://mangadex.org/title/..." --cover "original"

# 512px quality
mangadex-dl "https://mangadex.org/title/..." --cover "512px"

# 256px quality
mangadex-dl "https://mangadex.org/title/..." --cover "256px"

# No cover
mangadex-dl "https://mangadex.org/title/..." --cover "none"
```

# Download manga with compressed size images

```shell
mangadex-dl "https://mangadex.org/title/..." --use-compressed-image
```

## Login to MangaDex

With this, you can gain such power to download private list, etc.

```shell
mangadex-dl "https://mangadex.org/list/..." --login
# MangaDex username => "insert MangaDex username here"
# MangaDex password => "insert MangaDex password here"
# [INFO] Logging in to MangaDex
# [INFO] Logged in to MangaDex
# ...
```

You can specify username and password without be prompted (less secure) ! using `--login-username` and `--login-password`

```shell
mangadex-dl "https://mangadex.org/title/..." --login --login-username "..." --login-password "..."
# [INFO] Logging in to MangaDex
# [INFO] Logged in to MangaDex
# ...
```

## Setup proxy

```shell
# HTTP proxy
mangadex-dl "https://mangadex.org/title/..." --proxy "http://127.0.0.1"

# SOCKS proxy
mangadex-dl "https://mangadex.org/title/..." --proxy "socks://127.0.0.1"
```

mangadex-downloader support proxy from environments

```shell
# For Linux / Mac OS
export http_proxy="http://127.0.0.1"
export https_proxy="http://127.0.0.1"

# For Windows
set http_proxy=http://127.0.0.1
set https_proxy=http://127.0.0.1

mangadex-dl "insert mangadex url here" --proxy-env
```

```{warning}
If you specify ``--proxy`` with ``--proxy-env``, ``--proxy`` option will be ignored
```

## Update mangadex-downloader

```shell
mangadex-dl --update
```