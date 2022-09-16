# File command (batch download command)

Let's say you want to perform batch download and you have a file called "random"

```shell
mangadex-dl "random"
```

At this point, you will be doing random download not batch download. 
This is because `random` is reserved name in mangadex-downloader.

To prevent this from happening, you can use `file:<location>` command

```shell
mangadex-dl "file:random"
```

````{warning}
If you give invalid path, the app will throw an error.
See example below

```shell
# Not valid path
$ mangadex-dl "file:not-exist-lol/lmao.txt"
# error: argument URL: File "not-exist-lol/lmao.txt" is not exist

# valid path
$ mangadex-dl "file:yes-it-exist/exist.txt"
# ...
```
````

The command also support web location (http, https)

```{warning}
Make sure the inside contents is raw text and readable.
```

```shell
mangadex-dl "file:https://raw.githubusercontent.com/mansuf/md-test-urls/main/urls.txt"
```
