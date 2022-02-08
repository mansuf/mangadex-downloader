Command Line Interface (CLI) Usage
===================================

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
- ``--replace``     Replace manga if exist
- ``--verbose``     Enable verbose output

.. note:: 

    You can download mangas from a file containing urls, see example below:

    urls.txt

    .. code-block::

        https://mangadex.org/title/aa6c76f7-5f5f-46b6-a800-911145f81b9b/sono-bisque-doll-wa-koi-o-suru
        https://mangadex.org/title/6e445564-d9a8-4862-bff1-f4d6be6dba2c/karakai-jouzu-no-takagi-san
        https://mangadex.org/title/30f3ac69-21b6-45ad-a110-d011b7aaadaa/tonikaku-kawaii
    
    Command

    .. code-block:: shell

        $ mangadex-dl "urls.txt"
        # ...

.. warning::

    If you specify invalid path to file that containing MangaDex urls, the app will see it as URL. 
    See example below

    .. code-block:: shell

        # Not valid path
        $ mangadex-dl "not-exist-lol/lmao.txt"
        # error: argument URL: Invalid MangaDex URL or manga id

        # valid path
        $ mangadex-dl "yes-it-exist/exist.txt"
        # ...

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

Images related
~~~~~~~~~~~~~~~
- ``--use-compressed-image`` Use compressed image for low size file

Authentication related
~~~~~~~~~~~~~~~~~~~~~~~

- ``--login``           Login to MangaDex
- ``--login-username USERNAME``  Login to MangaDex with username (you will be prompted to input password if --login-password are not present)'
- ``--login-password PASSWORD``  Login to MangaDex with password (you will be prompted to input username if --login-username are not present)

Example usage:

.. code-block:: shell

    $ mangadex-dl "https://mangadex.org/title/a96676e5-8ae2-425e-b549-7f15dd34a6d8/komi-san-wa-komyushou-desu" --login
    MangaDex username => "insert MangaDex username here"
    MangaDex password => "insert MangaDex password here"
    [INFO] Logging in to MangaDex
    [INFO] Logged in to MangaDex
    [INFO] Fetching manga a96676e5-8ae2-425e-b549-7f15dd34a6d8
    [INFO] Downloading cover manga Komi-san wa Komyushou Desu.
    ...

You can specify username and password without be prompted (less secure) ! using ``--login-username`` and ``--login-password``

.. code-block:: shell

    $ mangadex-dl "https://mangadex.org/title/a96676e5-8ae2-425e-b549-7f15dd34a6d8/komi-san-wa-komyushou-desu" --login --login-username "..." --login-password "..."
    [INFO] Logging in to MangaDex
    [INFO] Logged in to MangaDex
    [INFO] Fetching manga a96676e5-8ae2-425e-b549-7f15dd34a6d8
    [INFO] Downloading cover manga Komi-san wa Komyushou Desu.
    ...

Proxy related
~~~~~~~~~~~~~~

- ``--proxy`` Set HTTP / SOCKS proxy
- ``--proxy-env`` use HTTP / SOCKS proxy from environments

.. warning::

    If you specify ``--proxy`` with ``--proxy-env``, ``--proxy`` option will be ignored

Example usage:

.. code-block:: shell

    $ mangadex-dl "insert mangadex url here" --proxy "http://127.0.0.1"


Example usage from environments:

.. code-block:: shell

    # For Linux / Mac OS
    $ export http_proxy="http://127.0.0.1"
    $ export https_proxy="http://127.0.0.1"

    # For Windows
    $ set http_proxy=http://127.0.0.1
    $ set https_proxy=http://127.0.0.1

    $ mangadex-dl "insert mangadex url here" --proxy-env

Update app
~~~~~~~~~~~~

- ``--update`` Update mangadex-downloader to the latest version.