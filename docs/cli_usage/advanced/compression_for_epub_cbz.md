# Enable compression for epub and cbz formats

By default, the application didn't enable compression for cbz and epub formats. 
In order to enable compression you must use 2 environment variables

```sh
# For Linux / Mac OS
export MANGADEXDL_ZIP_COMPRESSION_TYPE=deflated
export MANGADEXDL_ZIP_COMPRESSION_LEVEL=9
```

```batch
:: For Windows
set MANGADEXDL_ZIP_COMPRESSION_TYPE=deflated
set MANGADEXDL_ZIP_COMPRESSION_LEVEL=9
```

For more information, see:

- [MANGADEXDL_ZIP_COMPRESSION_TYPE](https://mangadex-dl.mansuf.link/en/stable/cli_ref/env_vars.html#cmdoption-arg-MANGADEXDL_ZIP_COMPRESSION_TYPE)
- [MANGADEXDL_ZIP_COMPRESSION_LEVEL](https://mangadex-dl.mansuf.link/en/stable/cli_ref/env_vars.html#cmdoption-arg-MANGADEXDL_ZIP_COMPRESSION_LEVEL)
