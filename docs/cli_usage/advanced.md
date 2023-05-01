# Advanced usage

## Show list of manga covers and download it

Wanna download the cover only ? I got you

```shell
# Manga id only
mangadex-dl "cover:manga_id"

# Full manga URL
mangadex-dl "cover:https://mangadex.org/title/..."

# Full cover manga URL
mangadex-dl "cover:https://mangadex.org/covers/..."
```

Don't wanna get prompted ? Use `--input-pos` option !

```sh
# Automatically select choice 1 
mangadex-dl "cover:https://mangadex.org/title/..." --input-pos 1 

# Automatically select all choices
mangadex-dl "cover:https://mangadex.org/title/..." --input-pos "*"
```

```{note}
This will download covers in original quality. 
If you want to use different quality, use command `cover-512px` for 512px quality 
and `cover-256px` for 256px quality.
```

For more information, see {doc}`../cli_ref/cover`

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
mangadex-dl -s -ft "group=063cf1b0-9e25-495b-b234-296579a34496"
```

## Blacklist a group or user

Sometimes you don't like the chapter that this user or group upload it. 
You can use this feature to prevent the chapter being downloaded.

**Group**

```shell
# For Windows
set MANGADEXDL_GROUP_BLACKLIST=4197198b-c99b-41ae-ad21-8e6ecc10aa49, 0047632b-1390-493d-ad7c-ac6bb9288f05

# For Linux / Mac OS
export MANGADEXDL_GROUP_BLACKLIST=4197198b-c99b-41ae-ad21-8e6ecc10aa49, 0047632b-1390-493d-ad7c-ac6bb9288f05
```

**User**

```shell
# For Windows
set MANGADEXDL_USER_BLACKLIST=1c4d814e-b1c1-4b75-8a69-f181bb4e57a9, f8cc4f8a-e596-4618-ab05-ef6572980bbf

# For Linux / Mac OS
export MANGADEXDL_USER_BLACKLIST=1c4d814e-b1c1-4b75-8a69-f181bb4e57a9, f8cc4f8a-e596-4618-ab05-ef6572980bbf
```

For more information, see {doc}`../cli_ref/env_vars`

## Blacklist one or more tags

Sometimes you don't like manga that has **some** tags. You can use this feature to prevent the manga being downloaded.

```shell
# For Windows
set MANGADEXDL_TAGS_BLACKLIST=gore, sexual violence, oneshot

# For Linux / Mac OS
export MANGADEXDL_TAGS_BLACKLIST=gore, sexual violence, oneshot
```

For more information, see {doc}`../cli_ref/env_vars`

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

For example:

```shell
mangadex-dl "file:/home/manga/urls.txt"

mangadex-dl "file:list"
```

For more information, see {doc}`../cli_ref/file_command`

<!-- ## Chapters and pages range syntax

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
``` -->

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

Example usage

```shell
mangadex-dl "conf:save_as=pdf"
# Successfully changed config save_as from 'raw' to 'pdf'

mangadex-dl "conf:use_chapter_title=1"
# Successfully changed config use_chapter_title from 'False' to 'True'
```

For more information, you can see -> {doc}`../cli_ref/config`

## Authentication cache

mangadex-downloader support authentication cache, which mean you can re-use your previous login session in mangadex-downloader 
without re-login.

```{note}
This authentication cache is stored in same place as where [config](#configuration) is stored.
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

For more information, you can see here -> {doc}`../cli_ref/auth_cache`

## Filters

mangadex-downloader support filters. These filters applied to search and random manga.

Example usage (Search manga)

```shell
# Search manhwa with status completed and ongoing, with tags "Comedy" and "Slice of life"
mangadex-dl -s -ft "status=completed,ongoing" -ft "original_language=Korean" -ft "included_tags=comedy, slice of life"

# or

mangadex-dl -s -ft "status=completed,ongoing" -ft "original_language=Korean" -ft "included_tags=4d32cc48-9f00-4cca-9b5a-a839f0764984, e5301a23-ebd9-49dd-a0cb-2add944c7fe9"
```

Example usage (Random manga)

```shell
# Search manga with tags "Comedy" and "Slice of life"
mangadex-dl "random" -ft "included_tags=comedy, slice of life"

# or

mangadex-dl "random" -ft "included_tags=4d32cc48-9f00-4cca-9b5a-a839f0764984, e5301a23-ebd9-49dd-a0cb-2add944c7fe9"
```

For more information about syntax and available filters, see {doc}`../cli_ref/filters`

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

## Enable chapter info creation (or "covers")

In case you want this image appeared in the beginning of every chapters.

![chapter info](../images/chapter_info.png)

You can use `--use-chapter-cover` to enable it.

```{note}
It only works for any `volume` and `single` format
```

```shell
mangadex-dl "insert URL here" --use-chapter-cover -f pdf-volume
```