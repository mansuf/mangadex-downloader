# Filters

mangadex-downloader support filters. These filters applied to search and random manga.

Example usage (Search manga)

```shell
# Search manhwa with status completed and ongoing, with tags "Comedy" and "Slice of life"
mangadex-dl -s -ft "status=completed,ongoing" -ft "original_language=Korean" -ft "included_tags=comedy, slice of life"

# or

mangadex-dl -s -ft "status=completed,ongoing" -ft "original_language=Korean" -ft "included_tags=4d32cc48-9f00-4cca-9b5a-a839f0764984, e5301a23-ebd9-49dd-a0cb-2add944c7fe9"
```

Example usage (Random manga)

```shell
# Search manga with tags "Comedy" and "Slice of life"
mangadex-dl "random" -ft "included_tags=comedy, slice of life"

# or

mangadex-dl "random" -ft "included_tags=4d32cc48-9f00-4cca-9b5a-a839f0764984, e5301a23-ebd9-49dd-a0cb-2add944c7fe9"
```

For more information about syntax and available filters, see {doc}`../../cli_ref/filters`
