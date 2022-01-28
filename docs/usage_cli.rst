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

- ``URL``           MangaDex URL
- ``--replace``     Replace manga if exist
- ``--verbose``     Enable verbose output

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