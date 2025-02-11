# Path placeholders

Starting from v3.0.0, `--path` option are absolute and support placeholders.

## Syntax

```shell
mangadex-dl "URL" --path "./MyManga/{placeholder}"
```

Also we have some options for filenames as well.

- `--filename-chapter` for chapters format (cbz, pdf, epub, etc)
- `--filename-volume` for volumes format (cbz-volume, pdf-volume, etc)
- `--filename-single` for singles format (cbz-single, pdf-single, etc)

Example syntax:

```shell
mangadex-dl --filename-chapter "filenames {placeholder}"
```

## Placeholder objects for `--path` option

There's 4 placeholders that you can use in `--path` option.

| placeholder | description |
| --- | --- |
| manga | Manga that want to be downloaded |
| language | Language used to download manga (from `--language`), this value can be changed if you used `--language all` |
| format | Format used to download manga, grabbed from (`--format`) |
| user | Logged in user, you must login (`--login`) if you want use this placeholder |

Some placeholders have attributes that you can accesss, some of them are:

- manga
- user
- language

For more information, see below:

### Manga placeholder attributes

| attribute | description | type data |
| ----- | ----- | ----- |
| title | The title of the manga | [string](#string) |
| id | The unique identifier of manga | [string](#string) |
| alternative_titles | Alternative titles of the manga | [array](#array)[[string](#string)] |
| description | The description of the manga | [string](#string) |
| authors | List of authors of the manga separated by comma | [string](#string) |
| artists | List of artists of the manga separated by comma | [string](#string) |
| cover | Manga main cover | [CoverArt](#coverart) |
| genres | List of manga genres separated by comma | [string](#string) |
| status | Status of the manga (hiatus, completed, etc) | [string](#string) |
| content_rating | Content rating of the manga (safe, suggestive, etc) | [ContentRating](#contentrating-and-language) |
| tags | List of manga tags separated by comma | [string](#string) |

### User placeholder attributes

| attribute | description | type data |
| ----- | ----- | ----- |
| id | The unique identifier of user | [string](#string) |
| name | An username | [string](#string) |

### Language placeholder attributes

| attribute | description | type data |
| ----- | ----- | ----- |
| full | Language in full text (ex: `English`) | [string](#string) |
| simple | Language in simplified text (ex: `en`) | [string](#string) |

## Placeholder objects for `--filename-chapter` option

There's 2 placeholders that you can use in `--filename-chapter` option.

| placeholder | description |
| --- | --- |
| chapter | Chapter that being downloaded currently |
| file_ext | File extension |

````{note}
This option support `manga` placeholder, so you can access manga placeholder for `--filename-chapter` option

For example:

```sh
mangadex-dl "url" -f cbz --filename-chapter "{manga.title} Ch. {chapter.chapter}{file_ext}"
```
````

### Chapter placeholder attributes

| attribute | description | type data |
| ----- | ----- | ----- |
| chapter | Manga chapter in number from 0 to 1 (You can get `Unknown` if there is no valid chapter number) | [integer](#integer) |
| volume | Manga volume in number from 0 to 1 (You can get `Unknown` if there is no valid volume number) | [integer](#integer) |
| title | Chapter title | [string](#string) |
| pages | Total pages in the chapter | [integer](#integer) |
| language | Chapter language | [Language](#contentrating-and-language) |
| name | Full parsed chapter name (ex: `Volume. 69 Chapter. 69`) | [string](#string) |
| simple_name | Simplified parsed chapter name (ex: `Vol. 69 Ch. 69`) | [string](#string) |
| groups_name | List of scanlation groups for the chapter separated by `&` (you can get `User - username` if there is no scanlation groups available) | [string](#string) |

## Placeholder objects for `--filename-volume` option

There's 2 placeholders that you can use in `--filename-volume` option.

| placeholder | description |
| --- | --- |
| volume | Manga volume |
| file_ext | File extension |

````{note}
This option support `manga` placeholder, so you can access manga placeholder for `--filename-volume` option

For example:

```sh
mangadex-dl "url" -f cbz-volume --filename-volume "{manga.title} Vol. {chapter.volume}{file_ext}"
```
````

### Volume placeholder attributes

| attribute | description | type data |
| --- | --- | --- |
| chapters | List of chapters in the volume | [ArrayModified](#arraymodified)[[Chapter](#chapter-placeholder-attributes)] |

## Placeholder objects for `--filename-single` option

There's 2 placeholders that you can use in `--filename-single` option.

| placeholder | description |
| --- | --- |
| chapters | List of all chapters in the manga, the attributes is same as [`chapters` in volume placeholder](#volume-placeholder-attributes) |
| file_ext | File extension |

````{note}
This option support `manga` placeholder, so you can access manga placeholder for `--filename-single` option

For example:

```sh
mangadex-dl "url" -f cbz-single --filename-single "{manga.title} All Chapters{file_ext}"
```
````

## Data types

Here you can find a data types that used in mangadex-downloader path placeholders

### string

It's a text.

The string type data follows python f-string (formatted string). 
You can read more about it [in here](https://docs.python.org/3/library/string.html#format-specification-mini-language)

### integer

It's a negative or positive number

### array

It's a list of data, 
you can access a data by giving index position.

```{note}
You may see additional data type inside of a bracket

Like this one: `array[string]`

This means inside the array is an list of strings.
```

For example:

```shell
# Let's say you want to get alternative title
# You can do this by accessing `alternative_titles` in manga placeholder
# This will get alternative title in position 0 of an list
mangadex-dl "URL" --path "/home/mymanga/{manga.alternative_titles[0]}"
```

### ArrayModified

Same as `array` data type, but it has additional attributes

- first
- last

These attributes is equals to accessing array with index `0` or `-1`.

Let me give you an example:

```shell
# Doing this
mangadex-dl "URL" --filename-volume "Vol. {volume} (Ch. {volume.chapters.first.chapter} - Ch. {volume.chapters.last.chapter})"

# Is equal to
mangadex-dl "URL" --filename-volume "Vol. {volume} (Ch. {volume.chapters[0].chapter} - Ch. {volume.chapters[-1].chapter})"
```

I know some of you asking "But why ? why you did this ?"

Because it looks elegant and clean 😂👌.

### ContentRating and Language

This data type contain these attributes

| attribute | description |
| --- | --- |
| value | Lowercase or short text (for example: safe, en) |
| name | Capitalized or long text (for example: Safe, English) |

### CoverArt

This data type contain these attributes

| attribute | description |
| --- | --- |
| id | CoverArt manga id |
| description | Cover manga description |
| file | Filename of the cover manga |
| locale | Cover manga language (type data: [Language](#contentrating-and-language)) |

## Examples

```shell
# This manga will be saved in directory
# "/home/verysus/manga/Some manga title/English"
# with cbz format and custom filename with placeholders
mangadex-dl "URL" -f cbz --path "/home/verysus/manga/{manga.title}/{language.full}" --filename-chapter "Vol. {chapter.volume} Ch. {chapter.chapter}{file_ext}"
```
