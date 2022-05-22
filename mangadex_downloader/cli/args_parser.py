import argparse
import logging
import sys

from .url import valid_types
from .utils import setup_logging, sys_argv
from ..iterator import IteratorUserLibraryManga
from ..update import update_app
from ..utils import (
    valid_cover_types,
    default_cover_type,
    validate_group_url as _validate_group_url,
)
from ..language import get_language, Language
from ..format import formats, default_save_as_format
from ..errors import InvalidURL
from .. import __description__

log = logging.getLogger(__name__)

def validate_group_url(url):
    try:
        return _validate_group_url(url)
    except InvalidURL as e:
        raise argparse.ArgumentTypeError(str(e))

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

class InputHandler(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):
        super().__init__(
            option_strings,
            dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar
        )
        # Get url from pipe input
        lowered_args = [i.lower() for i in sys_argv]
        if '-pipe' in lowered_args:
            pipe = True
            pipe_value = sys.stdin.read()
        else:
            pipe = False
            pipe_value = None

        self.search = '--search' in lowered_args
        self.unsafe = '--unsafe' in lowered_args
        self.use_alt_details = '--use-alt-details' in lowered_args

        # Manipulate positional arguments
        if pipe:
            sys_argv.append(pipe_value)

        self.pipe = pipe
        self.pipe_value = pipe_value

    def __call__(self, parser, namespace, values, option_string=None):
        urls = self.pipe_value if self.pipe else values

        fetch_library = urls.startswith('library')

        if self.pipe and self.search:
            parser.error("search with pipe input are not supported")
        elif self.pipe and self.use_alt_details:
            parser.error("--use-alt-details with -pipe are not supported")
        elif self.pipe and fetch_library:
            parser.error("-pipe are not supported when fetching user library manga")
        elif self.search and fetch_library:
            parser.error("--search are not supported when fetching user library manga")

        if fetch_library:
            result = urls.split(':')
            
            # Try to get filter status
            try:
                status = result[1]
            except IndexError:
                status = None
            else:
                status = status.strip()
            
            if status == 'help':
                text = "List of statuses filter for user library manga"

                # Build dynamic bar
                bars = ""
                for _ in text:
                    bars += "="

                print(bars)
                print(text)
                print(bars)
                for item in IteratorUserLibraryManga.statuses:
                    print(item)
                sys.exit(0)

            if status is not None and status not in IteratorUserLibraryManga.statuses:
                err = str(set(IteratorUserLibraryManga.statuses)).replace('\'', '')
                parser.error(f"{status} are not valid status, choices are {err}")

        setattr(namespace, self.dest, urls)
        setattr(namespace, 'fetch_library', fetch_library)

def get_args(argv):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        'URL',
        action=InputHandler,
        help='MangaDex URL or a file containing MangaDex URLs',
    )
    parser.add_argument(
        '--type',
        help='Override type MangaDex url. By default, it auto detect given url',
        choices=valid_types
    )
    parser.add_argument('--folder', metavar='FOLDER', help='Store manga in given folder')
    parser.add_argument('--replace', help='Replace manga if exist', action='store_true')
    parser.add_argument('--verbose', help='Enable verbose output', action='store_true')
    parser.add_argument('--search', help='Search manga and then download it', action='store_true')
    parser.add_argument('--unsafe', help='If set, it will allow you to search and download porn manga', action='store_true')

    # Manga related
    manga_group = parser.add_argument_group('Manga')
    manga_group.add_argument(
        '--use-alt-details',
        action='store_true',
        help='Use alternative title and description manga'
    )

    # Group related
    group_group = parser.add_argument_group('Group') # wtf group_group
    group_group.add_argument(
        '--group',
        metavar='GROUP_ID',
        help='Use different scanlation group for each chapter',
        type=validate_group_url
    )

    # Language related
    lang_group = parser.add_argument_group('Language')
    lang_group.add_argument(
        '-lang',
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
    chap_group.add_argument('--no-group-name', action='store_true', help='Do not use scanlation group name for each chapter')
    chap_group.add_argument(
        '--use-chapter-title',
        action='store_true',
        help='Use chapter title for each chapters. NOTE: This option is useless if used with any single and volume format.'
    ) 

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
        help='Login to MangaDex with username or email (you will be prompted to input password if --login-password are not present)',
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

    # Miscellaneous
    misc_group = parser.add_argument_group('Miscellaneous')
    misc_group.add_argument('-pipe', action='store_true', help="Download from pipe input")
    misc_group.add_argument(
        '--enable-legacy-sorting',
        action='store_true',
        help='Enable legacy sorting chapter images for old reader application'
    )
    misc_group.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip hash checking for each images'
    )

    # Update application
    update_group = parser.add_argument_group('Update application')
    update_group.add_argument(
        '--update',
        help='Update mangadex-downloader to latest version',
        action=UpdateAppAction,
        nargs=0
    )

    args = parser.parse_args(argv)

    return parser, args