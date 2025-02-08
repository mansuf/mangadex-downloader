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
| title | The title of the manga | [string](#string-type-data) |
| id | The unique identifier of manga | [string](#string-type-data) |
| alternative_titles | Alternative titles of the manga | array[[string](#string-type-data)] |
| description | The description of the manga | [string](#string-type-data) |
| authors | List of authors of the manga separated by comma | [string](#string-type-data) |
| artists | List of artists of the manga separated by comma | [string](#string-type-data) |
| cover | Manga main cover | CoverArt |
| genres | List of manga genres separated by comma | [string](#string-type-data) |
| status | Status of the manga (hiatus, completed, etc) | [string](#string-type-data) |
| content_rating | Content rating of the manga (9.0, 6.9, etc) | ContentRating |
| tags | List of manga tags separated by comma | [string](#string-type-data) |

### User placeholder attributes

| attribute | description | type data |
| ----- | ----- | ----- |
| id | The unique identifier of user | [string](#string-type-data) |
| name | An username | [string](#string-type-data) |

### Language placeholder attributes

| attribute | description | type data |
| ----- | ----- | ----- |
| full | Language in full text (ex: `English`) | [string](#string-type-data) |
| simple | Language in simplified text (ex: `en`) | [string](#string-type-data) |

## Placeholder objects for `--filename-chapter` option

There's 2 placeholders that you can use in `--filename-chapter` option.

| placeholder | description |
| --- | --- |
| chapter | Chapter that being downloaded currently |
| file_ext | File extension |

### Chapter placeholder attributes

| attribute | description | type data |
| ----- | ----- | ----- |
| chapter | Manga chapter in number from 0 to 1 (You can get `Unknown` if there is no valid chapter number) | [integer](#integer-type-data) |
| volume | Manga volume in number from 0 to 1 (You can get `Unknown` if there is no valid volume number) | [integer](#integer-type-data) |
| title | Chapter title | [string](#string-type-data) |
| pages | Total pages in the chapter | [integer](#integer-type-data) |
| language | Chapter language | Language |
| name | Full parsed chapter name (ex: `Volume. 69 Chapter. 69`) | [string](#string-type-data) |
| simple_name | Simplified parsed chapter name (ex: `Vol. 69 Ch. 69`) | [string](#string-type-data) |
| groups_name | List of scanlation groups for the chapter separated by `&` (you can get `User - username` if there is no scanlation groups available) | [string](#string-type-data) |

## Placeholder objects for `--filename-volume` option

There's 2 placeholders that you can use in `--filename-volume` option.

| placeholder | description |
| --- | --- |
| volume | Manga volume |
| file_ext | File extension |

### Volume placeholder attributes

| attribute | description | type data |
| --- | --- | --- |
| chapters | List of chapters in the volume | [ArrayModified](#arraymodified-type-data)[Chapter] |

## Placeholder objects for `--filename-single` option

There's 2 placeholders that you can use in `--filename-single` option.

| placeholder | description |
| --- | --- |
| chapters | List of all chapters in the manga, the attributes is same as [`chapters` in volume placeholder](#volume-placeholder-attributes) |
| file_ext | File extension |

## Types data

Here you can find a data types that used in mangadex-downloader path placeholders

### string type data

It's a text.

The string type data follows python f-string (formatted string). 
You can read more about it [in here](https://docs.python.org/3/library/string.html#format-specification-mini-language)

### integer type data

It's a negative or positive number

### array type data

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

### ArrayModified type data

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

## Examples

```shell
# This manga will be saved in directory
# "/home/verysus/manga/Some manga title/English"
# with cbz format and custom filename with placeholders
mangadex-dl "URL" -f cbz --path "/home/verysus/manga/{manga.title}/{language.full}" --filename-chapter "Vol. {chapter.volume} Ch. {chapter.chapter}{file_ext}"
```
