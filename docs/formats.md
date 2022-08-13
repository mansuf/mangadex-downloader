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

For CLI

```shell
mangadex-dl "insert MangaDex URL here"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL Here")
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as raw-volume
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL Here", save_as="raw-volume")
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as raw-single
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL Here", save_as="raw-single")
```

## tachiyomi

Same as `raw` format, except it has additional file "details.json" to provide additional info for manga.

If you don't know tachiyomi, it's android app for reading manga and it's open source !. You can learn more [here](https://tachiyomi.org/)

You can [read here](https://tachiyomi.org/help/guides/local-manga) for instruction how to create local manga in tachiyomi.

**NOTE: mangadex-downloader are not affliated with tachiyomi, the app only provide custom format for tachiyomi local manga.**

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
mangadex-dl "insert MangaDex URL here" --save-as "tachiyomi"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL Here", save_as="tachiyomi")
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "pdf-volume"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as='pdf-volume')
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cbz"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as="cbz")
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cbz-volume"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as='cbz-volume')
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cb7"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as="cb7")
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cb7-volume"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as='cb7-volume')
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

For CLI

```shell
mangadex-dl "insert MangaDex URL here" --save-as "cb7-single"
```

For embedding (API)

```python
from mangadex_downloader import download

manga = download("insert MangaDex URL here", save_as="cb7-single")
```