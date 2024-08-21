# mangadex-downloader

A command-line tool to download manga from [MangaDex](https://mangadex.org/), written in [Python](https://www.python.org/).

## Key features

- Download manga, cover manga, chapter, or list directly from MangaDex
- Download manga or list from user library
- Find and download MangaDex URLs from MangaDex forums ([https://forums.mangadex.org/](https://forums.mangadex.org/))
- Download manga in each chapters, each volumes, or wrap all chapters into single file
- Search (with filters) and download manga
- Filter chapters with scalantion groups or users
- Manga tags, groups, and users blacklist support
- Batch download support
- Authentication (with cache) support
- Control how many chapters and pages you want to download
- Multi languages support
- Legacy MangaDex url support
- Save as raw images, EPUB, PDF, Comic Book Archive (.cbz or .cb7)
- Respect API rate limit

## Getting started

- Installation: {doc}`installation`
- Basic usage: {doc}`./cli_usage/index`
- Advanced usage: {doc}`./cli_usage/advanced`

## Manuals

- Available formats: {doc}`./formats`
- CLI Options: {doc}`./cli_ref/cli_options`
- Commands: {doc}`./cli_ref/commands`

To see all available manuals, see {doc}`cli_ref/index`

```{toctree}
:maxdepth: 2
:hidden:

installation
formats
cli_usage/index
cli_usage/advanced/index
cli_ref/index
```

```{toctree}
:hidden:
:caption: Development

changelog
Github repository <https://github.com/mansuf/mangadex-downloader>
```
