# Download manga from logged in user library

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
