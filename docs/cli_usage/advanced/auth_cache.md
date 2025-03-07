# Authentication cache

mangadex-downloader support authentication cache, which mean you can reuse your previous login session in mangadex-downloader 
without re-login.

```{note}
This authentication cache is stored in same place as where [config](#configuration) is stored.
```

You have to enable [config](#configuration) in order to get working.

If you enabled authentication cache for the first time, you must login in order to get cached.

```shell
mangadex-dl "https://mangadex.org/title/..." --login --login-cache

# or

mangadex-dl "conf:login_cache=true"
mangadex-dl "https://mangadex.org/title/..." --login
```

After this command, you no longer need to use `--login` option, 
use `--login` option if you want to update user login.

```shell
# Let's say user "abc123" is already cached
# And you want to change cached user to "def9090"
mangadex-dl "https://mangadex.org/title/..." --login
```

For more information, you can see here -> {doc}`../../cli_ref/auth_cache`
