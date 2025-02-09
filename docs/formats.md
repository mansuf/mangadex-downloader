# Supported formats

mangadex-downloader can download in different formats, here a list of supported formats.

## raw

This is default format of mangadex-downloader. It's just bunch of images stored in each chapter folders.

### Structure files

`raw` format files look like this

```
📦Manga title
 ┣ 📂Volume. 1 Chapter. 1
 ┃ ┣ 🖼️images
 ┣ 📂Volume. 1 Chapter. 2
 ┃ ┣ 🖼️images
 ┗ 🖼️cover.jpg
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here"
```

## raw-volume

Same as `raw` format, except all chapters wrapped into each volumes.

### Structure files

`raw-volume` format files look like this

```
📦Manga title
 ┣ 📂Volume. 1
 ┃ ┣ 🖼️images
 ┣ 📂No Volume
 ┃ ┣ 🖼️images
 ┗ 🖼️cover.jpg
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as raw-volume
```

## raw-single

Same as `raw` format, except all chapters wrapped into single folder.

### Structure files

`raw-single` format files look like this

```
📦Manga title
 ┣ 📂Volume. 1 Chapter. 1 - Volume. 1 Chapter. 2
 ┃ ┣ 🖼️images
 ┗ 🖼️cover.jpg
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as raw-single
```

## pdf

All images in each chapter will be converted to PDF file (.pdf)

### Structure files

`pdf` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1 Chapter. 1.pdf
 ┗ 📜Volume. 1 Chapter. 2.pdf
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "pdf"
```

## pdf-volume

Same as `pdf`, except all chapters wrapped into each volumes PDF file.

### Structure files

`pdf-volume` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1.pdf
 ┗ 📜Volume. 2.pdf
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "pdf-volume"
```

## pdf-single

same as `pdf` format, except all chapters wrapped into single PDF file

### Structure files

`pdf-single` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┗ 📜Volume. 1 Chapter. 1 - Volume. 1 Chapter. 2.pdf
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "pdf-single"
```

## cbz

This is Comic Book Archive format. Comic Book Archive is a type of archive file for the purpose of sequential viewing of images, commonly for comic books. [wikipedia](https://en.wikipedia.org/wiki/Comic_book_archive)

It has additional file (`ComicInfo.xml`) inside of .cbz file, useful for showing details of the manga (if an reader support it).

This format was based of `zip` extension.

### Structure files

`cbz` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1 Chapter. 1.cbz
 ┗ 📜Volume. 1 Chapter. 2.cbz
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cbz"
```

## cbz-volume

same as `cbz` format, except all chapters wrapped into each volumes .cbz file

### Structure files

`cbz-volume` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1.cbz
 ┗ 📜Volume. 2.cbz
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cbz-volume"
```

## cbz-single

same as `cbz` format, except all chapters wrapped into single .cbz file

### Structure files

`cbz-single` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┗ 📜Volume. 1 Chapter. 1 - Volume. 1 Chapter. 2.cbz
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cbz-single"
```

## cb7

This is Comic Book Archive format. Comic Book Archive is a type of archive file for the purpose of sequential viewing of images, commonly for comic books. [wikipedia](https://en.wikipedia.org/wiki/Comic_book_archive)

This format was based of `7z` extension.

### Structure files

`cb7` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1 Chapter. 1.cb7
 ┗ 📜Volume. 1 Chapter. 2.cb7
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cb7"
```

## cb7-volume

same as `cb7` format, except all chapters wrapped into each volumes .cb7 file

### Structure files

`cb7-volume` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1.cb7
 ┗ 📜Volume. 2.cb7
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cb7-volume"
```

## cb7-single

same as `cb7` format, except all chapters wrapped into single .cb7 file

### Structure files

`cb7-single` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┗ 📜Volume. 1 Chapter. 1 - Volume. 1 Chapter. 2.cb7
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cb7-single"
```

## epub

An electronic book file format that is supported by many e-readers. [Wikipedia](https://en.wikipedia.org/wiki/EPUB).

This format was based of `zip` extension

### Structure files

`epub` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1 Chapter. 1.epub
 ┗ 📜Volume. 1 Chapter. 2.epub
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "epub"
```

## epub-volume

Same as `epub` format, except all chapters wrapped into each volumes.

```{note}
Unlike any other `volume` and `single` formats, `epub-volume` and `epub-single` doesn't create chapter info (or cover).

If you don't know what that means, you can have look here -> {doc}`../cli_ref/chapter_info`
```

### Structure files

`epub-volume` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1.epub
 ┗ 📜Volume. 2.epub
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "epub-volume"
```

## epub-single

Same as `epub` format, except all chapters wrapped into single .epub file.

```{note}
Unlike any other `volume` and `single` formats, `epub-volume` and `epub-single` doesn't create chapter info (or cover).

If you don't know what that means, you can have look here -> {doc}`../cli_ref/chapter_info`
```

### Structure files

`epub-single` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┗ 📜Volume. 1 Chapter. 1 - Volume. 1 Chapter. 2.epub
```

### Usage

```shell
mangadex-dl "insert MangaDex URL here" --save-as "epub-single"
```