Command-Line Interface (CLI) reference
=======================================

App names
----------

There is few app names in mangadex-downloader:

- ``mangadex-dl``
- ``mangadex-downloader``

.. note::

    If none of above doesn't work use this

    .. code-block:: shell

        # For Windows
        py -3 -m mangadex_downloader

        # For Linux
        python3 -m mangadex_downloader

Options
--------

Global options
~~~~~~~~~~~~~~~

- ``URL``           MangaDex URL or a file containing MangaDex URLs
- ``--type {manga,list,chapter,legacy-manga,legacy-chapter}`` Override type MangaDex url. By default, it auto detect given url
- ``--replace``     Replace manga if exist
- ``--verbose``     Enable verbose output
- ``--search``      Search manga and then download it
- ``--unsafe``      Enable unsafe mode

Manga related
~~~~~~~~~~~~~~~

- ``--use-alt-details``     Use alternative title and description manga

Group related
~~~~~~~~~~~~~~
- ``--group GROUP_ID``      Use different scanlation group for each chapter.

Language related
~~~~~~~~~~~~~~~~~~

- ``--language LANGUAGE`` Download manga in given language, to see all languages, use --list-languages option
- ``--list-languages`` List all available languages

Folder related
~~~~~~~~~~~~~~~

- ``--folder FOLDER``      Store manga in given folder

Chapters related
~~~~~~~~~~~~~~~~~

- ``--start-chapter CHAPTER``       Start download manga from given chapter
- ``--end-chapter CHAPTER``         Stop download manga from given chapter
- ``--no-oneshot-chapter``  If exist, don't download oneshot chapter
- ``--no-group-name``       Do not use scanlation group name for each chapter
- ``--use-chapter-title``   Use chapter title for each chapters. NOTE: This option is useless if used with any single and volume format.

Chapter page related
~~~~~~~~~~~~~~~~~~~~~
- ``--start-page NUM_PAGE`` Start download chapter page from given page number
- ``--end-page NUM_PAGE``   Stop download chapter page from given page number

Images related
~~~~~~~~~~~~~~~
- ``--use-compressed-image`` Use compressed image for low size file
- ``--cover {original,512px,256px,none}`` Choose quality cover, default is "original". Choose ``none`` to not download cover manga

Save as format
~~~~~~~~~~~~~~~

- ``--save-as {raw,raw-volume,raw-single,tachiyomi,tachiyomi-zip,pdf,pdf-volume,pdf-single,cbz,cbz-volume,cbz-single}`` Choose save as format, default to "tachiyomi"

Authentication related
~~~~~~~~~~~~~~~~~~~~~~~

- ``--login``           Login to MangaDex
- ``--login-username USERNAME``  Login to MangaDex with username or email (you will be prompted to input password if ``--login-password`` are not present)'
- ``--login-password PASSWORD``  Login to MangaDex with password (you will be prompted to input username if ``--login-username`` are not present)

Proxy related
~~~~~~~~~~~~~~

- ``--proxy`` Set HTTP / SOCKS proxy
- ``--proxy-env`` use HTTP / SOCKS proxy from environments

Miscellaneous
~~~~~~~~~~~~~~
- ``-pipe``                    Download from pipe input
- ``--enable-legacy-sorting``  Enable legacy sorting chapter images for old reader application

Update app
~~~~~~~~~~~~

- ``--update`` Update mangadex-downloader to the latest version.