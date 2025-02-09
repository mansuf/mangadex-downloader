# Migration guide from v2 to v3

Here's list of things that you should know before start using v3

## `--path` option become absolute path and support placeholders

In v2 or lower, if you set `--path` with value `mymanga/some_kawaii_manga`. 
The manga and the chapters will be stored under directory `mymanga/some_kawaii_manga/NameOfTheManga`.

```sh
mangadex-dl "URL" --path "mymanga/some_kawaii_manga"

# If you see download directory, you will see this:
📂mymanga
 ┗ 📂some_kawaii_manga
 ┃ ┗ 📂NameOfTheManga
 ┃ ┃ ┣ 📂Vol. 1 Ch. 1
 ┃ ┃ ┃ ┣ 📜00.png
 ┃ ┃ ┃ ┣ 📜01.png
 ┃ ┃ ┃ ┗ 📜++.png
 ┃ ┃ ┣ 📜cover.jpg
 ┃ ┃ ┗ 📜download.db
```

Now, if you set `--path` with value `mymanga/some_kawaii_manga`. 
The manga and the chapters will be stored under directory `mymanga/some_kawaii_manga`.

```sh
mangadex-dl "URL" --path "mymanga/some_kawaii_manga"

# If you see download directory, you will see this:
📂mymanga
 ┗ 📂some_kawaii_manga
 ┃ ┣ 📂Vol. 1 Ch. 1
 ┃ ┃ ┣ 📜00.png
 ┃ ┃ ┣ 📜01.png
 ┃ ┃ ┗ 📜++.png
 ┃ ┣ 📜cover.jpg
 ┃ ┗ 📜download.db
```

If you comfortable with old behaviour, you can use placeholders

```sh
mangadex-dl "URL" --path "mymanga/some_kawaii_manga/{manga.title}"
```

See more placeholders in {doc}`./cli_ref/path_placeholders`

## `No volume` will get separated into chapters format

```{note}
This change only affect any `volume` formats, 
`chapters` and `single` formats doesn't get affected by this change
```

Now, if a manga that doesn’t have no volume, 
it will get separated (chapters format) rather than being merged into single file called No volume.cbz (example). 
However if you prefer old behaviour (merge no volume chapters into single file) you can use --create-no-volume.

For example:

### v2 and lower

```sh
mangadex-dl "URL" --save-as "raw-volume"

# If you see download directory, you will see this:
📂mymanga
 ┗ 📂some_spicy_manga
 ┃ ┣ 📂No Volume
 ┃ ┃ ┣ 📜00.png
 ┃ ┃ ┗ 📜24.png
 ┃ ┣ 📂Volume. 1
 ┃ ┃ ┣ 📜00.png
 ┃ ┃ ┗ 📜24.png
 ┃ ┣ 📜cover.jpg
 ┃ ┗ 📜download.db
```

### v3 and upper

```sh
mangadex-dl "URL" --save-as "raw-volume"

# If you see download directory, you will see this:
📂mymanga
 ┗ 📂some_spicy_manga
 ┃ ┣ 📂Chapter 1
 ┃ ┃ ┣ 📜00.png
 ┃ ┃ ┗ 📜24.png
 ┃ ┣ 📂Chapter 2
 ┃ ┃ ┣ 📜00.png
 ┃ ┃ ┗ 📜24.png
 ┃ ┣ 📂Volume. 1
 ┃ ┃ ┣ 📜00.png
 ┃ ┃ ┗ 📜24.png
 ┃ ┣ 📜cover.jpg
 ┃ ┗ 📜download.db
```

If you prefer old behaviour like v2 and lower, you can use `--create-no-volume`

```sh
mangadex-dl "URL" --save-as "raw-volume" --create-no-volume
```

## Dropped support for Python v3.8 and v3.9

Since Python v3.8 already reached End-of-life (EOL), 
i have no intention to continue developing it and Python 3.9 is almost reached End-of-life too.

Minimum Python version for installing mangadex-downloader is 3.10 and upper.
