Embedding Usage
=================

Logging
--------

By default, mangadex-downloader not showing any output. 
It's because the library using logging module to handle the output.

If you want to see the output from mangadex-downloader library you need to create logging object, See example below.

.. code-block:: python3

    import logging

    # Creating log object
    log = logging.getLogger('mangadex_downloader')

    # Set level output
    log.setLevel(logging.INFO)

    # Uncomment this if you want to see debug output
    # log.setLevel(logging.DEBUG)

    # And finally add the stdout handler for the logging object
    log.addHandler(logging.StreamHandler())

Simple usage
-------------

.. code-block:: python3

    from mangadex_downloader import download

    # This will return Manga object
    manga = download("...")

    print(manga.title)


Advanced usage
---------------

.. code-block:: python3

    from mangadex_downloader import download

    # This will return Manga object
    manga = download(
        "insert MangaDex URL here",
        folder="Homework", # Store manga in "Homework" folder
        replace=True, # Replace manga if exist
        compressed_image=True, # Use compressed images for low size file
        start_chapter=5.0, # Start downloading from chapter 5
        end_chapter=10.0, # Stop downloading from chapter 10
        no_oneshot_chapter=True, # for those of you who hates oneshot :)
        language=Language.English # Download manga in english language
    )

Set up proxy
~~~~~~~~~~~~~

.. code-block:: python3

    from mangadex_downloader.network import Net, set_proxy, clear_proxy
    proxy = 'http://127.0.0.1'

    # Set up proxy
    Net.set_proxy(proxy)

    # Disable proxy
    Net.clear_proxy()

    # Shortcut
    set_proxy(proxy)
    clear_proxy()








