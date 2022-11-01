# Filters

## Syntax

It's accesible from `-ft` or `--filter` option

```shell
mangadex-dl -s -ft "KEY=VALUE"
```

It also support multiple values separated by commas

```shell
mangadex-dl "random" -ft "KEY=VALUE1,VALUE2,VALUE3"
```

```{note}
random manga has limited filters, here a list of available filters for random manga.

- included_tags
- included_tags_mode
- excluded_tags
- excluded_tags_mode

```

## Available filters

```{option} authors [VALUE1, VALUE2, ...]
Authors of manga
```

```{option} artists [VALUE1, VALUE2, ...]
Artists of manga
```

```{option} year [INTEGER]
Year of release
```

```{option} included_tags [VALUE1, VALUE2, ...]
Value must be valid keyword or uuid or MangaDex url containing uuid. 
To see all available tags in MangaDex -> https://mangadex.org/tag/
```

```{option} included_tags_mode [OR, AND]
```

```{option} excluded_tags [VALUE1, VALUE2, ...]
Value must be valid keyword or uuid or MangaDex url containing uuid. 
To see all available tags in MangaDex -> https://mangadex.org/tag/
```

```{option} excluded_tags_mode [OR, AND]
```

```{option} status [VALUE1, VALUE2, ...]
Must be one of:

- ongoing
- completed
- hiatus
- cancelled
```

```{option} original_language [VALUE1, VALUE2, ...]
Must be one of valid languages returned from `mangadex-dl --list-languages`
```

```{option} excluded_original_language [VALUE1, VALUE2, ...]
Must be one of valid languages returned from `mangadex-dl --list-languages`
```

```{option} available_translated_language [VALUE1, VALUE2, ...]
Must be one of valid languages returned from `mangadex-dl --list-languages`
```

```{option} publication_demographic [VALUE1, VALUE2, ...]
Must be one of:

- shounen
- shoujo
- josei
- seinen
- none
```

```{option} content_rating [VALUE1, VALUE2, ...]
Must be one of:

- safe
- suggestive
- erotica
- pornographic
```

```{option} created_at_since [DATETIME]
value must matching format `%Y-%m-%dT%H:%M:%S`
```

```{option} updated_at_since [DATETIME]
value must matching format `%Y-%m-%dT%H:%M:%S`
```

```{option} has_available_chapters [1 or 0, true or false]
```

```{option} order[title] [asc or ascending, desc or descending]
```

```{option} order[year] [asc or ascending, desc or descending]
```

```{option} order[createdAt] [asc or ascending, desc or descending]
```

```{option} order[updatedAt] [asc or ascending, desc or descending]
```

```{option} order[latestUploadedChapter] [asc or ascending, desc or descending]
```

```{option} order[followedCount] [asc or ascending, desc or descending]
```

```{option} order[relevance] [asc or ascending, desc or descending]
```

```{option} order[rating] [asc or ascending, desc or descending]
```

## Example usage

Search manga with content rating erotica and status completed 

```shell
mangadex-dl -s -ft "original_language=Japanese" -ft "content_rating=erotica" -ft "status=completed"
```

Search manhwa with "highest rating" order

```shell
mangadex-dl -s -ft "original_language=Korean" -ft "order[rating]=descending"
```

Random manga with oneshot tags but without yuri and yaoi tags

```shell
mangadex-dl "random" -ft "included_tags=oneshot" -ft "excluded_tags=boys' love, girls' love"
```