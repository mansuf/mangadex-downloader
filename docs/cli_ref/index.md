# Reference

## App names

There is few app names in mangadex-downloader:

- `mangadex-dl`
- `mangadex-downloader`

````{note}
If none of above doesnt work use this

```shell
# For Windows
py -3 -m mangadex_downloader

# For Linux
python3 -m mangadex_downloader
```
````

```{note}
For bundled executable will remain `mangadex-dl`
```

## Options

### Global options

```{option} URL
MangaDex URL or a file containing MangaDex URLs. 
Type `library:<status>` to download manga from logged in user library,
if `<status>` is provided, it will fetch all mangas with given reading status,
if not, then it will fetch all mangas from logged in user.
Type `list:<user_id>` to download MangaDex list user, 
if `<user_id>` is provided it will download public list,
if not, then it will download from public and private list from logged in user.
Type `followed-list` to download followed MangaDex list from logged in user
```

```{option} --type -t manga|list|chapter|legacy-manga|legacy-chapter
Override type MangaDex url. By default, it auto detect given url
```

```{option} --folder --path -d FOLDER
Store manga in given folder / directory
```

```{option} --replace -r 
Replace manga, chapter, or list (if exist)
```

```{option} --filter -ft
Apply filter to search and random manga

For more information, see {doc}`./filters`
```

```{option} --download-mode -dm
Set download mode, you can set to `default` or `unread`. 
If you set to `unread`, the app will download unread chapters only 
(require authentication). If you set to `default` the app will download all chapters
```

```{option} --verbose
Enable verbose output
```

### Search related

```{option} --search -s
Search a manga and then download it
```

### Manga related

```{option} --use-alt-details -uad
Use alternative title and description manga
```

### Group related

```{option} --group -g GROUP_ID
Filter each chapter with different scanlation group. Filter with user also supported.
```

### Language related

```{option} --language -lang LANGUAGE
Download manga in given language, to see all languages, use `--list-languages` option
```

```{option} --list-language -ll 
List all available languages
```

### Chapter related

```{option} --start-chapter -sc CHAPTER
Start download chapter from given chapter number
```

```{option} --end-chapter -ec CHAPTER
Stop download chapter from given chapter number
```

```{option} --no-oneshot-chapter -noc
If manga has oneshot chapter, it will be ignored
```

```{option} --no-group-name -ngn
Do not use scanlation group name for each chapter
```

```{option} --use-chapter-title -uct
Use chapter title for each chapters. **NOTE:** This option is useless if used with any single and volume format
```

````{option} --no-chapter-info -nci

```{warning}
Deprecated, chapter info creation are disabled by default. 
Use `--use-chapter-info` to enable chapter info creation
```

Do nothing. 
Previously, it was used to disable creation of chapter info for any `single` and `volume` formats
````

````{option} --use-chapter-cover -ucc
```{note}
Chapter info creation are not enabled if you are using any chapter format (cbz, pdf, raw, etc)
```

Enable creation of chapter info (cover) for any single or volume formats. 
See {doc}`./chapter_info` for more info. 
````

````{option} --use-volume-cover -uvc
```{note}
Volume cover will be not created in chapter (cbz, pdf, raw, etc) and single formats)
```

Enable creation of volume cover for any volume formats. 
Volume cover will be placed in first page in each volume files. 
````

```{option} --sort-by
Download sorting method, by default it's selected to `volume`
```

### Chapter page related

```{option} --start-page -sp NUM_PAGE
Start download chapter page from given page number
```

```{option} --end-page -ep NUM_PAGE
Stop download chapter page from given page number
```

### Chapter and page range

````{option} --range -rg
```{warning}
This option can only be used for downloading manga. Downloading a list or chapter while using this option will throw an error.
```

A range pattern to download specific chapters
````

### Images related

```{option} --use-compressed-image -uci
Use low size images manga (compressed quality)
```

```{option} --cover -c original|512px|256px|none
Choose quality cover, default is `original`
```

### Authentication related

```{option} --login -l
Login to MangaDex
```

```{option} --login-method -lm legacy|oauth2
Set authentication method for MangaDex, by default it set to `legacy`. 
Which is directly input (username or email) and password to the application.
```

````{option} --login-username -lu USERNAME
```{note}
You must provide `--login` or `-l` option to login. If you don't, you will not logged in to MangaDex
```
Login to MangaDex with username or email (you will be prompted to input password if --login-password are not present). 
````

````{option} --login-password -lp PASSWORD
```{note}
You must provide `--login` or `-l` option to login. If you don't, you will not logged in to MangaDex
```
Login to MangaDex with password (you will be prompted to input username if --login-username are not present). 
````

````{option} --login-cache -lc
```{note}
Using this option can cause an attacker in your computer may grab 
your authentication cache and using it for malicious actions. USE IT WITH CAUTION !!!
```

Cache authentication token. You don't have to re-login with this option. 
You must set `MANGADEXDL_CONFIG_ENABLED=1` in your environment variables before doing this, 
otherwise the app will throwing error.
````

### Save as format

```{option} --save-as -f raw|raw-volume|raw-single|tachiyomi|tachiyomi-zip|pdf|pdf-volume|pdf-single|cbz|cbz-volume|cbz-single|cb7|cb7-volume|cb7-single
Choose save as format, default to `raw`
```

### Network related

```{option} --proxy -p SOCKS / HTTP Proxy
Set http/socks proxy
```

```{option} --proxy-env -pe
use http/socks proxy from environments
```

```{option} --force-https -fh
Force download images in standard HTTPS port 443
```

```{option} --delay-requests -dr DELAY_TIME
Set delay for each requests send to MangaDex server
```

```{option} --dns-over-https -doh PROVIDER
Enable DNS-over-HTTPS (DoH), must be one of `cloudflare` or `google`
```

```{option} --timeout TIME_IN_SECONDS
Set timeout for each HTTPS(s) requests
```

```{option} --http-retries NUMBERS_OR_UNLIMITED
Set HTTP retries, use this if you want to set how much to retries 
if the app failed to send HTTP requests to MangaDex API. 
Value must be numbers or "unlimited", by default it set to 5
```

### Miscellaneous

```{option} --input-pos
Automatically select choices in selectable prompt (list, library, followed-list command)
```

```{option} -pipe
If set, the app will accept pipe input
```

```{option} -v --version
Print mangadex-downloader version
```

```{option} -npb --no-progress-bar
Disable progress bar when downloading or converting
```

````{option} --no-track
```{note}
If you enable this, the application will not verify images and chapters. 
Also file `download.db` will not created.
```

Disable download tracking
````

### Update application

```{option} --update
Update mangadex-downloader to latest version
```

## Available commands

### Example usage

```
mangadex-dl "random"
```

### List of commands

```{option} random
Show 5 of random manga and select to download

For more info, see {doc}`./random`
```

```{option} library
Show list of saved manga from logged in user

For more info, see {doc}`./manga_library`
```

```{option} list
Show list of saved MDLists from logged in user

For more info, see {doc}`./list_library`
```

```{option} followed-list
Show list of followed MDLists from logged in user

For more info, see {doc}`./follow_list_library`
```

```{option} group
Show list of manga from a group that have uploaded scanlated chapters
```

```{option} file
Download list of manga, chapters or lists from a file

For more info, see {doc}`./file_command`
```

```{option} seasonal
Select and download seasonal manga

For more info, see {doc}`./seasonal_manga`
```

```{option} conf
Modify or show config

For more info, see {doc}`./config`
```

```{option} login_cache
Modify or show cached authentication tokens expiration time

For more info, see {doc}`./auth_cache`
```

## Reference

```{toctree}
:maxdepth: 2

cover
file_command
forums
download_tracker
chapter_info
filters
random
manga_library
list_library
follow_list_library
seasonal_manga
config
auth_cache
env_vars
```