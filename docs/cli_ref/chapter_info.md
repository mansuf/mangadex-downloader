# Chapter info (cover)

![chapter info](../images/chapter_info.png)

This is called chapter info (some people would call this "cover"). 
This gives you information what chapter currently you reading on.

This applied to this formats

- `raw-volume`
- `raw-single`
- `cbz-volume`
- `cbz-single`
- `cb7-volume`
- `cb7-single`
- `pdf-volume`
- `pdf-single`

```{note}
any `epub` formats doesn't create chapter info, 
because obviously there is "Table of Contents" feature in EPUB (if an e-reader support it).
```

You can enable chapter info creation by giving `--use-chapter-cover` or `-ucc` to the app

```shell
mangadex-dl "URL" -f pdf-volume --use-chapter-cover
```
