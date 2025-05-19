# Changelog

## v3.1.4

### Fix bugs

- Fix UnicodeEncodeError when saving manga info in json format
- Fix comic book (.cbz) title metadata [#155](https://github.com/mansuf/mangadex-downloader/pull/155)
- Fix memory leak ? (progress 1)
- Fix application is being falsely flagged by several AVs [#157](https://github.com/mansuf/mangadex-downloader/issues/157)
- Fix volume cover become null when creating chapter info [#159](https://github.com/mansuf/mangadex-downloader/issues/159)
- Fix check_login throwing error when refreshing token from cache [#158](https://github.com/mansuf/mangadex-downloader/issues/158)

## v3.1.3

### Fix bugs

- Fix --use-alt-details is not working due to missing language (lang: Georgian) [#154](https://github.com/mansuf/mangadex-downloader/issues/154)
- Fix chapter cover doesn't work due to CoverArtIterator cache issue [#152](https://github.com/mansuf/mangadex-downloader/issues/152)
- Fix volume number not in EPUB title resulting duplicated entry in comic reader [#149](https://github.com/mansuf/mangadex-downloader/issues/149)

## v3.1.2

### Fix bugs

- Fixed application is left hanging when download is completed (report system is not working) [#146](https://github.com/mansuf/mangadex-downloader/issues/146)
- Fixed validator always not passed for "group_nomatch_behaviour" config
- Fixed negative value when rate-limited [#147](https://github.com/mansuf/mangadex-downloader/issues/147)

## v3.1.1

### Fix bugs

- Fixed migration is not applied properly [#136](https://github.com/mansuf/mangadex-downloader/issues/136) [#133](https://github.com/mansuf/mangadex-downloader/issues/133) [#134](https://github.com/mansuf/mangadex-downloader/issues/134)

### Documentation

- Fix typo in documentation and source code [#130](https://github.com/mansuf/mangadex-downloader/pull/130)

## v3.1.0

### New features

- Added `mihon` manga info format (`--manga-info-format`)

### Fix bugs

- Fixed `--update` option is not working in bundled executable version when updating from v2 to v3
- Fixed `FileNotFoundError` when using `--create-manga-info` with `--manga-info-format=json` [#129](https://github.com/mansuf/mangadex-downloader/issues/129)
- Fixed `--use-volume-cover` always use main cover [#131](https://github.com/mansuf/mangadex-downloader/issues/131)
- Fixed `--no-track` isn't working after updating to v3.0.0 [#133](https://github.com/mansuf/mangadex-downloader/issues/133)

## v3.0.0

### Breaking changes

- Change `--path` behaviour to absolute path with placeholders support
- Now, if a manga that doesn't have no volume, it will get separated (chapters format) rather than being merged into single file called `No volume.cbz` (example). However if you prefer old behaviour (merge no volume chapters into single file) you can use `--create-no-volume`.
- Dropped support for Python v3.8 and v3.9
- Removed `--no-progress-bar` option since it's deprecated (use `--progress-bar-layout=none` instead)
- Removed `--verbose` option since it's deprecated (use `--log-level=DEBUG` instead)
- Removed `--write-tachiyomi-details` option

### Improvements

- Refactored code base using ruff linter and black formatter
- The app now showing `X-Request-ID` if the app encountered `Unhandled HTTP error` that can be reported to MangaDex devs
- Missing dependencies error is now closing the application (do not ignore it)
- `ComicInfo.xml` file are now generated for volumes as well
- Options `--start-page` and `--end-page` are now support negative values (relative to end of chapter)

### New features

- Added `--login-api-id` and `--login-api-secret` to login with OAuth (you must set `--login-method` with value `oauth`)
- Added `--start-volume` and `--end-volume` to start and stop download chapter from given volume number
- Added `--filename-chapter` option to set filename for chapter formats
- Added `--filename-volume` option to set filename for volume formats
- Added `--filename-single` option to set filename for single formats
- Added `--ignore-missing-chapters` option to ignore missing chapters
- Added `--create-manga-info` option to store manga information in a file
- Added `--manga-info-format` option to change file format for manga information file
- Added `--manga-info-filepath` option to change location to store manga information file.
- Added `--manga-info-only` option to download manga information only (no chapters and volumes)
- Added `--order` option to change chapters released order (newest or oldest)
- Added `--group-nomatch-behaviour` to manage `--group` filter behaviour
- Added `--no-metadata` option to disable metadata creation on any cbz formats
- Added `--page-size` option to manage maximum items fit per page in any commands
- Added `--run-forever` to run the app indefinitely until crashed or stopped manually by user

### Fix bugs

- Fix `download.db` is modified if there is not new chapters available. 
- Fix `epub-volume` format doesn't adding cover art
- Fix default volume covers behaviour. (See [#105](https://github.com/mansuf/mangadex-downloader/issues/105) for more info)
- Fix app stopped downloading list when a manga doesn't have chapters

## v2.10.3

### Fix bugs

- Fixed `cover` command is not working if manga doesn't have covers for specified language
[#82](https://github.com/mansuf/mangadex-downloader/issues/82)

## v2.10.2

### Fix bugs

- Fixed `pdf-volume` and `cb7-volume` formats are not working after upgrading to v2.10.x 
[#78](https://github.com/mansuf/mangadex-downloader/issues/78)

## v2.10.1

### Fix bugs

- Fixed `cbz` format are not working after upgrading to v2.10.0 [#74](https://github.com/mansuf/mangadex-downloader/issues/74)

## v2.10.0

### New features

- Added stacked progress bar layout (accessible from `--progress-bar-layout=stacked`) [#65](https://github.com/mansuf/mangadex-downloader/issues/65)
- Added `--volume-cover-language` to change volume cover locale [#66](https://github.com/mansuf/mangadex-downloader/issues/66)
- Added `--log-level` to change logging level [#65](https://github.com/mansuf/mangadex-downloader/issues/65)

### Fix bugs

- Fix inconsistent volume cover locale [#66](https://github.com/mansuf/mangadex-downloader/issues/66)

### Dependencies

- Bump [requests-doh](https://github.com/mansuf/requests-doh) to v0.3.1

### Deprecated

- `--no-progress-bar` is deprecated in favor of `--progress-bar-layout`. This option will be removed in v3.0.0
- `--verbose` is deprecated in favor of `--log-level`. This option will be removed in v3.0.0

## v2.9.1

### Fix bugs

- Fixed `--write-tachiyomi-info` is not working when system locale is set to other language (not English)
[#62](https://github.com/mansuf/mangadex-downloader/issues/62)
- Fixed `--write-tachiyomi-info` is not working when any single or volume formats is used
[#63](https://github.com/mansuf/mangadex-downloader/issues/63)

## v2.9.0

### New features

- Added ability to download covers manga [#60](https://github.com/mansuf/mangadex-downloader/issues/60)

### Fix bugs

- Fix error message is not showing when chapters with specified language is not found
- Fixed `--type` are not respecting full URL

### Dependencies

- Bump [Pillow](https://github.com/python-pillow/Pillow) to v9.5.0
- Bump [py7zr](https://github.com/miurahr/py7zr) to v0.20.4
- Bump [orjson](https://github.com/ijl/orjson) to v3.8.9
- Bump [lxml](https://github.com/lxml/lxml) to v4.9.2

### Deprecated

- Removed `--no-chapter-info` as it's deprecated from v2.6.0

## v2.8.3

- Fixed `--no-track` is not working in version 2.8.x [#56](https://github.com/mansuf/mangadex-downloader/issues/56)

## v2.8.2

### Fix bugs

- `download.db` are no longer exist when `--no-track` is used
- Fixed download tracker are not tracking chapters properly in `raw-single` and `raw-volume` formats
- Fixed duplicated results when using any commands (`random`, `library`, etc) or search with `--input-pos "*"` used

## v2.8.1

- Fixed "database is locked" when `--path` is set to network shared directory
[#52](https://github.com/mansuf/mangadex-downloader/issues/52)
- Fixed "image file is truncated (xx bytes not processed)" error when using any `pdf` formats
[#54](https://github.com/mansuf/mangadex-downloader/issues/54)

## v2.8.0

### New features

- Add ability to disable tracking downloads [#45](https://github.com/mansuf/mangadex-downloader/issues/45)
- Add ability to add custom DoH (DNS over HTTPS) provider
- Added support for legacy URL forums thread ([https://mangadex.org/threads/...](https://mangadex.org/threads/...))

### Fix bugs

- Fixed high CPU usage when downloading large chapters [#48](https://github.com/mansuf/mangadex-downloader/issues/48)
- Fixed download from forum threads are not working if the URL containing page (page-123) with post-id (post-123)

### Improvements

- File hash creation for download tracker are now asynchronous to improve performance
- Added more metadata (tags and authors) to any `epub` formats

### Dependencies

- Bump [requests-doh](https://github.com/mansuf/requests-doh) to v0.3.0

## v2.7.2

### Fix bugs

- Fixed download tracker are not tracking chapters properly [#51](https://github.com/mansuf/mangadex-downloader/issues/51)

## v2.7.1

### Fix bugs

- Fixed `--use-chapter-cover` is throwing error because of missing fonts (PyPI users only).

## v2.7.0

### Improvements

- Reworked creation chapter info (cover) [#44](https://github.com/mansuf/mangadex-downloader/issues/44)

### Dependencies

- [Pillow](https://pypi.org/project/pillow/) is now required dependencies (no longer optional)

## v2.6.2

### Fix bugs

- Fixed app is slowing down after downloading 100+ chapters
- Fixed files are automatically verified if previous download is not complete
- Fixed `--use-volume-cover` is not working if manga doesn't have "No volume" cover [#46](https://github.com/mansuf/mangadex-downloader/issues/46)

## v2.6.1

### Fix bugs

- Fixed resume download is not working properly
- Fixed download forum thread is not working when option `--input-pos "*"` is used
- Fixed `--replace` option is not working when using converted formats (cbz, pdf, epub, epub-volume, etc)

## v2.6.0

### New features

- Added ability to add more groups or users in `--group` option
- Added ability to set retries for failed HTTP requests (`--http-retries`)
- Added OAuth2 login support (`--login-method oauth2`)
- Added ability to download unread chapters (`--download-mode unread`, require authentication) [#39](https://github.com/mansuf/mangadex-downloader/issues/39)
- Added ability to add volume cover for volume formats [#41](https://github.com/mansuf/mangadex-downloader/issues/41)
- Added ability to download MangaDex URLs from forum thread ([https://forums.mangadex.org](https://forums.mangadex.org))

### Fix bugs

- Fixed download is not resuming when network error happened
- Fixed download is overflowing when trying to resume incomplete download
- Fixed various bugs in command-line options parser

### Improvements

- Rework how to download latest chapters on various formats. See commit [`865b7f5`](https://github.com/mansuf/mangadex-downloader/commit/865b7f5988a9cd92e21112ac8649a29299b5023f) for more info

### Dependencies

- Bump orjson to v3.8.3
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) are now required dependencies (no longer optional)

### Breaking changes

- Chapter info (cover) creation are be disabled by default. Use `--use-chapter-cover` to enable it.

### Deprecated

- Removed `--search-filter` and `-sf` option as it's deprecated from v2.4.0
- Format `tachiyomi` and `tachiyomi-zip` are now deprecated, please use `raw` and `cbz` with `--write-tachiyomi-info` instead
- `--no-chapter-info` are now deprecated in favor of `--use-chapter-cover` and will be removed in v2.9.0

## v2.5.4

### Fix bugs

- Fixed typo in filter error message
- Fixed `year` filter is not working
- Fixed validator for environment `MANGADEXDL_TAGS_BLACKLIST` is not respecting rate limit
- Fixed app is crashing due to backward compatibility for config

### Improvements

- Some optimizations

## v2.5.3

### Fix bugs

- Fixed option `--group` is not working due to duplicate chapters.

## v2.5.2

### Fix bugs

- Fixed options `--use-chapter-title` and `--no-group-name` is not working. [#37](https://github.com/mansuf/mangadex-downloader/issues/37)
- Fixed duplicate chapters. [#37](https://github.com/mansuf/mangadex-downloader/issues/37)

## v2.5.1

### Fix bugs

- Fixed chapters are often skipped [#36](https://github.com/mansuf/mangadex-downloader/issues/36)
- Fixed unhandled exception because of `MANGADEXDL_USER_BLACKLIST` filter

## v2.5.0

### Fix bugs

- Fixed input command if user entering a invalid input on first try

### Improvements

- Do not download cover and create folder if manga doesn't contain downloadable chapters (single language only)
- Do not show traceback errors when manga doesn't have downloadable chapters

### New features

- Added ability to block one or more tags

## v2.4.2

### Fix bugs

- Fixed `content_rating` filter is not working in `random` manga

## v2.4.1

### Fix bugs

- Removed unnecessary console output from `random` command

## v2.4.0

### New features

- Added filters on `random` manga

### Improvements

- Added new filters
  - `author_or_artist`

### Fix bugs

- Fixed progress bar are not hidden when `--no-progress-bar` is used

### Dependencies

- Bump Pillow to v9.3.0
- Bump py7zr to v0.20.2

### Breaking changes

- `--search-filter` and `-sf` are no longer working as replaced with `--filter` and `-ft` option. 
The `--search-filter` and `-sf` option will be removed in v2.6.0

## v2.3.0

### New features

- Added ability to disable progress bar

### Improvements

- When executing `login_cache:purge` cached auth tokens will be invalidated (not only purged)
- Update in bundled executable is now verify the file before proceed to install

## v2.2.0

### New features

- Added new environment variables
  - `MANGADEXDL_USER_BLACKLIST`
  - `MANGADEXDL_GROUP_BLACKLIST`
- Added new config
  - `sort_by`
- Added `--sort-by`, Sorting download by `volume` or `chapter`
- Added ability to blacklist users and groups

## v2.1.0

### New features

- Add new environment variables
  - `MANGADEXDL_ZIP_COMPRESSION_TYPE`
  - `MANGADEXDL_ZIP_COMPRESSION_LEVEL`
- Added ability to download seasonal manga

### Fix bugs

- Fixed download file is incomplete when network error happened

## v2.0.4

### Fix bugs

- Fixed the app repeatedly download chapter images after error happened in one of MD@H node

## v2.0.3

### Fix bugs

- Fixed the app failed to download because of:
  - manga has volume with leading zeros numbers (ex: `00`, `01`)
  - manga has volume that is not numbers (ex: `3C63`, `xxx`)
  - manga doesn't have cover

## v2.0.2

### Fix bugs

- Fixed `UnboundLocalError: local variable 'delay' referenced before assignment` when the app get rate limited
- Fixed download in any `single` formats is not working if there is no chapters want to download
- Fixed the app is leaving empty folders if chapters or volume already exists [#35](https://github.com/mansuf/mangadex-downloader/issues/35)

## v2.0.1

### Fix bugs

- Fixed downloader is keep restarting indefinitely if the server has a problem.

### Improvements

- Downloader now has a default timeout (15 seconds) to prevent infinite waiting

## v2.0.0

### New features

- Added ability to auto select prompt (list, library, followed-list command) [#29](https://github.com/mansuf/mangadex-downloader/issues/29)
- Added ability to disable creation of chapter info for any `single` and `volume` formats [#30](https://github.com/mansuf/mangadex-downloader/issues/30)
- Added new config
  - `no_chapter_info`
  - `no_group_name`
- Added new search filters
  - `order[*]` [#32](https://github.com/mansuf/mangadex-downloader/issues/32)
- Added optional dependency [`orjson`](https://pypi.org/project/orjson/) for faster loading and dumping JSON object.
- Added EPUB support (`epub`, `epub-volume`, `epub-single`)

### Improvements

- Search filter `included_tags` and `excluded_tags` are now accepting keyword

### Fix bugs

- Fixed message `Chapter ... from group ... has no images` is not showing properly.
- Fixed batch download error handler is not working
- Fixed download is overflowing when `.temp` file is out of range
- Fixed memory slowly increased during download
- Fixed download with `raw-single` format is not working.
- Fixed error `OSError: broken data stream when reading image file` when downloading in any `pdf` formats.
- Fixed downloder is overflowing when server didn't support `Range` header

### Breaking changes

- Removed `--unsafe` and `-u` option (deprecated from v1.3.0)
- Removed `--no-verify` and `-nv` option
- Removed API references [notes](#notes-api-references-removal)
- Changed extension file for `tachiyomi-zip` format (from `.zip` to `.cbz`)
- [Pillow](https://pypi.org/project/pillow/) is no longer required when downloading in any `single` and `volume` format. 
- All formats will download and convert in separated time (previously was download and convert in same time).
- `--range` option is disabled, because it's broken right now and needs to reworked

### Notes: API references removal <a id="notes-api-references-removal"></a>

All public API is now become private API. Please do not use it for your python script. 
Those can be changed without any notice. 

## v1.7.2

### Fix bugs

- Fixed improper validation for `file:<location>` command
- Fixed error `cannot save mode xxx` when downloading in any `pdf` format

## v1.7.1

### Fix bugs

- Fixed the app won't start [#28](https://github.com/mansuf/mangadex-downloader/issues/28).
- Fixed `-doh` or `--dns-over-https` option are not working.

## v1.7.0

### New features

- Added ability to download manga from scanlator group
- Added new search filter
  - `group`
- Added new config
  - `dns_over_https`

### Improvements

- Added delay to each failed HTTP(s) requests (Delay time formula: `attempt * 0.5`). 
If `--delay-requests` is set, delay time will be used from `--delay-requests` instead.
- Simplified error message [[notes]](#notes-simplified-error-message)

### Dependencies

- Pinned `requests-doh` library version to 0.2.2

### Notes: Simplified error message <a id="notes-simplified-error-message"></a>

Error message has been simplified, no more showing usage on every error thrown.

Before

```shell
$ mangadex-dl "library:ayeeee lmao"
usage: mangadex-dl [-h] [--type {manga,list,chapter,legacy-manga,legacy-chapter}] [--path FOLDER] [--replace]
                   [--verbose] [--unsafe] [--search] [--search-filter SEARCH_FILTER] [--use-alt-details]
                   [--group GROUP_ID] [-lang LANGUAGE] [--list-languages] [--start-chapter CHAPTER]
                   [--end-chapter CHAPTER] [--no-oneshot-chapter] [--no-group-name] [--use-chapter-title]
                   [--range RANGE] [--start-page NUM_PAGE] [--end-page NUM_PAGE] [--use-compressed-image]
                   [--cover {original,512px,256px,none}] [--login] [--login-username USERNAME]
                   [--login-password PASSWORD] [--login-cache]
                   [--save-as {raw,raw-volume,raw-single,tachiyomi,tachiyomi-zip,pdf,pdf-volume,pdf-single,cbz,cbz-volume,cbz-single,cb7,cb7-volume,cb7-single}]
                   [--proxy SOCKS / HTTP Proxy] [--proxy-env] [--force-https] [--delay-requests TIME_IN_SECONDS]
                   [--dns-over-https PROVIDER] [--timeout TIME_IN_SECONDS] [-pipe] [--no-verify] [-v] [--update]
                   URL
mangadex-dl: error: ayeeee lmao are not valid status, choices are {reading, on_hold, plan_to_read, completed, dropped, re_reading}
```

After

```shell
$ mangadex-dl "library:ayeeee lmao"
Error: ayeee lmao are not valid status, choices are {dropped, completed, on_hold, plan_to_read, re_reading, reading}
```

## v1.6.2

### Fix bugs

- Fixed duplicate `ComicInfo.xml` in `cbz` format when app is in verifying files state [#27](https://github.com/mansuf/mangadex-downloader/pull/27).

## v1.6.1

### Improvements

- Added `ComicInfo.xml` for `cbz` format. 
This file is useful for showing details of manga (if an reader support `ComicInfo.xml` file) [#26](https://github.com/mansuf/mangadex-downloader/pull/26).

## v1.6.0

### New features

- Added DNS-over-HTTPS support
- Added ability to set timeout for each HTTP(s) requests

## v1.5.0

### New features

- Added ability to throttle requests [#24](https://github.com/mansuf/mangadex-downloader/issues/24)

### Fix bugs

- Fixed error `Too many open files` in Unix-based systems when downloading manga in any `pdf` format
- Fixed false owner list name when executing command `list:<user-id>`
- Fixed unproperly parsed `list` command

### Improvements

- Do not re-download cover manga when it already exist [#23](https://github.com/mansuf/mangadex-downloader/issues/23)

### Dependencies

- Bump py7zr to v0.20.0

## v1.4.0

### New features

- Added ability to choose and download random manga

### Fix bugs

- Fixed report system is not working if HTTP response is server error
- Fixed fail to parse authors and artists when fetching manga

## v1.3.0

### New features

- Added web URL location (`http`, `https`) support for batch download syntax
- Added new languages
  - Azerbaijani
  - Slovak
- Added search filters
- Added `--force-https` and `-fh` option, forcing you to download images in standard HTTPS port 443
- Added new configs
  - `force_https`
  - `path`
- Added ability to preview cover manga when searching manga

### Improvements

- Reduced time to preview list

### Fix bugs

- Fixed error `NameError: name 'exit' is not defined` in bundled executable 
when executing command `login_cache` or `login_cache:show`
- Fixed mangadex-downloader won't start in Python 3.8
- Fixed config is not parsed properly

### Breaking changes

- Removed unsafe feature, `--unsafe` or `-u` option is still exist but it's doing nothing and will be removed in v2.0.0. See [b32dac4](https://github.com/mansuf/mangadex-downloader/commit/b32dac4739369a9a6e94650dab8ff9fe5c7bd143)
- Removed `--enable-legacy-sorting` option as it's deprecated since v1.1.0

### Notes: Unsafe feature removal

You may be wondering, why remove a feature that got added 2 months before ?
<br>
Okay that was my mistake, 
because i was really naive to implement some restriction that makes user have a complicated process when downloading manga from MangaDex. 
See [d3470ce](https://github.com/mansuf/mangadex-downloader/commit/d3470ce47e7475f604cdd8b30a12f249a2bbcb38), 
but here's the thing, it's a downloader tool and it has nothing to do with content restrictions in a downloader tool.

## v1.2.1

### Fix bugs

- Fixed fail to get manga, lists, followed lists from user library (The error only happened if user is logged in from cache).

## v1.2.0

### New features

- Added ability to download manga in all languages
- Added cache authentication
- Added config
- Added new languages
    - Kazakh
    - Tamil
- Added support for `Other` language
- Added `--range` (or `-rg`) option, allow you to download specific chapters and pages.

### Fix bugs

- Fixed conflict `URL` argument with pipe input
- Fixed update is failing if user is logged in
- Fixed batch download throwing an error if location is pointed at folder

### Improvements

- Simplified chapter and volume name. For example: From `Volume. n Chapter. n` to `Vol. n Ch. n`
- Reduced requests fetching all chapters
- When batch downloading urls and error encountered. Do not stop immediately, instead ignore broken url
- Now you can search manga with empty keyword (`mangadex-dl -s`)
- Reduced startup time mangadex-downloader
- [`mangadex_downloader.format.utils.delete_file()`] Do not remove files when it doesn't exist

### Breaking changes

- MangaDex legacy urls are now deprecated
- [beautifoulsoup4](https://pypi.org/project/beautifulsoup4/) dependency was removed, because all of app works is depend on MangaDex API not MangaDex frontend website
- Erotica manga now cannot be downloaded without unsafe enabled

## v1.1.0

### New features

- Added aliases command line args
- Added `--version`, `-v` to print version
- Added ability to download list from user library
- Added ability to filter scanlation groups with user
- Added ability to download user followed list
- Added batch download with syntax `file:<path_to_file>` to prevent conflict with reserved names in `URL` argument

### Fix bugs

- Fix missing fonts in Linux for any `volume` and `single` formats. If error occurred during creating chapter info or the text is really small. Please install Arial font or FreeSans font (from GNU FreeFont) [#20](https://github.com/mansuf/mangadex-downloader/pull/20) @bachhh 

### Improvements

- Whenever the app in resuming download state, it will verify all downloaded images. Causing the app to perform faster when resuming download. **NOTE:** in v1.0.2 and lower, the app will open connection to MangaDex CDN to check if image from MangaDex CDN is same size as the downloaded one, which cause slow performance.
- Reduced fetching time before downloading a MangaDex list
- The app will not stop when server error happened. Instead, retry for 5 times. If still failed, the app will exit.

### Breaking changes

- `--enable-legacy-sorting` is now deprecated and does nothing. All images will be named with numbers leading zeros (ex: `001.jpg`)
- `pdf` format now will download the chapter first and then convert it.

## v1.0.2

### Fix bugs

- Fixed `--replace` is not working properly in `cbz` format 
- Fixed `--enable-legacy-sorting` is not working properly in `cbz` format 
- Fixed duplicate oneshot 

### New features

- From now on, you can download mangas from user library (require authentication)
- Added new formats
	- cb7 [#17](https://github.com/mansuf/mangadex-downloader/issues/17)
	- cb7-volume [#17](https://github.com/mansuf/mangadex-downloader/issues/17)
	- cb7-single [#17](https://github.com/mansuf/mangadex-downloader/issues/17)

## v1.0.1

### Fix bugs

- Fix page is starting from 2 when format cbz and pdf single is used
- Fix Random NoneType error while downloading [#19](https://github.com/mansuf/mangadex-downloader/pull/19)

## v1.0.0

### New features

- Legacy MangaDex url is now downloadable
- Added localization title and description for manga, with this you can choose different titles in different languages !
- Added pipe input
- Added ability to download all same chapters with different scanlation groups [#9](https://github.com/mansuf/mangadex-downloader/issues/9)
- Added ability to add chapter title to each chapters filename
- Added shortcut option for `--language`
- Added new formats
    - raw
    - raw-volume [#13](https://github.com/mansuf/mangadex-downloader/issues/13)
    - raw-single
    - pdf-volume [#13](https://github.com/mansuf/mangadex-downloader/issues/13)
    - cbz-volume [#13](https://github.com/mansuf/mangadex-downloader/issues/13)
- Added search feature
- Added ability to login with email
- Added old technique sorting images [#10](https://github.com/mansuf/mangadex-downloader/issues/10)
- Now, each chapter filename has scanlation group name on it

### Fix bugs

- Fixed image is not finished downloading but marked as "finished" [#14](https://github.com/mansuf/mangadex-downloader/issues/14)
- Fixed duplicate scanlation groups [#11](https://github.com/mansuf/mangadex-downloader/issues/11)
- For Mac OS users, error like "OSError: cannot open resource" is should not be happened again. If you are getting this error again, please install Arial font (`arial.ttf`) in your OS. If still getting error, please report it to [issue tracker](https://github.com/mansuf/mangadex-downloader/issues)

### Improvements

- Reduced requests to MangaDex server (to reduce hit limits and provide faster downloading)
- Much better error handling

### Breaking changes

- mangadex-downloader now restrict downloading porn content by default, you can bypass it using `--unsafe` option. See [d3470ce](https://github.com/mansuf/mangadex-downloader/commit/d3470ce47e7475f604cdd8b30a12f249a2bbcb38) why i'm doing this. (**NOTE:** to clarify, you still can search porn manga in MangaDex by login and enable it in settings)
- [aiohttp](https://github.com/aio-libs/aiohttp) dependency was removed, because i don't have a plan to make mangadex-downloader asynchronous, also to reduce time to load the app.
- Changed default format from `tachiyomi` to `raw` format, see [6aa1c98](https://github.com/mansuf/mangadex-downloader/commit/6aa1c9801e5f7358d9a1ff2ac9eea88c0661bc08) why i'm doing this.

## v0.6.1

- Downloading manga with format `pdf-single` or `cbz-single` throwing error `The _imagingft C module is not installed` after updating to v0.6.x in bundled executable
- Download a list with different language is not working

## v0.6.0

- Added `pdf-single` save as format
- Added `cbz` (Comic Book Archive) save as format
- Added `cbz-single` save as format
- Now, you can download a list (`https://mangadex.org/list/...`) or a chapter (`https://mangadex.org/chapter/...`)
- Added `--type` option to override type MangaDex url
- Added `--start-page` option, start download chapter page from given page number
- Added `--end-page` option, stop download chapter page from give page number

## v0.5.2

- Fixed `--update` option is not working
- Fixed unhandled exception if `--start-chapter` is more than `--end-chapter`
- Optimized app
- Better error handling

## v0.5.1

- Fixed critical `ModuleNotFoundError` for those who installed from PyPI

## v0.5.0

```{note}
PyPI version is broken, the bug is already fixed in v0.5.1
```

- Fixed oneshot chapter is unproperly parsed 
- Fix chapters are sometimes in string not in numbers [#7](https://github.com/mansuf/mangadex-downloader/issues/7)
- Fix `ConnectionError` 
- Added `none` type in `--cover` option, if the value is `none` it will not download cover manga. 
- Added save as format, available in 3 formats: `{tachiyomi, tachiyomi-zip, pdf}`. Default to `tachiyomi` 
- Added PDF support 
- Added Tachiyomi zipped support
- From now mangadex-downloader will no longer support Python 3.5, 3.6 and 3.7

## v0.4.2

- Fixed sometimes manga are failed to get volumes 
- Fixed additional info manga are not appeared in Tachiyomi local 
- Fixed incomplete artists and authors in manga 
- Fixed app still running when `--start-chapter` are more than `--end-chapter` 
- Fixed app throwing error if one of chapters has no images 
- Added auth handler. If login and logout is failed it will try again 5 times, if still failed it will exit (login) or ignored (logout) 
- Added `--cover` option, select quality cover to download
- Changed license from The Unlicense to MIT License. From now the app will be released under MIT License.

## v0.4.1

- Fixed error if selected manga with different translated language has no chapters.
- Fixed sometimes manga are failed to get chapters. 
- From now the app will fetch the chapters first before download the covers, writing details, etc. 

## v0.4.0

- Added multi urls in a file support
- Added multi languages support
- Added update feature, **NOTE:** This feature highly experimental for compiled app
- Fix bug [#6](https://github.com/mansuf/mangadex-downloader/issues/6)

## v0.3.0

- A lot of bug fixes
- Added authentication support
- Reworked how download chapter images work
- Added `CTRL + C` handler
- Added [documentation](https://mangadex-downloader.readthedocs.io/en/latest/index.html)
- Added `--replace` option

For more detail about updates, see below.

- Fixed `--start-chapter` and `--end-chapter` malfunctioning #5 , thanks to @kegilbert !
- Added `--replace` option, replace manga if exist.
- Added KeyboardInterrupt (Ctrl+C) handler, so there are no messy outputs when `CTRL + C` is pressed. See example below.

Before

```shell
$ mangadex-dl "a96676e5-8ae2-425e-b549-7f15dd34a6d8"
[INFO] Fetching manga a96676e5-8ae2-425e-b549-7f15dd34a6d8
[INFO] Downloading cover manga Komi-san wa Komyushou Desu.
file_sizes:  55%|██████████████▏           | 1.51M/2.76M [00:00<00:00, 5.84MB/s]^CTraceback (most recent call last):
  File ".../.local/bin/mangadex-dl", line 8, in <module>
    sys.exit(main())
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/__main__.py", line 59, in main
    _main(sys.argv[1:])
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/__main__.py", line 45, in _main
    download(
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/main.py", line 84, in download
    download_file(manga.cover_art, str(cover_path))
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/utils.py", line 27, in download
    downloader.download()
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/downloader.py", line 117, in download
    writer.write(chunk)
KeyboardInterrupt
```

After

```shell
$ mangadex-dl "a96676e5-8ae2-425e-b549-7f15dd34a6d8"
[INFO] Fetching manga a96676e5-8ae2-425e-b549-7f15dd34a6d8
[INFO] Downloading cover manga Komi-san wa Komyushou Desu.
file_sizes:  50%|████████████▉             | 1.38M/2.76M [00:00<00:00, 3.11MB/s]
[INFO] Cleaning up...
Action interrupted by user
```
- Added type checking for MangaDex url, so no more messy outputs. See example below

Before

```shell
$ mangadex-dl "invalid manga"
[ERROR] invalid manga is not valid mangadex url
Traceback (most recent call last):
  File ".../.local/bin/mangadex-dl", line 8, in <module>
    sys.exit(main())
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/__main__.py", line 59, in main
    _main(sys.argv[1:])
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/__main__.py", line 45, in _main
    download(
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/main.py", line 37, in download
    raise e from None
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/main.py", line 34, in download
    manga_id = validate_url(url)
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/utils.py", line 15, in validate_url
    raise InvalidURL('Invalid MangaDex URL or manga id')
mangadex_downloader.errors.InvalidURL: Invalid MangaDex URL or manga id
```

After

```shell
$ mangadex-dl "invalid manga"
usage: mangadex-dl [-h] [--folder FOLDER] [--replace] [--proxy SOCKS / HTTP Proxy] [--proxy-env] [--verbose]
                   [--start-chapter CHAPTER] [--end-chapter CHAPTER] [--use-compressed-image] [--no-oneshot-chapter]
                   [--login] [--login-username USERNAME] [--login-password PASSWORD]
                   URL
__main__.py: error: argument URL: Invalid MangaDex URL or manga id
```

- Fixed report time for MangaDex network are high numbers
- Fixed massive reports to MangaDex network if response `status_code` was `206`
- HTTP server errors are now handled by the session
- Now `download()` will raise `InvalidManga` if given manga are not exist, see example below.

Before
```shell
$ mangadex-dl "2bdf5af0-54ab-41e2-978b-58e74bdb9d15"
[INFO] Fetching manga 2bdf5af0-54ab-41e2-978b-58e74bdb9d15
Traceback (most recent call last):
  File ".../.local/lib/python3.8/site-packages/mangadex_downloader/fetcher.py", line 11, in get_manga
    raise HTTPException('Server sending %s code' % r.status_code) from None
mangadex_downloader.errors.HTTPException: Server sending 404 code
```

After
```shell 
$ mangadex-dl "2bdf5af0-54ab-41e2-978b-58e74bdb9d15"
[INFO] Fetching manga 2bdf5af0-54ab-41e2-978b-58e74bdb9d15
Traceback (most recent call last):
  File "...\mangadex-downloader\mangadex_downloader\fetcher.py", line 9, in get_manga
    raise InvalidManga('Manga \"%s\" cannot be found' % manga_id)
mangadex_downloader.errors.InvalidManga: Manga "2bdf5af0-54ab-41e2-978b-58e74bdb9d15" cannot be found
```
- Added `login()` for logging in to MangaDex API, for more info: https://mangadex-downloader.readthedocs.io/en/latest/api.html#mangadex_downloader.login.
- Added `logout()` for logging out from MangaDex API, for more info: https://mangadex-downloader.readthedocs.io/en/latest/api.html#mangadex_downloader.logout


## v0.2.0

- Some optimization
- Downloading chapters are now starting from zero (the previous one was from highest chapter)
- Added `--no-oneshot-chapter`. If oneshot chapter exist, don't download it.
- Added `--use-compressed-image`. Use low size images manga
- Added `--start-chapter`. Start download chapter from given chapter number.
- Added `--end-chapter`. Stop download chapter from given chapter number.
- Added `compressed_image` parameter in `download()` function
- Added `start_chapter` parameter in `download()` function
- Added `end_chapter` parameter in `download()` function
- Added `no_oneshot_chapter` in `download()` function

## v0.1.1

This update fixes critical error from v0.1.0

## v0.1.0

- Reworked app for MangaDex API v5
- Added CLI
- Added proxy support (http or socks)
- From now, the app will always download in tachiyomi local format.

Other features are coming soon.

````{note}
A lot of errors during running `mangadex-downloader` v0.1.0.
The errors (included with solution) can be see below:  

Case 1

**Error:**
The app throwing error like this:
```shell
Traceback (most recent call last):
  File "...../mangadex-downloader", line 5, in <module>
    from mangadex_downloader.__main__ import main
  File "...../python3.8/site-packages/mangadex_downloader/__init__.py", line 13, in <module>
    from .main import *
  File "..../python3.8/site-packages/mangadex_downloader/main.py", line 2, in <module>
    from pathvalidate import sanitize_filename
ModuleNotFoundError: No module named 'pathvalidate'
```

**Solution:**
Install `pathvalidate`
```shell
# For Windows
py -3 -m pip install pathvalidate

# For Linux / Mac OS
python3 -m pip install pathvalidate
```

Case 2

**Error:**
CLI `mangadex-dl` or `mangadex-downloader` didn't work.
```shell
$ mangadex-dl
Traceback (most recent call last):
  File "...", line 8, in <module>
    sys.exit(main())
TypeError: main() missing 1 required positional argument: 'argv'
```

**Solution:**
Run mangadex-downloader module from python app with `-m` option
```shell
# For Windows
py -3 -m mangadex_downloader

# For Linux / Mac OS
python3 -m mangadex_downloader
```
````

## v0.0.5

- Bug fix: Changed API Mangadex URL from `https://mangadex.org/api/v2` to `https://api.mangadex.org/v2`
- New feature: Added `latest_chapters` attribute in `MangaData` class, to see the latest chapters in manga

## v0.0.4

- New feature: added `Mangadex.extract_basic_info()` to grab all information in manga without the chapters.
- New feature: added `data_saver` argument in `Mangadex.extract_info()` and `Mangadex.download()` to use low quality and size image.
- Enchantment: now mangadex-downloader will always using API for fetching information and chapters for manga, **NOTE:** for grabbing manga id still need scrapping from main website.
- Enchantment: Improved verbose logger.
- Bug fix: fixed failed to create folder when downloading manga in windows OS.
- `language` argument in `Mangadex` class, `MangadexFetcher` class, and `mangadex_downloader.parser.parse_infos()` (this function is removed too) is removed, until i explore all languages code in mangadex, right now mangadex-downloader will fetch and download in English language by default.

## v0.0.3

- Bug fix: given url doesn't have title in url causing empty and useless loop request
- Bug fix: `MangaData.__repr__()` raise error for `oneshot` genre manga
- New Feature: Add `output_folder` in Mangadex class arguments for choose the path in which store the downloaded mangas [#1](https://github.com/mansuf/mangadex-downloader/pull/1)
- Enchantment: add functional `Mangadex.download()`

## v0.0.2

- fixed failed to getting info when manga dont have more than 100 chapters

## v0.0.1

[NOT STABLE, USABLE]
