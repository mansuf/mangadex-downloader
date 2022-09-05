# Manga library command

Show all saved mangas from logged in user. You will be prompted to select which manga want to download.

```{note}
You must login in order to use this command. Otherwise it will not work.
```

## Syntax

```shell
mangadex-dl "library" --login
```

## Example usage

```shell
# User will be prompted to select which manga wants to download
# And then save it as pdf format
mangadex-dl "library" --login --save-as pdf
```

Output

```shell
=============================================
List of manga from user library "..."
=============================================
(1). ...
(2). ...
(3). ...
(4). ...
(5). ...
(6). ...
(7). ...
(8). ...
(9). ...

type "next" to show next results
type "previous" to show previous results
type "preview NUMBER" to show more details about selected result. For example: "preview 2"
=>
# ....
```