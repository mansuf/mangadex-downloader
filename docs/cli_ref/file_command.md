# File command (batch download command)

## Syntax

```shell
mangadex-dl "file:<location>"
```

## Arguments

```{option} location
A valid local or web (http, https) file location
```

## Example usage

### Batch download from local file

```shell
mangadex-dl "file:/etc/my-manga/lists-urls.txt"
```

### Batch download from web URL

```shell
mangadex-dl "file:https://raw.githubusercontent.com/mansuf/md-test-urls/main/urls.txt"
```
