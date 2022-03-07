import argparse
import os
import logging
import sys

from .url import smart_select_url, valid_types
from .utils import setup_logging
from ..update import update_app
from ..utils import (
    get_language,
    Language,
    valid_cover_types,
    default_cover_type
)
from ..format import formats, default_save_as_format
from ..errors import InvalidURL
from .. import __description__

log = logging.getLogger(__name__)

def _validate(url):
    try:
        _url = smart_select_url(url)
    except InvalidURL as e:
        raise argparse.ArgumentTypeError(str(e))
    return _url

def validate_url(url):
    if os.path.exists(url):
        with open(url, 'r') as opener:
            return [_validate(url) for i in opener.read().splitlines()]
    else:
        return [_validate(url)]

def validate_language(lang):
    try:
        return get_language(lang)
    except Exception as e:
        raise argparse.ArgumentTypeError(str(e))

def list_languages():
    text = ""
    for lang in Language:
        text += "%s = %s; " % (lang.name, lang.value)
    return text

class UpdateAppAction(argparse.Action):
    def __call__(self, *args, **kwargs):
        setup_logging('mangadex_downloader')
        update_app()
        sys.exit(0)

def get_args(argv):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('URL', type=validate_url, help='MangaDex URL or a file containing MangaDex URLs')
    parser.add_argument(
        '--type',
        help='Override type MangaDex url. By default, it auto detect given url',
        choices=valid_types
    )
    parser.add_argument('--folder', metavar='FOLDER', help='Store manga in given folder')
    parser.add_argument('--replace', help='Replace manga if exist', action='store_true')
    parser.add_argument('--verbose', help='Enable verbose output', action='store_true')

    # Language related
    lang_group = parser.add_argument_group('Language')
    lang_group.add_argument(
        '--language',
        metavar='LANGUAGE',
        help='Download manga in given language, to see all languages, use --list-languages option',
        type=validate_language,
        default=Language.English
    )
    lang_group.add_argument(
        '--list-languages',
        action='version',
        help='List all available languages',
        version=list_languages()
    )

    # Chapter related
    chap_group = parser.add_argument_group('Chapter')
    chap_group.add_argument(
        '--start-chapter',
        type=float,
        help='Start download chapter from given chapter number',
        metavar='CHAPTER'
    )
    chap_group.add_argument(
        '--end-chapter',
        type=float,
        help='Stop download chapter from given chapter number',
        metavar='CHAPTER'
    )
    chap_group.add_argument('--no-oneshot-chapter', help='If exist, don\'t download oneshot chapter', action='store_true')

    # Chapter page related
    chap_page_group = parser.add_argument_group("Chapter Page")
    chap_page_group.add_argument(
        '--start-page',
        type=int,
        help='Start download chapter page from given page number',
        metavar='NUM_PAGE'
    )
    chap_page_group.add_argument(
        '--end-page',
        type=int,
        help='Stop download chapter page from given page number',
        metavar='NUM_PAGE'
    )

    # Images related
    img_group = parser.add_argument_group('Images')
    img_group.add_argument('--use-compressed-image', help='Use low size images manga (compressed quality)', action='store_true')
    img_group.add_argument(
        '--cover',
        choices=valid_cover_types,
        help='Choose quality cover, default is \"original\"',
        default=default_cover_type
    )

    # Authentication related
    auth_group = parser.add_argument_group('Authentication')
    auth_group.add_argument('--login', help='Login to MangaDex', action='store_true')
    auth_group.add_argument(
        '--login-username',
        help='Login to MangaDex with username (you will be prompted to input password if --login-password are not present)',
        metavar='USERNAME'
    )
    auth_group.add_argument(
        '--login-password',
        help='Login to MangaDex with password (you will be prompted to input username if --login-username are not present)',
        metavar='PASSWORD'
    )

    # Save as format
    save_as_group = parser.add_argument_group('Save as format')
    save_as_group.add_argument(
        '--save-as',
        choices=formats.keys(),
        help='Select save as format, default to \"tachiyomi\"',
        default=default_save_as_format
    )

    # Proxy related
    proxy_group = parser.add_argument_group('Proxy')
    proxy_group.add_argument('--proxy', metavar='SOCKS / HTTP Proxy', help='Set http/socks proxy')
    proxy_group.add_argument('--proxy-env', action='store_true', help='use http/socks proxy from environments')

    # Update application
    update_group = parser.add_argument_group('Update application')
    update_group.add_argument(
        '--update',
        help='Update mangadex-downloader to latest version',
        action=UpdateAppAction,
        nargs=0
    )

    return parser.parse_args(argv)