import argparse
import logging
import sys
from pathlib import Path

from .url import valid_types
from .utils import dynamic_bars, setup_logging, sys_argv, print_version_info
from .config import build_config_from_url_arg
from ..cover import valid_cover_types, default_cover_type
from ..iterator import IteratorUserLibraryManga
from ..update import update_app
from ..utils import validate_group_url as _validate_group_url, validate_url
from ..language import get_language, Language
from ..format import formats, default_save_as_format
from ..config import config
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

        # An monkey patch to determine if positional arguments is empty or no
        _store_true_args = [
            '--replace',
            '-r',
            '--verbose',
            '--unsafe',
            '-u',
            '--search',
            '-s',
            '--use-alt-details',
            '-uad',
            '--list-languages',
            '-ll',
            '--no-oneshot-chapter',
            '-noc',
            '--no-group-name',
            '-ngn',
            '--use-chapter-title',
            '-uct',
            '--use-compressed-image',
            '-uci',
            '--login',
            '-l',
            '--login-cache',
            '-lc',
            '-pipe',
            '--no-verify',
            '-nv',
            '--version',
            '-v',
            '--update',
            '--force-https',
            '-fh'
        ]

        # positional arguments
        pos_arg = False
        pos_value = None
        pos = 0
        while True:
            try:
                argv = sys_argv[pos]
            except IndexError:
                break
            
            if argv.startswith('-'):
                # Try to find value option
                try:
                    next_arg = sys_argv[pos + 1]
                except IndexError:
                    pass
                else:
                    if not next_arg.startswith('-') and argv not in _store_true_args:
                        # We assume this as value of another option
                        pos += 1
                        pass
                
                pos += 1
                continue
            
            pos_arg = True
            pos_value = argv
            break

        # If positional exist and pipe is true
        # remove it
        # ONLY if -pipe is exist
        if pos_arg and pipe:
            sys_argv.remove(pos_value)

        # Manipulate positional arguments
        if pipe:
            sys_argv.append(pipe_value)

        # Allow to search with empty keyword
        self.empty_search = not pos_arg and self.search
        if self.empty_search:
            sys_argv.append("dummy_empty_search")
        
        self.pipe = pipe
        self.pipe_value = pipe_value

    def __call__(self, parser, namespace, values, option_string=None):
        urls = self.pipe_value if self.pipe else values

        file_exist = False
        file_path = Path(urls)
        if file_path.exists() and file_path.is_file():
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

        setattr(namespace, self.dest, "" if self.empty_search else urls)
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
        '--unsafe',
        '-u',
        help='If set, it will allow you to search and download porn and erotica manga', 
        action='store_true',
        default=False
    )

    # Search related
    search_group = parser.add_argument_group('Search')
    search_group.add_argument(
        '--search',
        '-s',
        help='Search manga and then download it',
        action='store_true'
    )
    search_group.add_argument(
        '--search-filter',
        '-sf',
        help='Apply filter when searching manga',
        action='append'
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
        default=config.language
    )
    lang_group.add_argument(
        '--list-languages',
        '-ll',
        action=ListLanguagesAction,
        help='List all available languages',
        nargs=0
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
             'NOTE: This option is useless if used with any single and volume format.',
        default=config.use_chapter_title
    )
    chap_group.add_argument(
        '--range',
        '-rg',
        help='A range pattern to download specific chapters'
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
        action='store_true',
        default=config.use_compressed_image
    )
    img_group.add_argument(
        '--cover',
        '-c',
        choices=valid_cover_types,
        help='Choose quality cover, default is \"original\"',
        default=config.cover
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
    auth_group.add_argument(
        '--login-cache',
        '-lc',
        action='store_true',
        help='Cache authentication token. ' \
            'You don\'t have to re-login with this option. ' \
            'You must set MANGADEXDL_CONFIG_ENABLED=1 in your environment variables before doing this, ' \
            'otherwise the app will throwing error. ' \
            'NOTE: Using this option can cause an attacker in your computer may grab your authentication cache ' \
            'and using it for malicious actions. USE IT WITH CAUTION !!!',
        default=config.login_cache
    )

    # Save as format
    save_as_group = parser.add_argument_group('Save as format')
    save_as_group.add_argument(
        '--save-as',
        '-f',
        choices=formats.keys(),
        help='Select save as format, default to `raw`',
        default=config.save_as
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
    misc_group.add_argument(
        '--force-https',
        '-fh',
        action='store_true',
        help='Force download images in standard HTTPS port 443',
        default=config.force_https
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