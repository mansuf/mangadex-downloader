# Download manga, chapter, or list from pipe input

mangadex-downloader support pipe input. You can use it by adding `-pipe` option.

```shell
echo "https://mangadex.org/title/..." | mangadex-dl -pipe
```

Multiple lines input also supported.

```shell
# For Linux / Mac OS
cat "urls.txt" | mangadex-dl -pipe

# For Windows
type "urls.txt" | mangadex-dl -pipe
```

Also, you can use another options when using pipe

```shell
echo "https://mangadex.org/title/..." | mangadex-dl -pipe --path "/home/myuser" --cover "512px"
```
