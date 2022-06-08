import argparse
import logging
import os
import sys

from .url import valid_types
from .utils import setup_logging, sys_argv, print_version_info
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
from .. import __description__, __version__

log = logging.getLogger(__name__)

def _check_args(opts, args):
    """Utility for checking args from original and alias options
    
    Used in :class:`InputHandler`
    """
    for opt in opts:
        if opt not in args:
            continue
        else:
            # original or alias options is exist in args
            return True
    
    # not exist
    return False

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

class PrintVersionAction(argparse.Action):
    def __call__(self, *args, **kwargs):
        print_version_info()
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

        self.search = _check_args(
            (
                '--search',
                '-s'
            ),
            lowered_args
        )
        self.unsafe = _check_args(
            (
                '--unsafe',
                '-u'
            ),
            lowered_args
        )
        self.use_alt_details = _check_args(
            (
                '--use-alt-details',
                '-uad'
            ),
            lowered_args
        )

        # Manipulate positional arguments
        if pipe:
            sys_argv.append(pipe_value)

        self.pipe = pipe
        self.pipe_value = pipe_value

    def __call__(self, parser, namespace, values, option_string=None):
        urls = self.pipe_value if self.pipe else values

        file_exist = False
        if os.path.exists(urls):
            file_exist = True

        fetch_library_manga = urls.startswith('library')
        fetch_library_list = urls.startswith('list')
        fetch_library_follows_list = urls.startswith('followed-list')
        file = urls.startswith('file')

        if self.pipe and self.search:
            parser.error("search with pipe input are not supported")
        elif self.pipe and self.use_alt_details:
            parser.error("--use-alt-details with -pipe are not supported")
        elif self.pipe and fetch_library_manga:
            parser.error("-pipe are not supported when fetching user library manga")
        elif self.search and fetch_library_manga:
            parser.error("--search are not supported when fetching user library manga")
        elif self.pipe and fetch_library_list:
            parser.error("-pipe are not supported when fetching user library list")
        elif self.search and fetch_library_list:
            parser.error("--search are not supported when fetching user library list")
        elif self.pipe and fetch_library_follows_list:
            parser.error("-pipe are not supported when fetching user library followed list")
        elif self.search and fetch_library_follows_list:
            parser.error("--search are not supported when fetching user library followed list")
        elif self.search and file_exist:
            parser.error("--search are not supported when used for batch downloading")


        if fetch_library_manga:
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
        setattr(namespace, 'fetch_library_manga', fetch_library_manga)
        setattr(namespace, 'fetch_library_list', fetch_library_list)
        setattr(
            namespace,
            'fetch_library_follows_list',
            fetch_library_follows_list
        )
        setattr(namespace, 'file', file)

def get_args(argv):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        'URL',
        action=InputHandler,
        help='MangaDex URL or a file containing MangaDex URLs. ' \
             'Type `library:<status>` to download manga from logged in user library, ' \
             'if <status> is provided, it will fetch all mangas with given reading status, ' \
             'if not, then it will fetch all mangas from logged in user. ' \
             'Type `list:<user_id>` to download MangaDex list user, ' \
             'if <user_id> is provided it will download public list, ' \
             'if not, then it will download from public and private list from logged in user. ' \
             'Type `followed-list` to download followed MangaDex list from logged in user ' \
    )
    parser.add_argument(
        '--type',
        '-t',
        help='Override type MangaDex url. By default, it auto detect given url',
        choices=valid_types
    )
    parser.add_argument(
        '--folder',
        '--path',
        '-d',
        metavar='FOLDER',
        help='Store manga in given folder'
    )
    parser.add_argument(
        '--replace',
        '-r',
        help='Replace manga if exist',
        action='store_true'
    )
    parser.add_argument('--verbose', help='Enable verbose output', action='store_true')
    parser.add_argument(
        '--search',
        '-s',
        help='Search manga and then download it',
        action='store_true'
    )
    parser.add_argument(
        '--unsafe',
        '-u',
        help='If set, it will allow you to search and download porn manga', 
        action='store_true'
    )

    # Manga related
    manga_group = parser.add_argument_group('Manga')
    manga_group.add_argument(
        '--use-alt-details',
        '-uad',
        action='store_true',
        help='Use alternative title and description manga'
    )

    # Group related
    group_group = parser.add_argument_group('Group') # wtf group_group
    group_group.add_argument(
        '--group',
        '-g',
        metavar='GROUP_ID',
        type=validate_group_url,
        help='Filter each chapter with different scanlation group. ' \
             'Filter with user also supported.'
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
        '-ll',
        action='version',
        help='List all available languages',
        version=list_languages()
    )

    # Chapter related
    chap_group = parser.add_argument_group('Chapter')
    chap_group.add_argument(
        '--start-chapter',
        '-sc',
        type=float,
        help='Start download chapter from given chapter number',
        metavar='CHAPTER'
    )
    chap_group.add_argument(
        '--end-chapter',
        '-ec',
        type=float,
        help='Stop download chapter from given chapter number',
        metavar='CHAPTER'
    )
    chap_group.add_argument(
        '--no-oneshot-chapter',
        '-noc',
        help='If manga has oneshot chapter, it will be ignored.',
        action='store_true'
    )
    chap_group.add_argument(
        '--no-group-name',
        '-ngn',
        action='store_true',
        help='Do not use scanlation group name for each chapter'
    )
    chap_group.add_argument(
        '--use-chapter-title',
        '-uct',
        action='store_true',
        help='Use chapter title for each chapters. ' \
             'NOTE: This option is useless if used with any single and volume format.'
    ) 

    # Chapter page related
    chap_page_group = parser.add_argument_group("Chapter Page")
    chap_page_group.add_argument(
        '--start-page',
        '-sp',
        type=int,
        help='Start download chapter page from given page number',
        metavar='NUM_PAGE'
    )
    chap_page_group.add_argument(
        '--end-page',
        '-ep',
        type=int,
        help='Stop download chapter page from given page number',
        metavar='NUM_PAGE'
    )

    # Images related
    img_group = parser.add_argument_group('Images')
    img_group.add_argument(
        '--use-compressed-image',
        '-uci',
        help='Use low size images manga (compressed quality)',
        action='store_true'
    )
    img_group.add_argument(
        '--cover',
        '-c',
        choices=valid_cover_types,
        help='Choose quality cover, default is \"original\"',
        default=default_cover_type
    )

    # Authentication related
    auth_group = parser.add_argument_group('Authentication')
    auth_group.add_argument('--login', '-l', help='Login to MangaDex', action='store_true')
    auth_group.add_argument(
        '--login-username',
        '-lu',
        metavar='USERNAME',
        help='Login to MangaDex with username or email ' \
             '(you will be prompted to input password if --login-password are not present)'
    )
    auth_group.add_argument(
        '--login-password',
        '-lp',
        metavar='PASSWORD',
        help='Login to MangaDex with password ' \
             '(you will be prompted to input username if --login-username are not present)'
    )

    # Save as format
    save_as_group = parser.add_argument_group('Save as format')
    save_as_group.add_argument(
        '--save-as',
        '-f',
        choices=formats.keys(),
        help='Select save as format, default to `raw`',
        default=default_save_as_format
    )

    # Proxy related
    proxy_group = parser.add_argument_group('Proxy')
    proxy_group.add_argument('--proxy', '-p', metavar='SOCKS / HTTP Proxy', help='Set http/socks proxy')
    proxy_group.add_argument(
        '--proxy-env',
        '-pe',
        action='store_true',
        help='use http/socks proxy from environments'
    )

    # Miscellaneous
    misc_group = parser.add_argument_group('Miscellaneous')
    misc_group.add_argument('-pipe', action='store_true', help="Download from pipe input")
    misc_group.add_argument(
        '--enable-legacy-sorting',
        action='store_true',
        help='[DEPRECATED] will be removed in v1.3.0. ' \
             'Does nothing. In previous version this option is used to enable legacy sorting. ' \
             'Which rename all images with numbers leading zeros (example: 001.jpg)'
    )
    misc_group.add_argument(
        '--no-verify',
        '-nv',
        action='store_true',
        help='Skip hash checking for each images'
    )
    misc_group.add_argument(
        '-v',
        '--version',
        action=PrintVersionAction,
        nargs=0,
        help='Print mangadex-downloader version'
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