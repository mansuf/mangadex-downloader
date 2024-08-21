# Download manga from scanlator group

You can download manga from your favorite scanlator groups !. Just type `group:<group-id>`, and then choose which manga you want to download.

```shell
# "Tonikaku scans" group
mangadex-dl "group:063cf1b0-9e25-495b-b234-296579a34496"
```

You can also give the full URL if you want to

```shell
mangadex-dl "group:https://mangadex.org/group/063cf1b0-9e25-495b-b234-296579a34496/tonikaku-scans?tab=titles"
```

This was equal to these command if you use search with filters

```shell
mangadex-dl -s -ft "group=063cf1b0-9e25-495b-b234-296579a34496"
```
