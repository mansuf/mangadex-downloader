# Download a manga with different title

mangadex-downloader also support multi titles manga, which mean you can choose between different titles in different languages !

Example usage:

```shell
mangadex-dl "https://mangadex.org/title/..." --use-alt-details
# Manga "..." has alternative titles, please choose one
# (1). [English]: ...
# (2). [Japanese]: ...
# (3). [Indonesian]: ...
# => 
```

```{warning}
When you already downloaded a manga, but you wanna download it again with different title. It will re-download the whole manga.
```
