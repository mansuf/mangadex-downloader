# Environment variables

```{option} MANGADEXDL_CONFIG_ENABLED [1 or 0, true or false]
Set this `1` or `true` to enable config, `0` or `false` to disable config.
```

```{option} MANGADEXDL_CONFIG_PATH
A directory to store config and authentication cache.
```

```{option} MANGADEXDL_ZIP_COMPRESSION_TYPE
Set zip compression type for any `cbz` and `epub` formats, 
by default it setted to `stored`

Must be one of:

- stored
- deflated
- bzip2
- lzma

For more information, see https://docs.python.org/3/library/zipfile.html#zipfile.ZIP_STORED
```

````{option} MANGADEXDL_ZIP_COMPRESSION_LEVEL
Set zip compression level for any `cbz` and `epub` formats.

```{note}
Zip compression type `stored` or `lzma` has no effect
```

levels:

- deflated : 0-9
- bzip2    : 1-9

For more information about each levels zip compression, 
see https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile
````