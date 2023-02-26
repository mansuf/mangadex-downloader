# Configuration

These configs automatically written into command-line options value,
so you don't have to write a bunch command line options. 
Just set a config and the app will automatically set the value to command-line options.

Still confused how is it working ? see this example

Let's say you want to download a manga with

- Forced HTTPS port
- No progress bar
- Using DNSOverHTTPS to cloudflare
- No manga cover
- No group name in each chapters
- And the chapters language must Indonesian
- And store it to `manga` directory

The results:

```shell
mangadex-dl "https://mangadex.org/title/..." --force-https --no-progress-bar --dns-over-https "cloudflare" --cover "none" --no-group-name --language "Indonesian" --path "manga"
```

It is wayyyy too longgggggg and you have to write these command-line options everytime to download manga. 
How to fix this ? **Config** is the only answer !

First, enable config first.

```shell
# `1` is alias for True and `0` is alias for False

# For Windows
set MANGADEXDL_CONFIG_ENABLED=1

# For Linux / Mac OS
export MANGADEXDL_CONFIG_ENABLED=1
```

```{note}
Keep in mind this is for current session console only. If you want to set it permanently, 
change the user environment variables.
```

Second, set the values for configs

```shell
# `1` is alias for True and `0` is alias for False
mangadex-dl "conf:force_https=1"
mangadex-dl "conf:no_progress_bar=1"
mangadex-dl "conf:dns_over_https=cloudflare"
mangadex-dl "conf:cover=none"
mangadex-dl "conf:no_group_name=1"
mangadex-dl "conf:language=Indonesian"
mangadex-dl "conf:path=manga"
```

After that you can download the manga without writing very-very long command-line options

```shell
mangadex-dl "https://mangadex.org/title/..."
```

**But, i don't want type all those commands. I just want single command, 
just type the file that i have every configs that i wanna change and it changed**.

Well, you can do it too. But, this time we're using `-pipe` option.

Let's say you have `config.txt`. And inside of that file is that every configs that you wanna change.

```shell
conf:force_https=1
conf:no_progress_bar=1
conf:dns_over_https=cloudflare
conf:cover=none
conf:no_group_name=1
conf:language=Indonesian
conf:path=manga
```

And then you execute these commands:

```shell
# For Windows
type config.txt | mangadex-dl -pipe

# For Linux / Mac OS
cat config.txt | mangadex-dl -pipe
```

Horray ! your configs is now changed.

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

```{option} no_progress_bar
Same as `-npb` or `--no-progress-bar`
```

```{option} http_retries
Same as `--http-retries`
```

```{option} no_track
Same as `--no-track`
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