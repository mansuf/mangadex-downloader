# Followed list library command

Show all followed MangaDex lists from logged in user. You will be prompted to select which list want to download.

```{note}
You must login in order to use this command. Otherwise it will not work.
```

## Syntax

```shell
mangadex-dl "followed-list" --login
```

## Example usage

```shell
# User will be prompted to select which list wants to download
# And then save it as pdf format
mangadex-dl "followed-list" --login --save-as pdf
```

Output

```shell
===============================================
List of followed MDlist from user "..."
===============================================
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