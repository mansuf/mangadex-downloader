# Forums

Imagine, you seeing a list of manga in some MangaDex forums thread and you want to download them all. 
Surely you copy each URLs from the thread and paste them into mangadex-downloader. 
You must be tired copy paste them all right ? and you wasted your time doing that.

Worry not, you can download all of them directly from mangadex-downloader itself !

**Wow, it so cool. How ?**

Just copy the forum thread url and paste it into mangadex-downloader

```sh
mangadex-dl "https://forums.mangadex.org/threads/whats-your-top-3-manga.1082493/"
```

That's it, you will be prompted to select which manga, chapter, or list you wanna download. 
If you don't wanna be prompted and just wanna download them all, you can use `--input-pos` option.

```sh
# "*" means all
mangadex-dl "https://forums.mangadex.org/threads/whats-your-top-3-manga.1082493/" --input-pos "*"
```

## Note

mangadex-downloader only shows results if the thread containing valid MangaDex urls.
