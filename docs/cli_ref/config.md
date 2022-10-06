# Configuration

## Syntax

```shell
mangadex-dl "conf:KEY=VALUE"
```

## Environment variables

```{option} MANGADEXDL_CONFIG_ENABLED [1 or 0, true or false]
Set this `1` or `true` to enable config, `0` or `false` to disable config.
```

```{option} MANGADEXDL_CONFIG_PATH
A directory to store config and authentication cache.
```

## Available configs

```{option} login_cache [1 or 0, true or false]
Same as `--login-cache`
```

```{option} language
Same as `--language` or `-lang`
```

```{option} cover
Same as `--cover` or `-c`
```

```{option} save_as
Same as `--save-as` or `-f`
```

```{option} use_chapter_title [1 or 0, true or false]
Same as `--use-chapter-title` or `-uct`
```

```{option} use_compressed_image [1 or 0, true or false]
Same as `--use-compressed-image` or `-uci`
```

```{option} force_https [1 or 0, true or false]
Same as `--force-https` or `-fh`
```

```{option} path
Same as `--path` or `--folder` or `-d`
```

```{option} dns_over_https
Same as `-doh` or `--dns-over-https`
```

```{option} no_chapter_info
Same as `-nci` or `--no-chapter-info`
```

```{option} no_group_name
Same as `-ngn` or `--no-group-name`
```

```{option} sort_by
Same as `--sort-by`
```

```{option} reset [config]
Reset config back to default value
```

## Example usage

### Enable config

```shell
# For Windows
set MANGADEXDL_CONFIG_ENABLED=1

# For Linux / Mac OS
export MANGADEXDL_CONFIG_ENABLED=1
```

### Change directory stored config to another path

```shell
# For Windows
set MANGADEXDL_CONFIG_PATH=D:\myconfig\here\lmao

# For Linux / Mac OS
export MANGADEXDL_CONFIG_PATH="/etc/mangadex-dl/config"
```

### Set a config

```shell
mangadex-dl "conf:save_as=pdf"
# Successfully changed config save_as from 'raw' to 'pdf'

mangadex-dl "conf:use_chapter_title=1"
# Successfully changed config use_chapter_title from 'False' to 'True'
```

### Print all configs

```shell
mangadex-dl "conf"
# Config 'login_cache' is set to '...'
# Config 'language' is set to '...'
# Config 'cover' is set to '...'
# Config 'save_as' is set to '...'
# Config 'use_chapter_title' is set to '...'
# Config 'use_compressed_image' is set to '...'
```

### Reset a config back to default value

```shell
mangadex-dl "conf:reset=save_as"
# Successfully reset config 'save_as'
```