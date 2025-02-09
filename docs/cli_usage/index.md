# Usage

## Download manga, cover manga, chapter or list

```shell
# Manga
mangadex-dl "https://mangadex.org/title/..."

# Cover manga
mangadex-dl "https://mangadex.org/covers/..."

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
mangadex-dl "https://mangadex.org/chapter/34"
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

## Download from a forums thread

```sh
mangadex-dl "https://forums.mangadex.org/threads/..."

# An example
mangadex-dl "https://forums.mangadex.org/threads/whats-your-top-3-manga.1082493/"
```

For more info, you can see it here -> {doc}`../cli_ref/forums`

## Batch download

mangadex-downloader support batch downloading. Just type a file and you're good to go !.

Make sure contents of the file are list of MangaDex urls

```shell
# Inside of `urls.txt` file

https://mangadex.org/title/manga_id
https://mangadex.org/chapter/chapter_id
https://mangadex.org/list/list_id
```

Example usage:

```shell
mangadex-dl "insert a file here"
```

````{warning}
If you give invalid path to file that containing MangaDex urls, the app will see it as URL. 
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

mangadex-downloader support download manga as different format. 
For more info about supported formats, you can see it here -> {doc}`../formats`

By default, mangadex-downloader will download in `raw` format. 
Which just a bunch of images stored in each chapter folder. You can use different format by using `--save-as` option.

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

## Download manga, chapter, or list in different translated language

By default, the app will download in English language.
To view all available languages, use `--list-languages` option.

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

### Store in different path / folder

````{note}
Starting v3.0.0 and upper, `--folder`, `--path`, and `-d` options become absolute path

For example, if you store the manga in `mymanga/some_kawaii_manga`. 
The manga and the chapters will be stored under directory `some_kawaii_manga`

```
📂mymanga
 ┗ 📂some_kawaii_manga
 ┃ ┣ 📂Vol. 1 Ch. 1
 ┃ ┃ ┣ 📜00.png
 ┃ ┃ ┣ 📜01.png
 ┃ ┃ ┗ 📜++.png
 ┃ ┣ 📜cover.jpg
 ┃ ┗ 📜download.db
```

You can use placeholders like `{manga.title}` if you comfortable with old behaviour
````

```shell
mangadex-dl "https://mangadex.org/title/..." --folder "./mymanga/some_random_title"

# or

mangadex-dl "https://mangadex.org/title/..." --path "./mymanga/some_random_title"

# or

mangadex-dl "https://mangadex.org/title/..." -d "./mymanga/some_random_title"

# The option also support placeholders, for example:

mangadex-dl "https://mangadex.org/title/..." -d "./mymanga/{manga.title}"
```

For more information about placeholders, you can see {doc}`../cli_ref/path_placeholders`

### Replace existing manga, chapter or list

```shell
mangadex-dl "https://mangadex.org/title/..." --replace
```

### Add chapter title for each folder

```shell
mangadex-dl "https://mangadex.org/title/..." --use-chapter-title
```

By default, mangadex-downloader will add scanlator group name for each chapter folder. 
If you don't want this, use `--no-group-name` option

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

By default, oneshot chapter are downloaded. If you don't want download oneshot chapter, use `--no-oneshot-chapter`.

Example usage:

```shell
mangadex-dl "https://mangadex.org/title/..." --no-oneshot-chapter
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

## Login to MangaDex

You can download private list and manga from your library if you logged in.

```shell
mangadex-dl "https://mangadex.org/list/..." --login
# MangaDex username / email => "insert MangaDex username or email here"
# MangaDex password => "insert MangaDex password here"
# [INFO] Logging in to MangaDex
# [INFO] Logged in to MangaDex
# ...
```

You can specify (username or email) and password without be prompted (less secure) ! 
using `--login-username` and `--login-password`

```shell
mangadex-dl "https://mangadex.org/title/..." --login --login-username "..." --login-password "..."
# [INFO] Logging in to MangaDex
# [INFO] Logged in to MangaDex
# ...
```

Using new authencation system:

```sh
mangadex-dl "https://mangadex.org/title/..." --login --login-method "oauth2" --login-username "username" --login-password "password" --login-api-id "API Client ID" --login-api-secret "API Client Secret"
```

For more information about new authencation system, please refer to {doc}`../cli_ref/oauth`

## Choose and download random manga

In case you wanna try something different, this feature is for you !

Example usage:

```shell
mangadex-dl "random"
```

it also support filters

```shell
mangadex-dl "random" --filter "content_rating=safe, suggestive"
```

For more information, see {doc}`../cli_ref/random`

## Download seasonal manga

Trying to see something good in this season ?

```shell
mangadex-dl "seasonal"
```

For more information, see {doc}`../cli_ref/seasonal_manga`

## Update mangadex-downloader

```shell
mangadex-dl --update
```