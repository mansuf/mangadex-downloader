# Ignore missing chapters

You want to perform update manga after moving downloaded chapters 
to another place but mangadex-downloader keeps downloading the missing chapters. 
How to avoid this ?

Worry not the `--ignore-missing-chapters` is your option.

Simple add `--ignore-missing-chapters` to the CLI arguments and the missing chapters
won't be downloaded anymore

```{warning}
This option cannot be used with `--no-track` option
```

Example usage:

```sh
# We try to perform clean download
# Meaning that, the manga is not downloaded yet
mangadex-dl "insert URL here" -f cbz 

# After that the manga is downloaded.
# And you moving the chapters to somewhere else
# and now the downloaded chapters are gone moved to another place
...

# If you want to update it,
# but do not want to re-download the missing chapters
# simply add --ignore-missing-chapters option
mangadex-dl "The same URL you downloaded" -f cbz --ignore-missing-chapters
```

And done, the missing chapters won't be downloaded anymore.
