# Scanlator group filtering

You can download chapters only from 1 scanlation group, by using `--group` option

```shell
# This will download all chapters from group "Tonikaku scans" only
mangadex-dl "https://mangadex.org/title/..." --group "https://mangadex.org/group/063cf1b0-9e25-495b-b234-296579a34496/tonikaku-scans"
```

You can download all same chapters with different groups, by using `--group` option with value "all"

```shell
# This will download all chapters, regardless of scanlation groups
mangadex-dl "https://mangadex.org/title/..." --group "all"
```

```{warning}
You cannot use `--group all` and `--no-group-name` together. It will throw error, if you're trying to do it
```

Also, you can use user as filter in `--group` option.

For example:

```shell
mangadex-dl "https://mangadex.org/title/..." --group "https://mangadex.org/user/..."
```
