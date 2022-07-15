# Pornographic and erotica content

By default, mangadex-downloader doesn't allow downloading porn and erotica manga. If you're trying to do it, you will get "You are not allowed to see ..." error.

However, there is a way you can bypass this restriction (if you have to **you know ( ͡° ͜ʖ ͡°)**). You can use `--unsafe` or `-u` option.

For example:

```shell
mangadex-dl "https://mangadex.org/title/..." --unsafe
```

It also applied to search too.

```shell
# This will NOT show any of porn and erotica mangas
mangadex-dl "some porn keyword here" --search

# This will show porn and erotica mangas
mangadex-dl "some porn keyword here" --search --unsafe
```

Even to individual chapter

```shell
# Let's say this is chapter from porn and erotica manga
# You will get "You are not allowed to see .." error
mangadex-dl "https://mangadex.org/chapter/..."

# No more error 👍
mangadex-dl "https://mangadex.org/chapter/..." --unsafe
```

What about MangaDex list ? When there is 1 or more porn or erotica manga in some list, it will be ignored and not downloaded. 
Use `--unsafe` or `-u` to download all mangas with porn and erotica manga included.

```shell
mangadex-dl "https://mangadex.org/list/..." --unsafe

```

Stay in the bright side brothers 👍, don't let the dark side take control of you.