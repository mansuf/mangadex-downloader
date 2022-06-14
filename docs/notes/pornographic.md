# Pornographic content

By default, mangadex-downloader doesn't allow downloading porn manga. If you're trying to do it, you will get "You are not allowed to see ..." error.

However, there is a way to get rid of this. You can use `--unsafe` or `-u` option.

For example:

```shell
mangadex-dl "https://mangadex.org/title/..." --unsafe
```

It also applied to search too.

```shell
# This will NOT show any of porn mangas
mangadex-dl "some porn keyword here" --search

# This will show porn mangas
mangadex-dl "some porn keyword here" --search --unsafe
```

Even to individual chapter

```shell
# Let's say this is chapter from porn manga
# You will get "You are not allowed to see .." error
mangadex-dl "https://mangadex.org/chapter/..."

# No more error 👍
mangadex-dl "https://mangadex.org/chapter/..." --unsafe
```

What about MangaDex list ? When there is 1 or more porn manga in some list, it will be ignored and not downloaded. 
Use `--unsafe` or `-u` to download all mangas with porn manga included.

```shell
mangadex-dl "https://mangadex.org/list/..." --unsafe

```

## Questions and answers

**Q:** But why ?

**A:** Good question. To compliance with other countries with porn restriction.

**Q:** What about erotica content ? isn't that a porn too ?

**A:** 

```{image} ../images/well_yes_but_actually_no.jpg
:width: 500px
:height: 300px
```

Stay in the bright side brothers 👍, don't let the dark side take control of you.

