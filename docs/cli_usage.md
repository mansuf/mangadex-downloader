# Command-Line Interface (CLI) usage

## Download manga, chapter or list

```shell
# Manga
mangadex-dl "https://mangadex.org/title/..."

# Chapter
mangadex-dl "https://mangadex.org/chapter/..."

# List
mangadex-dl "https://mangadex.org/list/..."

# Or you can just give the id
mangadex-dl "a96676e5-8ae2-425e-b549-7f15dd34a6d8"
```

````{warning}
If you want to download private list and you own that list, you must login by using `--login` option. Otherwise
you will get error "List ... cannot be found"

```shell
mangadex-dl "https://mangadex.org/list/..." --login
# You will be prompted to input (username or email) and password
```
````

mangadex-downloader also support old MangaDex url

```shell
# Old manga url
mangadex-dl "https://mangadex.org/title/123"

# Old chapter url
mangadex-dl "https://mangadex.org/title/34"
```

````{warning}
Old MangaDex url only support full URL, not just the id. If you just provide old id, it will not work.

For example
```shell
# This will work
mangadex-dl "https://mangadex.org/title/34"

# This will NOT work
mangadex-dl "34"
```
````

By default, mangadex-downloader will detect MangaDex url type. It it's valid manga url it will download manga, if it's valid chapter url it will download chapter, etc. However, if you want to skip checking url type or having a weird issue (ex: the provided url are manga type, but when downloaded it become chapter or list), you can use `--type` option with valid url type. 

For example:

```shell
# Manga
mangadex-dl "a96676e5-8ae2-425e-b549-7f15dd34a6d8" --type manga

# Chapter 
mangadex-dl "https://mangadex.org/chapter/7f9d162c-484b-46e9-a717-673a782f69a0" --type chapter

# List
mangadex-dl "https://mangadex.org/list/96518582-2253-47c0-954f-3f00756b3b54/test-manga" --type list

# Old Manga url
mangadex-dl "https://mangadex.org/title/123" --type legacy-manga

# Old chapter url
mangadex-dl "https://mangadex.org/chapter/123" --type legacy-chapter

```

## Batch download

mangadex-downloader support batch downloading. Just type a file and you're good to go !.

Make sure contents of the file are list of MangaDex urls

```
https://mangadex.org/title/manga_id
https://mangadex.org/chapter/chapter_id
https://mangadex.org/list/list_id
```

Example usage:

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

## Download manga, chapter or list in different format

mangadex-downloader support download manga as different format. For more info about supported formats, you can see it here -> :doc:`formats`

By default, mangadex-downloader will download in `raw` format. Which just a bunch of images stored in each chapter folder. You can use different format by using `--save-as` option.

```shell
# Save as .pdf
mangadex-dl "https://mangadex.org/title/..." --save-as pdf

# Save as .cbz
mangadex-dl "https://mangadex.org/title/..." --save-as cbz

# Save as raw
mangadex-dl "https://mangadex.org/title/..." --save-as raw
```

## Search a manga and then download it

mangadex-downloader support search and download. You can use it by adding `--search` option.

```shell
mangadex-dl "komi san" --search
# Output:
# =============================
# Search results for "komi san"
# =============================
# (1). ...
# (2). ...
# (3). ...
# (4). ...
# (5). ...
# (6). ...
# (7). ...
# (8). ...
# (9). ...
# (10). ...

# type "next" to show next results
# type "previous" to show previous results
# =>
# ...
```

## Pipe input

mangadex-downloader support pipe input. You can use it by adding `-pipe` option.

```shell
echo "https://mangadex.org/title/..." | mangadex-dl -pipe
```

Multiple lines input also supported.

```shell
# For Linux / Mac OS
cat "urls.txt" | mangadex-dl -pipe

# For Windows
type "urls.txt" | mangadex-dl -pipe
```

## Download manga, chapter, or list in different translated language

By default, the app will download in English language.
To view all available languages, use --list-languages option.

```shell
mangadex-dl --list-languages
# ...
```

An example downloading a manga in Indonesian language.

```shell
mangadex-dl "https://mangadex.org/title/..." --language "id"
mangadex-dl "https://mangadex.org/title/..." --language "Indonesian"
```

## File management

mangadex-downloader support store in different path / folder.

```shell
mangadex-dl "https://mangadex.org/title/..." --folder "insert folder here"
```

It also support replace existing manga, chapter or list

```shell
mangadex-dl "https://mangadex.org/title/..." --replace
```

Also, you can add chapter title for each folder.

```shell
mangadex-dl "https://mangadex.org/title/..." --use-chapter-title
```

By default, mangadex-downloader will add scanlator group name for each chapter folder. If you don't want this, use `--no-group-name` option

```shell
mangadex-dl "https://mangadex.org/title/..." --no-group-name
```

## Chapters and pages range

mangadex-downloader support download manga with specified range chapters and pages

```shell
# This will download chapters from 20 to 69
mangadex-dl "https://mangadex.org/title/..." --start-chapter 20 --end-chapter 69

# This will download chapters from 20 to 69 and pages from 5 to 20
mangadex-dl "https://mangadex.org/title/..." --start-chapter 20 --end-chapter 69 --start-page 5 --end-page 20
```

```{warning}
If you use `--start-page` and `--end-page` when downloading manga it will download all chapter with specified range pages
```

You can use `--start-page` and `--end-page` too when downloading a chapter

```shell
mangadex-dl "https://mangadex.org/chapter/..." --start-page 5 --end-page 20
```

````{warning}
You can't use these options when downloading a list. If you're trying to do that, it will throw a error.

```shell
mangadex-dl "https://mangadex.org/list/..." --start-chapter 20 --end-chapter 69
# Output: [ERROR] --start-chapter is not allowed when download a list
```
````

## Oneshot chapter

By default, oneshot chapter are downloaded. If you don't want download oneshot chapter, use `--no-oneshot-chapter`.

Example usage:

```shell
mangadex-dl "https://mangadex.org/title/..." --no-oneshot-chapter
```

## Scanlator group filtering

By default, mangadex-downloader will download chapters provided by MangaDex API (https://api.mangadex.org/manga/{manga_id}/aggregate). To prevent conflict, only chapters selected by MangaDex API are downloaded, other same chapters but different groups are not downloaded.

How it works:

```jsonc
// An example json data from https://api.mangadex.org/manga/{manga_id}/aggregate
{
    result: "ok",
    volumes: {
        1: {
            volume: "1",
            count: 1,
            chapters: {
                1: {
                    chapter: "1",
                    id: "...", // The app will only download from this id
                    others: [ 
                        "...", // This are not downloaded
                        "...", // This are not downloaded
                        "..."  // This are not downloaded
                    ],
                    count: 1
                }
            }
        }
    }
}
```

You can download chapters with only from 1 scanlation group, by using `--group` option

```shell
# This will download all chapters from group "Tonikaku scans" only
mangadex-dl "https://mangadex.org/title/..." --group "https://mangadex.org/group/063cf1b0-9e25-495b-b234-296579a34496/tonikaku-scans"
```

You can download all same chapters with different groups, by using `--group` option with value "all"

```shell
# This will download all chapters, regardless of scanlation groups
mangadex-dl "https://mangadex.org/title/..." --group "all"
```

```{warning}
You cannot use `--group all` and `--no-group-name` together. It will throw error, if you're trying to do it
```

## Download a manga with different title

mangadex-downloader also support multi titles manga, which mean you can choose between different titles in different languages !.

Example usage:

```shell
mangadex-dl "https://mangadex.org/title/..." --use-alt-details
```

```{warning}
When you already downloaded a manga, but you wanna download it again with different title. It will re-download the whole manga.
```

## Manga cover

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

## Download manga with compressed size images

```shell
mangadex-dl "https://mangadex.org/title/..." --use-compressed-image
```

## Login to MangaDex

With this, you can gain such power to download private list, etc.

```shell
mangadex-dl "https://mangadex.org/list/..." --login
# MangaDex username / email => "insert MangaDex username or email here"
# MangaDex password => "insert MangaDex password here"
# [INFO] Logging in to MangaDex
# [INFO] Logged in to MangaDex
# ...
```

You can specify (username or email) and password without be prompted (less secure) ! using `--login-username` and `--login-password`

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

## Old sorting images technique

If you have problems like [this](https://github.com/mansuf/mangadex-downloader/issues/10), you might want to enable optional feature called "legacy sorting". This will rename chapter images to numbers with leading zeros.

Example usage:

```shell
mangadex-dl "https://mangadex.org/title/..." --enable-legacy-sorting
```


## Update mangadex-downloader

```shell
mangadex-dl --update
```