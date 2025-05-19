# Advanced usage

Moved to {doc}`./advanced/index`

<!-- ## Chapters and pages range syntax

mangadex-downloader already have these options for downloading chapters and pages `from n to n`

- `--start-chapter`
- `--end-chapter`
- `--start-page`
- `--end-page`
- `--no-oneshot-chapter`

```{warning}
Currently, this syntax only applied when downloading manga. You cannot use these option when download a chapter or list
```

But, imagine if you want to download specific chapters and pages. 
This is where special syntax for chapters and pages range comes to help.

The format syntax are:

```
chapters[pages]
```

### Supported operators

`````{option} !
Any chapter and page that comes with this operator will be ignored and not downloaded

````{warning}
You cannot use `!` operator with `-`. It will throw an error, if you trying to do it.

For example:

```shell
# Will throw an error because of "!3-30"
mangadex-dl "https://mangadex.org/title/..." --range "1,2,!3-30"
```
````
`````

```{option} -
From `begin` to `end` chapters and pages
```

### Example usage

```shell
mangadex-dl "https://mangadex.org/title/..." --range "1,4,5,6,90"
# Downloaded chapters: 1, 4, 5, 6, 90
```

```shell
mangadex-dl "https://mangadex.org/title/..." --range "1-9,!7,!5,20-30,!25"
# Downloaded chapters:
# 1,2,3,4,6,8,9,20,21,22,23,24,26,27,28,29,30
```

```shell
mangadex-dl "https://mangadex.org/title/..." --range "1[2-20],2[3-15],5[3-9,!5,12]"
# Downloaded chapters
# 1 with pages: 2 to 20
# 2 with pages: 3 to 15
# 3 with pages: 3,4,6,7,8,9,12
``` -->