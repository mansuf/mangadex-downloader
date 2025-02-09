# Download MangaDex list from logged in user library

```{warning}
This method require authentication
```

You can download MangaDex list from logged in user library. Just type `list`, login, and select mdlist you want to download.

For example:

```shell
mangadex-dl "list" --login
# You will be prompted to input username and password for login to MangaDex
```

Also, you can download mdlist from another user. It will only fetch all public list only.

```{note}
Authentication is not required when download MangaDex list from another user.
```

For example:

```shell
mangadex-dl "list:give_the_user_id_here"
```
