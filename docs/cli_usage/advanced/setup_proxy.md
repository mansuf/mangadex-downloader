# Setup proxy

```shell
# HTTP proxy
mangadex-dl "https://mangadex.org/title/..." --proxy "http://127.0.0.1"

# SOCKS proxy
mangadex-dl "https://mangadex.org/title/..." --proxy "socks://127.0.0.1"
```

mangadex-downloader support proxy from environments

```shell
# For Linux / Mac OS
export http_proxy="http://127.0.0.1"
export https_proxy="http://127.0.0.1"

# For Windows
set http_proxy=http://127.0.0.1
set https_proxy=http://127.0.0.1

mangadex-dl "insert mangadex url here" --proxy-env
```

```{warning}
You cannot use `--proxy` and `--proxy-env` together. It will throw error, if you're trying to do it
```
