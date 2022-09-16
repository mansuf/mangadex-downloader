# Search filters

## Syntax

```shell
mangadex-dl -s -sf "FILTER_KEY=FILTER_VALUE"
```

It also support multiple values separated by commas

```shell
mangadex-dl -s -sf "FILTER_KEY=FILTER_VALUE1,FILTER_VALUE2,FILTER_VALUE3"
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
mangadex-dl -s -sf "original_language=Japanese" -sf "content_rating=erotica" -sf "status=completed"
```

Search manhwa with "highest rating" order

```shell
mangadex-dl -s -sf "original_language=Korean" -sf "order[rating]=descending"
```