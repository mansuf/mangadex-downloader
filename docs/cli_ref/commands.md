# Commands

Here is a list of available commands that you can execute in mangadex-downloader. 
Most of them are for to show and download manga or lists. 
This command can be executed through `URL` parameter, see syntax below

## Syntax

```sh
# Command without argument
mangadex-dl "command"

# Command with argument
mangadex-dl "command:arg"

# Command with multiple arguments
mangadex-dl "command:arg1, arg2, arg3"
```

## Available commands

```{option} random
Show 5 of random manga and select to download

For more information, see {doc}`./random`
```

````{option} library STATUS
```{note}
This command require authentication
```
Show list of saved manga from logged in user

For more information, see {doc}`manga_library`
````

````{option} list USER-ID
```{note}
Argument `USER-ID` are optional. 
You must login if you didn't use `USER-ID` argument
```
Show list of saved MDLists from logged in user

For more info, see {doc}`./list_library`
````

````{option} followed-list
```{note}
This command require authentication
```
Show list of followed MDLists from logged in user

For more info, see {doc}`./follow_list_library`
````

```{option} group GROUP-ID
Show and download list of manga from a group that have uploaded scanlated chapters
```

````{option} file PATH_TO_FILE
```{note}
Path file can be offline or online location. 
If you're using file from online location, it only support HTTP(s) method.
```
Download list of manga, chapters or lists from a file

For more info, see {doc}`./file_command`
````

````{option} seasonal SEASON
```{note}
Argument `SEASON` are optional
```
Select and download seasonal manga

For more info, see {doc}`./seasonal_manga`
````

```{option} conf CONFIG_KEY=CONFIG_VALUE
Modify or show config

For more info, see {doc}`./config`
```

```{option} login_cache SUBCOMMAND
Modify or show cached authentication tokens expiration time

For more info, see {doc}`./auth_cache`
```

## Example usage

### Random manga command

```sh
mangadex-dl "random"
```

### File command

```sh
# Offline location
mangadex-dl "file:/home/user/mymanga/urls.txt"

# Online location
mangadex-dl "file:https://raw.githubusercontent.com/mansuf/md-test-urls/main/urls.txt"
```

### Modify and show configs

```sh
# Show all configs
mangadex-dl "conf"

# Show `save_as` config value
mangadex-dl "conf:save_as"

# Change `dns_over_https` config value
mangadex-dl "conf:dns_over_https=google"
```