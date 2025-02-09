# Configuration

mangadex-downloader support local config stored in local disk. You must set `MANGADEXDL_CONFIG_ENABLED` to `1` or `true` in order to get working.

```shell
# For Windows
set MANGADEXDL_CONFIG_ENABLED=1

# For Linux / Mac OS
export MANGADEXDL_CONFIG_ENABLED=1
```

These config are stored in local user directory (`~/.mangadex-dl`). If you want to change location to store these config, you can set `MANGADEXDL_CONFIG_PATH` to another path.

```{note}
If new path is doesn't exist, the app will create folder to that location.
```

```shell
# For Windows
set MANGADEXDL_CONFIG_PATH=D:\myconfig\here\lmao

# For Linux / Mac OS
export MANGADEXDL_CONFIG_PATH="/etc/mangadex-dl/config"
```

Example usage

```shell
mangadex-dl "conf:save_as=pdf"
# Successfully changed config save_as from 'raw' to 'pdf'

mangadex-dl "conf:use_chapter_title=1"
# Successfully changed config use_chapter_title from 'False' to 'True'
```

For more information, you can see -> {doc}`../../cli_ref/config`
