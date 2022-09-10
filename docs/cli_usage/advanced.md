# Advanced usage

## Download a manga with different title

mangadex-downloader also support multi titles manga, which mean you can choose between different titles in different languages !

Example usage:

```shell
mangadex-dl "https://mangadex.org/title/..." --use-alt-details
# Manga "..." has alternative titles, please choose one
# (1). [English]: ...
# (2). [Japanese]: ...
# (3). [Indonesian]: ...
# => 
```

```{warning}
When you already downloaded a manga, but you wanna download it again with different title. It will re-download the whole manga.
```

## Download manga with compressed size images

If you have limited plan or metered network, you can download manga, chapter, or list with compressed size. 
And yes, this may reduce the quality. But hey, atleast it saved you from huge amount of bytes

Example Usage:

```shell
mangadex-dl "https://mangadex.org/title/..." --use-compressed-image
```

## Download manga from logged in user library

```{warning}
This method require authentication
```

mangadex-downloader support download from user library. Just type `library`, login, and select which manga you want to download.

For example:

```shell
mangadex-dl "library" --login
# You will be prompted to input username and password for login to MangaDex
```

You can also apply filter to it !

```shell
# List all mangas with "Reading" status from user library
mangadex-dl "library:reading" --login

# List all mangas with "Plan to read" status from user library
mangadex-dl "library:plan_to_read" --login
```

To list all available filters type `library:help`

```shell
mangadex-dl "library:help"
# ...
```

## Download MangaDex list from logged in user library

```{warning}
This method require authentication
```

You can download MangaDex list from logged in user library. Just type `list`, login, and select mdlist you want to download.

For example:

```shell
mangadex-dl "list" --login
# You will be prompted to input username and password for login to MangaDex
```

Also, you can download mdlist from another user. It will only fetch all public list only.

```{note}
Authentication is not required when download MangaDex list from another user.
```

For example:

```shell
mangadex-dl "list:give_the_user_id_here"
```

## Download MangaDex followed list from logged in user library

```{warning}
This method require authentication
```

You can download MangaDex followed list from logged in user library. Just type `followed-list`, login, and select mdlist you want to download.

```shell
mangadex-dl "followed-list" --login
# You will be prompted to input username and password for login to MangaDex
```

## Download manga from scanlator group

You can download manga from your favorite scanlator groups !. Just type `group:<group-id>`, and then choose which manga you want to download.

```shell
# "Tonikaku scans" group
mangadex-dl "group:063cf1b0-9e25-495b-b234-296579a34496"
```

You can also give the full URL if you want to

```shell
mangadex-dl "group:https://mangadex.org/group/063cf1b0-9e25-495b-b234-296579a34496/tonikaku-scans?tab=titles"
```

This was equal to these command if you use search with filters

```shell
mangadex-dl -s -sf "group=063cf1b0-9e25-495b-b234-296579a34496"
```

## Download manga, chapter, or list from pipe input

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

Also, you can use another options when using pipe

```shell
echo "https://mangadex.org/title/..." | mangadex-dl -pipe --path "/home/myuser" --cover "512px"
```

## Scanlator group filtering

You can download chapters only from 1 scanlation group, by using `--group` option

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

Also, you can use user as filter in `--group` option.

For example:

```shell
mangadex-dl "https://mangadex.org/title/..." --group "https://mangadex.org/user/..."
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
You cannot use `--proxy` and `--proxy-env` together. It will throw error, if you're trying to do it
```

## Special syntax for batch download

To avoid conflict filenames with reserved names (such as: `list`, `library`, `followed-list`) in `URL` argument, 
you can use special syntax for batch download

```
file:<path_to_file>
```

For example:

```shell
mangadex-dl "file:/home/manga/urls.txt"

mangadex-dl "file:list"
```

Also, you can do batch download from web URL location

```{warning}
Make sure the inside contents is raw text and readable.
```

```shell
mangadex-dl "file:https://raw.githubusercontent.com/mansuf/md-test-urls/main/urls.txt"
```

````{warning}
If you give invalid path, the app will throw an error.
See example below

```shell
# Not valid path
$ mangadex-dl "file:not-exist-lol/lmao.txt"
# error: argument URL: File "not-exist-lol/lmao.txt" is not exist

# valid path
$ mangadex-dl "file:yes-it-exist/exist.txt"
# ...
```
````

## Chapters and pages range syntax

mangadex-downloader already have these options for downloading chapters and pages `from n to n`

- `--start-chapter`
- `--end-chapter`
- `--start-page`
- `--end-page`
- `--no-oneshot-chapter`

```{warning}
Currently, this syntax only applied when downloading manga. You cannot use these option when download a chapter or list
```

But, imagine if you want to download specific chapters and pages. 
This is where special syntax for chapters and pages range comes to help.

The format syntax are:

```
chapters[pages]
```

### Supported operators

`````{option} !
Any chapter and page that comes with this operator will be ignored and not downloaded

````{warning}
You cannot use `!` operator with `-`. It will throw an error, if you trying to do it.

For example:

```shell
# Will throw an error because of "!3-30"
mangadex-dl "https://mangadex.org/title/..." --range "1,2,!3-30"
```
````
`````

```{option} -
From `begin` to `end` chapters and pages
```

### Example usage

```shell
mangadex-dl "https://mangadex.org/title/..." --range "1,4,5,6,90"
# Downloaded chapters: 1, 4, 5, 6, 90
```

```shell
mangadex-dl "https://mangadex.org/title/..." --range "1-9,!7,!5,20-30,!25"
# Downloaded chapters:
# 1,2,3,4,6,8,9,20,21,22,23,24,26,27,28,29,30
```

```shell
mangadex-dl "https://mangadex.org/title/..." --range "1[2-20],2[3-15],5[3-9,!5,12]"
# Downloaded chapters
# 1 with pages: 2 to 20
# 2 with pages: 3 to 15
# 3 with pages: 3,4,6,7,8,9,12
```

## Configuration

mangadex-downloader support local config stored in local disk. You must set `MANGADEXDL_CONFIG_ENABLED` to `1` or `true` in order to get working.

```shell
# For Windows
set MANGADEXDL_CONFIG_ENABLED=1

# For Linux / Mac OS
export MANGADEXDL_CONFIG_ENABLED=1
```

These config are stored in local user directory (`~/.mangadex-dl`). If you want to change location to store these config, you can set `MANGADEXDL_CONFIG_PATH` to another path.

```{note}
If new path is doesn't exist, the app will create folder to that location.
```

```shell
# For Windows
set MANGADEXDL_CONFIG_PATH=D:\myconfig\here\lmao

# For Linux / Mac OS
export MANGADEXDL_CONFIG_PATH="/etc/mangadex-dl/config"
```

### Supported configs

```{option} login_cache [1 or 0, true or false]
Same as `--login-cache`
```

```{option} language
Same as `--language` or `-lang`
```

```{option} cover
Same as `--cover` or `-c`
```

```{option} save_as
Same as `--save-as` or `-f`
```

```{option} use_chapter_title [1 or 0, true or false]
Same as `--use-chapter-title` or `-uct`
```

```{option} use_compressed_image [1 or 0, true or false]
Same as `--use-compressed-image` or `-uci`
```

```{option} force_https [1 or 0, true or false]
Same as `--force-https` or `-fh`
```

```{option} path
Same as `--path` or `--folder` or `-d`
```

### Example usage

Set a config

```shell
mangadex-dl "conf:save_as=pdf"
# Successfully changed config save_as from 'raw' to 'pdf'

mangadex-dl "conf:use_chapter_title=1"
# Successfully changed config use_chapter_title from 'False' to 'True'
```

Print all configs

```shell
mangadex-dl "conf"
# Config 'login_cache' is set to '...'
# Config 'language' is set to '...'
# Config 'cover' is set to '...'
# Config 'save_as' is set to '...'
# Config 'use_chapter_title' is set to '...'
# Config 'use_compressed_image' is set to '...'
```

Reset a config back to default value

```shell
mangadex-dl "conf:reset=save_as"
# Successfully reset config 'save_as'
```

## Authentication cache

mangadex-downloader support authentication cache, which mean you can re-use your previous login session in mangadex-downloader 
without re-login.

```{note}
This authentication cache is stored in same place as where [config](#configuration) is stored. If you concerned about security, you can change `MANGADEXDL_CONFIG_PATH` to secured and safe path.
```

You have to enable [config](#configuration) in order to get working.

If you enabled authentication cache for the first time, you must login in order to get cached.

```shell
mangadex-dl "https://mangadex.org/title/..." --login --login-cache

# or

mangadex-dl "conf:login_cache=true"
mangadex-dl "https://mangadex.org/title/..." --login
```

After this command, you no longer need to use `--login` option, 
use `--login` option if you want to update user login.

```shell
# Let's say user "abc123" is already cached
# And you want to change cached user to "def9090"
mangadex-dl "https://mangadex.org/title/..." --login
```

### Available commands

```{option} purge
Purge cached authentication tokens
```

```{option} show
Show expiration time cached authentication tokens 
```

````{option} show_unsafe
```{warning}
You should not use this command, 
because it exposing your auth tokens to terminal screen. 
Use this if you know what are you doing.
```

Show cached authentication tokens
````

### Example usage commands

Purge cached authentication tokens

```shell
mangadex-dl "login_cache:purge"
```

Show expiration time session token and refresh token

```shell
mangadex-dl "login_cache:show"

# or

mangadex-dl "login_cache"
```

## Search filters

mangadex-downloader support search manga with filters. Which mean you can speed up your searching !

For more information about syntax and available filters, see {doc}`../cli_ref/search_filters`

### Example usage

```shell
# Search manhwa with status completed and ongoing, with tags "Comedy" and "Slice of life"
mangadex-dl -s -sf "status=completed,ongoing" -sf "original_language=Korean" -sf "included_tags=4d32cc48-9f00-4cca-9b5a-a839f0764984, e5301a23-ebd9-49dd-a0cb-2add944c7fe9"
```

## Download manga, chapter, or list in forced HTTPS 443 port

To prevent school/office network blocking traffic to non-standard ports. You can use `--force-https` or `-fh` option

For example:

```shell
mangadex-dl "https://mangadex.org/title/..." --force-https
```

## Throttling requests

If you worried about being blocked by MangaDex if you download too much, you can use this feature to throttle requests.

Example usage:

```shell
# Delay requests for each 1.5 seconds
mangadex-dl "https://mangadex.org/title/..." --delay-requests 1.5
```

## Enable DNS-over-HTTPS

mangadex-downloader support DoH (DNS-over-HTTPS). 
You can use it in case your router or ISP being not friendly to MangaDex server.

Example usage

```shell
mangadex-dl "https://mangadex.org/title/..." --dns-over-https cloudflare
```

If you're looking for all available providers, [see here](https://requests-doh.mansuf.link/en/stable/doh_providers.html)

## Set timeout for each HTTP(s) requests

In case if you don't have patience 😁

```shell
# Set timeout for 2 seconds for each HTTP(s) requests
mangadex-dl "https://mangadex.org/title/..." --timeout 2
```

## Auto select choices from selectable prompt command (list, library, followed-list)

In case you didn't want to be prompted, you can use this feature !

```shell
# Automatically select position 1
mangadex-dl "insert keyword here" -s --input-pos "1"

# Select all
mangadex-dl "insert keyword here" -s --input-pos "*"
```

## Disable chapter info creation (or "covers")

In case you didn't want this image appeared in the beginning of every chapters.

![chapter info](../images/chapter_info.png)

You can use `--no-chapter-info` to disable it.

```{note}
It only works for any `volume` and `single` format
```

```shell
mangadex-dl "insert URL here" --no-chapter-info -f pdf-volume
```