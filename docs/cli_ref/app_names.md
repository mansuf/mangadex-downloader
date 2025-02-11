# Application names

## For PyPI users

- `mangadex-dl`
- `mangadex-downloader`

````{note}
If none of above doesn't work use this

```shell
# For Windows
py -3 -m mangadex_downloader

# For Linux
python3 -m mangadex_downloader
```
````

## For bundled executable users

It depend to the filename actually, 
by default the executable is named `mangdex-dl.exe`.

You can execute the application without ".exe". For example:

```sh
# With .exe
mangadex-dl.exe "insert manga url here"

# Without .exe
mangadex-dl "insert manga url here"
```