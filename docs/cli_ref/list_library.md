# List library command

Show all saved MangaDex lists from logged in user or from another user. You will be prompted to select which list want to download.

## Syntax

```shell
mangadex-dl "list:<user-id>"
```

If `<user-id>` is given, it will show all public MangaDex lists from that user. 
Otherwise it will show all MangaDex lists from logged in user.

You can give just the id or full URL to `<user-id>`.

```{note}
Authentication is required if `<user-id>` is not given.
```

## Example usage

Show all MangaDex lists (private and public) from logged in user

```shell
mangadex-dl "list" --login
```

Show all public MangaDex lists from another user

```shell
# MangaDex lists from user "BraveDude8" (one of MangaDex moderators)
mangadex-dl "list:https://mangadex.org/user/81304b72-005d-4e62-bea6-4cb65869f7da"
# or
mangadex-dl "list:81304b72-005d-4e62-bea6-4cb65869f7da"
```