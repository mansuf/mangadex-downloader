# Command-line Interface (CLI) options

## Global options

```{option} URL
MangaDex URL or a file containing MangaDex URLs. 
This parameter also can be used for commands, 
to see all available commands see {doc}`./commands`
```

```{option} --type -t manga|cover|list|chapter|legacy-manga|legacy-chapter
Override type MangaDex url. By default, it auto detect given url
```

```{option} --folder --path -d DIRECTORY
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

## Search related

```{option} --search -s
Search a manga and then download it
```

## Manga related

```{option} --use-alt-details -uad
Use alternative title and description manga
```

## Group related

```{option} --group -g GROUP_ID
Filter each chapter with different scanlation group. 
Filter with user also supported.
```

## Language related

```{option} --language -lang LANGUAGE
Download manga in given language, 
to see all languages, use `--list-languages` option
```

```{option} --list-language -ll 
List all available languages
```

```{option} --volume-cover-language -vcl LANGUAGE
Override volume cover language. 
If this option is not set, it will follow `--language` option
```

## Chapter related

```{option} --start-chapter -sc CHAPTER
Start download chapter from given chapter number
```

```{option} --end-chapter -ec CHAPTER
Stop download chapter from given chapter number
```

```{option} --no-oneshot-chapter -noc
Ignore oneshot chapter (if manga has oneshot chapter)
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

````{option} --use-chapter-cover -ucc
```{note}
Chapter info creation are not enabled if you are using any chapter formats (cbz, pdf, raw, etc)
```

Enable creation of chapter info (cover) for any single or volume formats. 
See {doc}`./chapter_info` for more info. 
````

````{option} --use-volume-cover -uvc
```{note}
Volume cover will be not created in chapter (cbz, pdf, raw, etc) and single formats
```

Enable creation of volume cover for any volume formats. 
Volume cover will be placed in first page in each volume files. 
````

```{option} --sort-by
Download sorting method, by default it's selected to `volume`
```

## Chapter page related

```{option} --start-page -sp PAGE
Start download chapter page from given page number
```

```{option} --end-page -ep PAGE
Stop download chapter page from given page number
```

## Chapter and page range

````{option} --range -rg
```{warning}
This option can only be used for downloading manga. 
Downloading a list or chapter while using this option will throw an error.
```

A range pattern to download specific chapters
````

## Images related

```{option} --use-compressed-image -uci
Use low size images manga (compressed quality)
```

```{option} --cover -c original|512px|256px|none
Choose quality cover, default is `original`
```

## Authentication related

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

## Save as format

```{option} --save-as -f raw|raw-volume|raw-single|tachiyomi|tachiyomi-zip|pdf|pdf-volume|pdf-single|cbz|cbz-volume|cbz-single|cb7|cb7-volume|cb7-single
Choose save as format, default to `raw`. 
For more information about formats, see {doc}`../formats`
```

## Network related

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

## Miscellaneous

````{option} --input-pos
Automatically select choices in selectable prompt (list, library, followed-list command)

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

```{option} -npb --no-progress-bar
Disable progress bar when downloading or converting
````

````{option} --no-track
```{note}
If you enable this, the application will not verify images and chapters. 
Also file `download.db` will not created.
```

Disable download tracking
````

## Update application

```{option} --update
Update mangadex-downloader to latest version
```