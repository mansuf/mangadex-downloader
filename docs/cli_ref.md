# Command-line Interface (CLI) reference

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

```{option} --verbose
Enable verbose output
```

```{option} --search -s
Search a manga and then download it
```

```{option} --unsafe -u
If set, it will allow you to search and download porn manga
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

### Chapter page related

```{option} --start-page -sp NUM_PAGE
Start download chapter page from given page number
```

```{option} --end-page -ep NUM_PAGE
Stop download chapter page from given page number
```

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

### Save as format

```{option} --save-as -f raw|raw-volume|raw-single|tachiyomi|tachiyomi-zip|pdf|pdf-volume|pdf-single|cbz|cbz-volume|cbz-single|cb7|cb7-volume|cb7-single
Choose save as format, default to `raw`
```

### Proxy related

```{option} --proxy -p SOCKS / HTTP Proxy
Set http/socks proxy
```

```{option} --proxy-env -pe
use http/socks proxy from environments
```

### Miscellaneous

```{option} -pipe
If set, the app will accept pipe input
```

````{option} --enable-legacy-sorting

```{warning}
Deprecated, will be removed in v1.3.0.
```
Does nothing. In previous version this option is used
to enable legacy sorting. Which rename all images with numbers leading zeros (example: 001.jpg)
````

```{option} --no-verify -nv
Skip hash checking for each images
```

```{option} -v --version
Print mangadex-downloader version
```

### Update application

```{option} --update
Update mangadex-downloader to latest version
```