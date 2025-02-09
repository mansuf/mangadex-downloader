# Command-line Interface (CLI) options

## Global options

```{option} URL
MangaDex URL or a file containing MangaDex URLs. 
This parameter also can be used for commands, to see all available commands see {doc}`./commands`
```

```{option} --type -t manga|cover|list|chapter|legacy-manga|legacy-chapter
Override type MangaDex url. By default, it auto detect given url
```

```{option} --replace -r
Replace manga if exist
```

```{option} --filter -ft FILTERS
Apply filter to search and random manga. For more information, you can see {doc}`./filters`
```

```{option} --download-mode -dm default|unread
Set download mode, you can set to `default` or `unread`. 
If you set to `unread`, the app will download unread chapters only (require authentication). 
If you set to `default` the app will download all chapters
```

## Path / Directory

```{option} --path --folder -d DIRECTORY
Store manga / chapter to specified directory. This option support placeholders, read {doc}`./path_placeholders` for more info
```

```{option} --filename-single -fs FILENAME_WITH_PLACEHOLDERS
Set filename for single format, read {doc}`./path_placeholders` for more info
```

```{option} --filename-volume -fv FILENAME_WITH_PLACEHOLDERS
Set filename for volume format, read {doc}`./path_placeholders` for more info
```

```{option} --filename-chapter -fc FILENAME_WITH_PLACEHOLDERS
Set filename for chapter format, read {doc}`./path_placeholders` for more info
```

## Search related

```{option} --search -s
Search manga and then download it
```

## Manga related

```{option} --use-alt-details -uad
Use alternative title and description manga
```

```{option} --create-manga-info -cmi
Store manga information such as title, authors, artists, description, and tags in a file called `manga_info.csv`. 
By default this file will save to csv format you can change this in --manga-info-format
```

```{option} --manga-info-format -mif csv|json
Change file format for manga information file (manga_info.csv). Available options: csv, json
```

```{option} --manga-info-filepath -mip PATH
Change file location to store manga information. Default to `./manga_info.{manga_info_format}`. 
Available placeholders: {download_path} and {manga_info_format}, placeholder {download_path} is value from --path option 
and placeholder {manga_info_format} is from --manga-info-format option
```

```{option} --manga-info-only -mio
Store manga information without downloading manga. The application will exit after writing manga information
```

## Group related

```{option} --group -g GROUP_ID
Filter each chapter with different scanlation group. 
Filter with user also supported. 
You can also put `all` value, this will make download all chapters from all groups available in the manga
```

```{option} --group-nomatch-behaviour -gnb ignore|fallback
Change behaviour for group filtering if it doesn't match. 
By default, it set to `ignore`. Which mean it will ignore the chapter if the chapter doesn't match with specified group. 
If you set it to `fallback` the app will find another chapter if the chapter doesn't match with specified group
```

## Language

```{option} --language -lang LANGUAGE
Download manga in given language, to see all languages, use `--list-languages` option
```

```{option} --list-languages -ll
List all available languages
```

## Volume manga

```{option} --volume-cover-language -vcl LANGUAGE
Override volume cover language. If this option is not set, it will follow `--language` option
```

```{option} --start-volume -sv VOLUME
Start download chapter from given volume number
```

```{option} --end-volume -ev VOLUME
Stop download chapter from given volume number
```

## Chapter manga

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

````{option} --use-chapter-title -uct
Use chapter title for each chapters.

```{note} 
This option is useless if used with any single and volume format 
```
````

```{option} --range -rg
A range pattern to download specific chapters
```

```{option} --sort-by chapter|volume
Download sorting method, by default it's selected to `volume`
```

````{option} --use-chapter-cover -ucc
Enable creation of chapter info (cover) for any single or volume formats. See {doc}`./chapter_info` for more info.

```{note}
Chapter info creation are not enabled if you are using any chapter format (cbz, pdf, raw, etc) 
```
````

````{option} --use-volume-cover -uvc
Enable creation of volume cover for any volume formats. Volume cover will be placed in first page in each volume files.

```{note} 
Volume cover will be not created in chapter (cbz, pdf, raw, etc) and single formats 
```
````

```{option} --ignore-missing-chapters -imc
Ignore missing downloaded chapters. This will prevent the application to re-download the missing chapters.
```

```{option} --create-no-volume -cnv
Merge all chapters that has no volume into 1 file for `volume` format
```

```{option} --order newest|oldest
Change chapter order, by default it set to `newest`. 
Which mean it always try to download the newest chapter. Available options: newest, oldest
```

## Chapter page manga

```{option} --start-page -sp NUM_PAGE
Start download chapter page from given page number
```

```{option} --end-page -ep NUM_PAGE
Stop download chapter page from given page number
```

## Images

```{option} --use-compressed-image -uci
Use low size images manga (compressed quality)
```

```{option} --cover -c original|512px|256px|none
Choose quality cover, default is `original`
```

## Authentication

```{option} --login -l
Login to MangaDex
```

```{option} --login-method -lm legacy|oauth2
Set authentication method for MangaDex, by default it set to `legacy`. 
Which is directly input (username or email) and password to the application
```

````{option} --login-username -lu USERNAME
Login to MangaDex with username or email (you will be prompted to input password if --login-password are not present)

```{note} 
You must provide `--login` or `-l` option to login. If you don't, you will not logged in to MangaDex 
```
````

````{option} --login-password -lp PASSWORD
Login to MangaDex with password (you will be prompted to input username if --login-username are not present)

```{note} 
You must provide `--login` or `-l` option to login. If you don't, you will not logged in to MangaDex 
```
````

```{option} --login-api-id -lai API_CLIENT_ID
Login to MangaDex with API Client. 
This option is working if you use `oauth2` login method (--login-method oauth2). 
Also you will be prompted to input API client secret if --login-api-secret are not present
```

```{option} --login-api-secret -las API_CLIENT_SECRET
Login to MangaDex with API Client. 
This option is working if you use `oauth2` login method (--login-method oauth2). 
Also you will be prompted to input API client id if --login-api-id are not present
```

````{option} --login-cache -lc
Cache authentication token. You don't have to re-login with this option. 
You must set `MANGADEXDL_CONFIG_ENABLED=1` in your environment variables before doing this, 
otherwise the app will throwing error.

```{warning} 
Using this option can cause an attacker in your computer may grab your authentication cache and using it for malicious actions. 
USE IT WITH CAUTION !!! 
```
````

## Format (Save as)

```{option} --save-as -f raw|raw-volume|raw-single|tachiyomi|tachiyomi-zip|pdf|pdf-volume|pdf-single|cbz|cbz-volume|cbz-single|cb7|cb7-volume|cb7-single
Choose save as format, default to `raw`. For more information about formats, see {doc}`../formats`
```

## Network

```{option} --proxy -p SOCKS / HTTP Proxy
Set http/socks proxy
```

```{option} --proxy-env -pe
Use http/socks proxy from environments
```

```{option} --force-https -fh
Force download images in standard HTTPS port 443
```

```{option} --delay-requests -dr TIME_IN_SECONDS
Set delay for each requests send to MangaDex server
```

```{option} --dns-over-https -doh PROVIDER
Enable DNS-over-HTTPS (DoH), must be one of `cloudflare` or `google`
```

```{option} --timeout TIME_IN_SECONDS
Set timeout for each HTTPS(s) requests
```

```{option} --http-retries NUMBERS_OR_UNLIMITED
Set HTTP retries, use this if you want to set how much to retries if the app failed to send HTTP requests to MangaDex API. Value must be numbers or "unlimited", by default it set to 5
```

## Miscellaneous

````{option} --input-pos
Automatically select choices in selectable prompt (list, library, followed-list command). 
You also can put asterisk (*) in this option to select all choices

```{note}
This option does not apply to `--use-alt-details` 
```
````

```{option} -pipe
If set, the app will accept pipe input
```

```{option} -v --version
Print mangadex-downloader version
```

````{option} --no-track
Disable download tracking

```{note}
If you enable this, the application will not verify images and chapters. Also file `download.db` will not created. 
```
````

```{option} --no-metadata
Disable metadata creation (ComicInfo.xml) in any cbz format (cbz, cbz-volume, cbz-single)
```

```{option} --page-size NUMBERS
Set maximum items displayed in page for commands and search mode. 
For example: `mangadex-dl library --login --page-size 50`, 
this example command will display 50 items per page. 
If you set to 0, the application will follow default limit size depends on what type of command
```

## Console output

```{option} --log-level LEVEL
Set logger level, available options: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET. Default level is INFO
```

```{option} --progress-bar-layout -pbl LAYOUT
Set progress bar layout, available options: default, stacked, none. Default layout is `default`. Set layout `none` to disable progress bar.
```

```{option} --stacked-progress-bar-order -spb-order ORDER
Set stacked progress bar order, available options: volumes, chapters, pages, file sizes, convert. 
Multiple values is supported, separated by comma. Default order is `volumes, chapters, pages, file sizes, convert`
```

## Update application

```{option} --run-forever
Allow the application to run indefinitely with 5 seconds delay for repeating the same job
```

```{option} --update
Update mangadex-downloader to latest version
```
