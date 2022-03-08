# Supported formats

mangadex-downloader can download in different formats, here a list of supported formats.

## tachiyomi

This is default format of mangadex-downloader, If you don't know tachiyomi, it's android app for reading manga and it's open source !. You can learn more [here](https://tachiyomi.org/)


You can [read here](https://tachiyomi.org/help/guides/local-manga) for instruction how to create local manga in tachiyomi

### Structure files

`tachiyomi` format files look like this

```
📦Manga title
 ┣ 📂Volume. 1 Chapter. 1
 ┃ ┣ 🖼️images
 ┣ 📂Volume. 1 Chapter. 2
 ┃ ┣ 🖼️images
 ┣ 🖼️cover.jpg
 ┗ 📜details.json
```

### Usage

For CLI

```shell
mangadex-dl "insert MangaDex URL here"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL Here")
```

## tachiyomi-zip

Same as `tachiyomi` except, all images in each chapter will stored in ZIP file.

### Structure files

`tachiyomi-zip` format files look like this

```
📦 Manga title
 ┣ 📜cover.jpg
 ┣ 📜details.json
 ┣ 📜Volume. 1 Chapter. 1.zip
 ┗ 📜Volume. 1 Chapter. 2.zip
```

### Usage

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "tachiyomi-zip"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as="tachiyomi-zip")
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "pdf"
```

For embedding (API)

```python

from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as='pdf')
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "pdf-single"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as="pdf-single")
```

## cbz

cbz or Comic Book Archive is a type of archive file for the purpose of sequential viewing of images, commonly for comic books. [wikipedia](https://en.wikipedia.org/wiki/Comic_book_archive)

### Structure files

`cbz` format files look like this

```
📦Manga title
 ┣ 📜cover.jpg
 ┣ 📜Volume. 1 Chapter. 1.cbz
 ┗ 📜Volume. 1 Chapter. 2.cbz
```

### Usage

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cbz"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as="cbz")
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cbz-single"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as="cbz-single")
```