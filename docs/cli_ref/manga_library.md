# Manga library command

Show all saved mangas from logged in user. You will be prompted to select which manga want to download.

```{note}
You must login in order to use this command. Otherwise it will not work.
```

## Syntax

```shell
mangadex-dl "library:<status>" --login
```

If `<status>` is given, it will filter manga library based on reading status. 
If not, then it will show all manga in the library.

## Statuses

```{option} reading
```

```{option} on_hold
```

```{option} plan_to_read
```

```{option} dropped
```

```{option} re_reading
```

```{option} completed
```

```{option} help
Show all available statuses
```

## Example usage

### Show all manga in user library

```shell
# User will be prompted to select which manga wants to download
# And then save it as pdf format
mangadex-dl "library" --login --save-as pdf
```

### Show manga with reading status "Plan to read" in user library

```shell
mangadex-dl "library:plan_to_read" --login
```