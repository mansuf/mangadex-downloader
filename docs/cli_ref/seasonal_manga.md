# Seasonal manga

## Syntax

```
mangadex-dl "seasonal:<season>"
```

If `<season>` is given, it will show seasonal manga based on given season. 
Otherwise it will show current seasonal manga.

If you want to see all available seasons, 
type `list` in `<season>` argument

```shell
mangadex-dl "seasonal:list"
```

```{note}
Current seasonal manga is retrieved from 
https://github.com/mansuf/mangadex-downloader/blob/main/seasonal_manga_now.txt. 
If you think this is out of update, 
please open a issue [here](https://github.com/mansuf/mangadex-downloader/issues)
```

## Example usage

Get current seasonal manga

```shell
mangadex-dl "seasonal"
```

Get `Seasonal: Fall 2020` manga

```shell
mangadex-dl "seasonal:fall 2020"
```

Get all available seasons

```shell
mangadex-dl "seasonal:list"
```