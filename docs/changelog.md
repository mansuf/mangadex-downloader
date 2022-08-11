# Changelog

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
- Fixed uncomplete artists and authors in manga 
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