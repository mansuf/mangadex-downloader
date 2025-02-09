# Show list of manga covers and download it

Wanna download the cover only ? I got you

```shell
# Manga id only
mangadex-dl "cover:manga_id"

# Full manga URL
mangadex-dl "cover:https://mangadex.org/title/..."

# Full cover manga URL
mangadex-dl "cover:https://mangadex.org/covers/..."
```

Don't wanna get prompted ? Use `--input-pos` option !

```sh
# Automatically select choice 1 
mangadex-dl "cover:https://mangadex.org/title/..." --input-pos 1 

# Automatically select all choices
mangadex-dl "cover:https://mangadex.org/title/..." --input-pos "*"
```

```{note}
This will download covers in original quality. 
If you want to use different quality, use command `cover-512px` for 512px quality 
and `cover-256px` for 256px quality.
```

For more information, see {doc}`../../cli_ref/cover`
