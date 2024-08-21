# MIT License

# Copyright (c) 2022-present Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import logging
import sys
from gettext import gettext

from .utils import dynamic_bars, setup_logging, print_version_info
from ..cover import valid_cover_types
from ..update import update_app
from ..utils import validate_group_url as _validate_group_url, valid_url_types
from ..language import get_language, Language
from ..format import formats
from ..config import config
from ..errors import InvalidURL
from ..network import Net
from .. import __description__
from ..forums import validate_forum_thread_url

log = logging.getLogger(__name__)


class ModifiedArgumentParser(argparse.ArgumentParser):
    """Modified :class:`argparse.ArgumentParser`

    The only thing modified is :meth:`argparse.ArgumentParser.error()` function.
    The function should not show whole usage, instead just show the error for simplicity.
    """

    def error(self, message):
        self.exit(2, f"Error: {gettext(message)}\n")


def validate_group_url(url):
    try:
        return _validate_group_url(url)
    except InvalidURL as e:
        raise argparse.ArgumentTypeError(e)


def validate_language(lang):
    try:
        return get_language(lang)
    except Exception as e:
        raise argparse.ArgumentTypeError(e)


class ListLanguagesAction(argparse.Action):
    def __call__(self, *args, **kwargs):
        text = "List of available languages"
        print(text)
        print(dynamic_bars(len(text)))

        for lang in Language:
            if lang == Language.Other:
                # Need special treatment
                continue

            print(f"{lang.name} / {lang.value}")

        # Value of Language.Other is None
        # And we don't want that to showed up in screen
        print(f"{Language.Other.name}")

        sys.exit(0)


class UpdateAppAction(argparse.Action):
    def __call__(self, *args, **kwargs):
        setup_logging("mangadex_downloader")
        update_app()
        sys.exit(0)


class PrintVersionAction(argparse.Action):
    def __call__(self, *args, **kwargs):
        print_version_info()
        sys.exit(0)


def get_args(argv):
    parser = ModifiedArgumentParser(description=__description__)
    parser.add_argument(
        "URL",
        help="MangaDex URL or a file containing MangaDex URLs. "
        "See https://mangadex-downloader.rtfd.io/en/latest/cli_ref/index.html#available-commands "  # noqa: E501
        "for available commands",
        nargs="?",
        default="",
    )
    parser.add_argument(
        "--type",
        "-t",
        help="Override type MangaDex url. By default, it auto detect given url",
        choices=valid_url_types,
    )
    parser.add_argument(
        "--replace", "-r", help="Replace manga if exist", action="store_true"
    )
    parser.add_argument(
        "--verbose",
        help="[DEPRECATED] Use `--log-level=DEBUG` instead. " "Enable verbose output",
        action="store_true",
    )
    parser.add_argument(
        "--filter",
        "-ft",
        help="Apply filter to search and random manga",
        action="append",
    )
    parser.add_argument(
        "--download-mode",
        "-dm",
        help="Set download mode, you can set to 'default' or 'unread'. "
        "If you set to 'unread', the app will download unread chapters only "
        "(require authentication). If you set to 'default' "
        "the app will download all chapters",
        choices=("default", "unread"),
        default=config.download_mode,
    )

    # Path related
    path_group = parser.add_argument_group("Path")
    path_group.add_argument(
        "--path",
        "--folder",
        "-d",
        metavar="DIRECTORY",
        help="Store manga / chapter to specified directory. "
        "this option support placeholders, "
        "read https://mangadex-dl.mansuf.link/en/stable/cli_ref/path_placeholders.html for more info",
        default=config.path,
    )
    path_group.add_argument(
        "--filename-single",
        "-fs",
        help=(
            "Set filename for single format, "
            "read https://mangadex-dl.mansuf.link/en/stable/cli_ref/path_placeholders.html for more info"
        ),
        default=config.filename_single,
    )
    path_group.add_argument(
        "--filename-volume",
        "-fv",
        help=(
            "Set filename for volume format, "
            "read https://mangadex-dl.mansuf.link/en/stable/cli_ref/path_placeholders.html for more info"
        ),
        default=config.filename_volume,
    )
    path_group.add_argument(
        "--filename-chapter",
        "-fc",
        help=(
            "Set filename for chapter format, "
            "read https://mangadex-dl.mansuf.link/en/stable/cli_ref/path_placeholders.html for more info"
        ),
        default=config.filename_chapter,
    )

    # Search related
    search_group = parser.add_argument_group("Search")
    search_group.add_argument(
        "--search", "-s", help="Search manga and then download it", action="store_true"
    )

    # Manga related
    manga_group = parser.add_argument_group("Manga")
    manga_group.add_argument(
        "--use-alt-details",
        "-uad",
        action="store_true",
        help="Use alternative title and description manga",
    )
    manga_group.add_argument(
        "--create-manga-info",
        "-cmi",
        action="store_true",
        help="Store manga information such as title, authors, artists, description, and tags "
        "in a file called 'manga_info.csv'. By default this file will save to csv format you can change this in "
        "--manga-info-format",
        default=config.create_manga_info,
    )
    manga_group.add_argument(
        "--manga-info-format",
        "-mif",
        help="Change file format for manga information file (manga_info.csv)",
        choices=("csv", "json"),
        default=config.manga_info_format,
    )
    manga_group.add_argument(
        "--manga-info-filepath",
        "-mip",
        help="Change file location to store manga information. Default to './manga_info.{manga_info_format}'",
        default=config.manga_info_filepath,
    )

    # Group related
    group_group = parser.add_argument_group("Group")  # wtf group_group
    group_group.add_argument(
        "--group",
        "-g",
        metavar="GROUP_ID",
        type=validate_group_url,
        help="Filter each chapter with different scanlation group. "
        "Filter with user also supported.",
        action="append",
    )

    # Language related
    lang_group = parser.add_argument_group("Language")
    lang_group.add_argument(
        "-lang",
        "--language",
        metavar="LANGUAGE",
        help="Download manga in given language, "
        "to see all languages, use --list-languages option",
        type=validate_language,
        default=config.language,
    )
    lang_group.add_argument(
        "--list-languages",
        "-ll",
        action=ListLanguagesAction,
        help="List all available languages",
        nargs=0,
    )
    lang_group.add_argument(
        "-vcl",
        "--volume-cover-language",
        help="Override volume cover language. "
        "If this option is not set, it will follow --language option",
        type=validate_language,
        default=config.volume_cover_language,
    )

    # Volume related
    vol_group = parser.add_argument_group("Volume")
    vol_group.add_argument(
        "--start-volume",
        "-sv",
        type=float,
        help="Start download chapter from given volume number",
        metavar="VOLUME",
    )
    vol_group.add_argument(
        "--end-volume",
        "-ev",
        type=float,
        help="Stop download chapter from given volume number",
        metavar="VOLUME",
    )

    # Chapter related
    chap_group = parser.add_argument_group("Chapter")
    chap_group.add_argument(
        "--start-chapter",
        "-sc",
        type=float,
        help="Start download chapter from given chapter number",
        metavar="CHAPTER",
    )
    chap_group.add_argument(
        "--end-chapter",
        "-ec",
        type=float,
        help="Stop download chapter from given chapter number",
        metavar="CHAPTER",
    )
    chap_group.add_argument(
        "--no-oneshot-chapter",
        "-noc",
        help="If manga has oneshot chapter, it will be ignored.",
        action="store_true",
    )
    chap_group.add_argument(
        "--no-group-name",
        "-ngn",
        action="store_true",
        help="Do not use scanlation group name for each chapter",
        default=config.no_group_name,
    )
    chap_group.add_argument(
        "--use-chapter-title",
        "-uct",
        action="store_true",
        help="Use chapter title for each chapters. "
        "NOTE: This option is useless if used with any single and volume format.",
        default=config.use_chapter_title,
    )
    chap_group.add_argument(
        "--range",
        "-rg",
        help="[DISABLED] A range pattern to download specific chapters",
    )
    chap_group.add_argument(
        "--sort-by",
        help='Download sorting method, by default it\'s selected to "volume"',
        default=config.sort_by,
    ),
    chap_group.add_argument(
        "--use-chapter-cover",
        "-ucc",
        action="store_true",
        help="Enable creation of chapter info (cover) for any single or volume formats. "
        "See https://mangadex-dl.mansuf.link/en/stable/cli_ref/chapter_info.html for more info. "  # noqa: E501
        "NOTE: chapter info creation are not enabled "
        "if you are using any chapter format (cbz, pdf, raw, etc)",
        default=config.use_chapter_cover,
    )
    chap_group.add_argument(
        "--use-volume-cover",
        "-uvc",
        action="store_true",
        help="Enable creation of volume cover for any volume formats. "
        "Volume cover will be placed in first page in each volume files. "
        "NOTE: Volume cover will be not created in chapter "
        "(cbz, pdf, raw, etc) and single formats",
        default=config.use_volume_cover,
    )
    chap_group.add_argument(
        "--ignore-missing-chapters",
        "-imc",
        action="store_true",
        help="Ignore missing downloaded chapters. "
        "This will prevent the application to re-download the missing chapters.",
        default=config.ignore_missing_chapters,
    )
    chap_group.add_argument(
        "--create-no-volume",
        "-cnv",
        action="store_true",
        help="Merge all chapters that has no volume into 1 file for 'volume' format. ",
        default=config.create_no_volume,
    )

    # Chapter page related
    chap_page_group = parser.add_argument_group("Chapter Page")
    chap_page_group.add_argument(
        "--start-page",
        "-sp",
        type=int,
        help="Start download chapter page from given page number",
        metavar="NUM_PAGE",
    )
    chap_page_group.add_argument(
        "--end-page",
        "-ep",
        type=int,
        help="Stop download chapter page from given page number",
        metavar="NUM_PAGE",
    )

    # Images related
    img_group = parser.add_argument_group("Images")
    img_group.add_argument(
        "--use-compressed-image",
        "-uci",
        help="Use low size images manga (compressed quality)",
        action="store_true",
        default=config.use_compressed_image,
    )
    img_group.add_argument(
        "--cover",
        "-c",
        choices=valid_cover_types,
        help='Choose quality cover, default is "original"',
        default=config.cover,
    )

    # Authentication related
    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument(
        "--login", "-l", help="Login to MangaDex", action="store_true"
    )
    auth_group.add_argument(
        "--login-method",
        "-lm",
        help="Set authentication method for MangaDex, by default it set to `legacy`. "
        "Which is directly input (username or email) and password to the application",
        choices=Net.available_auth_cls.keys(),
        default=Net.default_auth_method,
    )
    auth_group.add_argument(
        "--login-username",
        "-lu",
        metavar="USERNAME",
        help="Login to MangaDex with username or email "
        "(you will be prompted to input password if --login-password are not present)",
    )
    auth_group.add_argument(
        "--login-password",
        "-lp",
        metavar="PASSWORD",
        help="Login to MangaDex with password "
        "(you will be prompted to input username if --login-username are not present)",
    )
    auth_group.add_argument(
        "--login-api-id",
        "-lai",
        metavar="API_CLIENT_ID",
        help="Login to MangaDex with API Client. "
        "This option is working if you use 'oauth2' login method (--login-method oauth2). "
        "Also you will be prompted to input API client secret if --login-api-secret are not present",
    )
    auth_group.add_argument(
        "--login-api-secret",
        "-las",
        metavar="API_CLIENT_SECRET",
        help="Login to MangaDex with API Client. "
        "This option is working if you use 'oauth2' login method (--login-method oauth2). "
        "Also you will be prompted to input API client id if --login-api-id are not present",
    )
    auth_group.add_argument(
        "--login-cache",
        "-lc",
        action="store_true",
        help="Cache authentication token. "
        "You don't have to re-login with this option. "
        "You must set MANGADEXDL_CONFIG_ENABLED=1 "
        "in your environment variables before doing this, "
        "otherwise the app will throwing error. "
        "NOTE: Using this option can cause an attacker "
        "in your computer may grab your authentication cache "
        "and using it for malicious actions. USE IT WITH CAUTION !!!",
        default=config.login_cache,
    )

    # Save as format
    save_as_group = parser.add_argument_group("Save as format")
    save_as_group.add_argument(
        "--save-as",
        "-f",
        choices=formats.keys(),
        help="Select save as format, default to `raw`",
        default=config.save_as,
    )

    # Network related
    network_group = parser.add_argument_group("Network")
    network_group.add_argument(
        "--proxy", "-p", metavar="SOCKS / HTTP Proxy", help="Set http/socks proxy"
    )
    network_group.add_argument(
        "--proxy-env",
        "-pe",
        action="store_true",
        help="use http/socks proxy from environments",
    )
    network_group.add_argument(
        "--force-https",
        "-fh",
        action="store_true",
        help="Force download images in standard HTTPS port 443",
        default=config.force_https,
    )
    network_group.add_argument(
        "--delay-requests",
        "-dr",
        help="Set delay for each requests send to MangaDex server",
        type=float,
        metavar="TIME_IN_SECONDS",
    )
    network_group.add_argument(
        "--dns-over-https",
        "-doh",
        help="Enable DNS-over-HTTPS (DoH)",
        metavar="PROVIDER",
    )
    network_group.add_argument(
        "--timeout",
        help="Set timeout for each HTTPS(s) requests",
        metavar="TIME_IN_SECONDS",
        type=float,
    )
    network_group.add_argument(
        "--http-retries",
        help="Set HTTP retries, use this if you want to set how much to retries "
        "if the app failed to send HTTP requests to MangaDex API. "
        'Value must be numbers or "unlimited", by default it set to 5',
        metavar="NUMBERS_OR_UNLIMITED",
        default=config.http_retries,
    )

    # Miscellaneous
    misc_group = parser.add_argument_group("Miscellaneous")
    misc_group.add_argument(
        "--input-pos",
        help="Automatically select choices in selectable prompt "
        "(list, library, followed-list command)",
    )
    misc_group.add_argument(
        "-pipe", action="store_true", help="Download from pipe input"
    )
    misc_group.add_argument(
        "-v",
        "--version",
        action=PrintVersionAction,
        nargs=0,
        help="Print mangadex-downloader version",
    )

    misc_group.add_argument(
        "--write-tachiyomi-info",
        "-wti",
        action="store_true",
        default=config.write_tachiyomi_info,
        help="Write manga details to tachiyomi `details.json` file",
    )
    misc_group.add_argument(
        "--no-track",
        action="store_true",
        default=config.no_track,
        help="Disable download tracking. "
        "NOTE: If you enable this, the application will not verify images and chapters. ",
    )
    misc_group.add_argument(
        "--no-metadata",
        action="store_true",
        default=config.no_metadata,
        help="Disable metadata creation (ComicInfo.xml) in any cbz format (cbz, cbz-volume, cbz-single)",
    )

    console_group = parser.add_argument_group("Console output")
    console_group.add_argument(
        "--log-level",
        default=config.log_level,
        help="Set logger level, available options: "
        "CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET. "
        "Default level is INFO",
        metavar="LEVEL",
    )
    console_group.add_argument(
        "--progress-bar-layout",
        "-pbl",
        default=config.progress_bar_layout,
        choices=["default", "stacked", "none"],
        help="Set progress bar layout, available options: "
        "default, stacked, none. "
        "Default layout is 'default'",
        metavar="LAYOUT",
    )
    console_group.add_argument(
        "--stacked-progress-bar-order",
        "-spb-order",
        default=config.stacked_progress_bar_order,
        help="Set stacked progress bar order, available options: "
        "volumes, chapters, pages, file sizes, convert. "
        "Multiple values is supported, separated by comma. "
        "Default order is 'volumes, chapters, pages, file sizes, convert'",
        metavar="ORDER",
    )
    console_group.add_argument(
        "--no-progress-bar",
        "-npb",
        action="store_true",
        default=config.no_progress_bar,
        help="[DEPRECATED] Use '--progress-bar-layout=none' instead. "
        "Disable progress bar when downloading or converting",
    )

    # Update application
    update_group = parser.add_argument_group("Update application")
    update_group.add_argument(
        "--update",
        help="Update mangadex-downloader to latest version",
        action=UpdateAppAction,
        nargs=0,
    )

    args = parser.parse_args(argv)

    ##########################
    #  Finalization Process  #
    ##########################

    urls: str = sys.stdin.read() if args.pipe else args.URL

    try:
        validate_forum_thread_url(urls)
        is_forum_thread = True
    except InvalidURL:
        is_forum_thread = False

    fetch_library_manga = urls.startswith("library")
    fetch_library_list = urls.startswith("list")
    fetch_library_follows_list = urls.startswith("followed-list")
    random = urls.startswith("random")
    group = urls.startswith("group")
    file = urls.startswith("file")
    seasonal = urls.startswith("seasonal")
    thread = is_forum_thread

    cover_art_512px = None
    cover_art_256px = None
    cover_art = None

    # Lifehack
    if urls.startswith("cover"):
        cover_art_512px = urls.startswith("cover-512px")
        cover_art_256px = urls.startswith("cover-256px")
        cover_art = not any([cover_art_256px, cover_art_512px])

    # TODO: Add extra checking for -pipe and --search options

    setattr(args, "URL", urls)
    setattr(args, "fetch_library_manga", fetch_library_manga)
    setattr(args, "fetch_library_list", fetch_library_list)
    setattr(args, "fetch_library_follows_list", fetch_library_follows_list)
    setattr(args, "random", random)
    setattr(args, "fetch_group", group)
    setattr(args, "file", file)
    setattr(args, "seasonal", seasonal)
    setattr(args, "thread", thread)
    setattr(args, "cover_art", cover_art)
    setattr(args, "cover_art_512px", cover_art_512px)
    setattr(args, "cover_art_256px", cover_art_256px)

    return parser, args
