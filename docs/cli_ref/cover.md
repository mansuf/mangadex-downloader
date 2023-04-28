# Cover command

This command will show list of covers which you can choose and download it.

```{note}
This command will download covers only. The manga is not downloaded at all.
The covers will be stored in folder under manga title name (ex: "Official "Test" Manga")
```

## Syntax

It support following values:

- Full manga URL (https://mangadex.org/title/...)
- Full cover manga URL (https://mangadex.org/covers/...)
- Manga id only (f9c33607-9180-4ba6-b85c-e4b5faee7192)

### Original quality

```sh
mangadex-dl "cover:manga_id_or_full_url"
```

### 512px quality

```sh
mangadex-dl "cover-512px:manga_id_or_full_url"
```

### 256px quality

```sh
mangadex-dl "cover-256px:manga_id_or_full_url"
```

## Example usage

```sh
# Original quality (manga id only)
mangadex-dl "cover:f9c33607-9180-4ba6-b85c-e4b5faee7192"

# Original quality (full manga URL)
mangadex-dl "cover:https://mangadex.org/title/f9c33607-9180-4ba6-b85c-e4b5faee7192/official-test-manga"

# Original quality (full cover manga URL)
mangadex-dl "cover:https://mangadex.org/covers/f9c33607-9180-4ba6-b85c-e4b5faee7192/c18da525-e34f-4128-a696-4477b6ce6827.png"


# 512px quality (manga id only)
mangadex-dl "cover-512px:f9c33607-9180-4ba6-b85c-e4b5faee7192"

# 512px quality (full manga URL)
mangadex-dl "cover-512px:https://mangadex.org/title/f9c33607-9180-4ba6-b85c-e4b5faee7192/official-test-manga"

# 512px quality (full cover manga URL)
mangadex-dl "cover-512px:https://mangadex.org/covers/f9c33607-9180-4ba6-b85c-e4b5faee7192/c18da525-e34f-4128-a696-4477b6ce6827.png"
```