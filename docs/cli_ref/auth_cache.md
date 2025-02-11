# Authentication cache

Reuse authentication tokens for later use. These tokens stored in same place as [config](./config) is stored. 
You don't have to use `--login` again with this, just run the app and you will be automatically logged in.

```{warning}
You must enable config in order to use authentication cache.
```

## Syntax command

```shell
mangadex-dl "login_cache:<subcommand>"
```

## Available sub commands

```{option} purge
Invalidate and purge cached authentication tokens
```

```{option} show
Show expiration time cached authentication tokens 
```

````{option} show_unsafe
```{warning}
You should not use this command, 
because it exposing your auth tokens to terminal screen. 
Use this if you know what are you doing.
```

Show cached authentication tokens
````

## Example usage commands

### Enable authentication cache

```shell
mangadex-dl "conf:login_cache=1"

# You must login first in order to get cached
mangadex-dl "tamamo no koi" --login -s

# After that you won't need to use --login anymore
mangadex-dl "another manga lmao" -s
```

### Invalidate and purge cached authentication tokens

```shell
mangadex-dl "login_cache:purge"
```

### Show expiration time session token and refresh token

```shell
mangadex-dl "login_cache:show"

# or

mangadex-dl "login_cache"
```
