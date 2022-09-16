# Authentication cache

```{warning}
You must enable config in order to use authentication cache.
```

```shell
# Enable authentication cache
mangadex-dl "conf:login_cache=1"
```

## Available commands

```{option} purge
Purge cached authentication tokens
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

### Purge cached authentication tokens

```shell
mangadex-dl "login_cache:purge"
```

### Show expiration time session token and refresh token

```shell
mangadex-dl "login_cache:show"

# or

mangadex-dl "login_cache"
```
