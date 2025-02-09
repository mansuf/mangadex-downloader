# Download tracker

Everytime you download a manga, chapter or list. 
The application will write `download.db` file into manga folder. 
But what does it do ? does it dangerous ? the file seems suspicious.

Worry not, the file is not dangerous. It's called download tracker, 
it will track chapters and images everytime you download. 
So next time you run the application, it will check what chapters has been downloaded 
and if the application found chapters that has not been downloaded yet, 
the application will download them all.

Download tracker is designed to avoid rate-limit frequently from MangaDex API on some formats. 
Also it check latest chapters on any `volume` and `single` formats. 
So let's say you already downloaded `Volume 1`, but there is new chapter on `Volume 1`. 
The application will re-download `Volume 1`.

## Verify downloaded chapters and images

The download tracker can verify downloaded chapters and images on all formats. 
Previously, the application only verify images which only available to `raw` formats (raw, raw-volume, raw-single). 
With this, the application will know what chapters and images is corrupted or missing 
and will re-download the corrupted or missing chapters and images.

## Cool features, is there a way to turn it off ?

You can, use `--no-track` to turn off download tracker feature.

```sh
mangadex-dl "insert MangaDex URL here" --no-track
```