# Filename customization

Starting v3.0.0, mangadex-downloader support customize filename based on your preference. 
Also it support placeholders !

## Available options

The usage is depends which format you're using.

- `--filename-chapter` for any chapter format (cbz, pdf, epub, etc)
- `--filename-volume` for any volume format (cbz-volume, pdf-volume, etc)
- `--filename-single` for any single format (cbz-single, pdf-single)

## Example usage

### Chapter format

```sh
mangadex-dl "URL" -f cbz --filename-chapter "{manga.title} Ch. {chapter.chapter}{file_ext}"
```

### Volume format

```sh
mangadex-dl "URL" -f cbz-volume --filename-volume "{manga.title} Vol. {chapter.volume}{file_ext}"
```

### Single format

```sh
mangadex-dl "URL" -f cbz-single --filename-single "{manga.title} All Chapters{file_ext}"
```
