# This was used to run mangadex-downloader for compiled app
# Because we cannot compile __main__.py directly (i don't know why, the errors are confusing)

from mangadex_downloader.__main__ import main

if __name__ == "__main__":
    main()