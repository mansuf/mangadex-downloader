import argparse
import os
import logging
import threading
import sys

from .url import build_URL_from_type, smart_select_url, valid_types
from .utils import Paginator, setup_logging, sys_argv
from ..main import search
from ..update import update_app
from ..utils import (
    valid_cover_types,
    default_cover_type,
    validate_url as __validate,
    validate_legacy_url,
    validate_group_url as _validate_group_url
)
from ..language import get_language, Language
from ..format import formats, default_save_as_format
from ..format.utils import NumberWithLeadingZeros
from ..errors import InvalidURL
from .. import __description__

log = logging.getLogger(__name__)

def _validate(url):
    try:
        _url = __validate(url)
    except InvalidURL:
        pass
    else:
        return _url
    # Legacy support
    try:
        _url = validate_legacy_url(url)
    except InvalidURL as e:
        raise argparse.ArgumentTypeError(str(e))
    return _url

def validate_url(url):
    if os.path.exists(url):
        with open(url, 'r') as opener:
            content = opener.read()
    else:
        content = url

    urls = []
    for _url in content.splitlines():
        if not _url:
            continue

        urls.append((_validate(_url), _url))
    
    return urls

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
        lowered_args = [i.lower() for i in sys.argv]
        if '-pipe' in lowered_args:
            pipe = True
            pipe_value = sys.stdin.read()
        else:
            pipe = False
            pipe_value = None

        self.search = '--search' in lowered_args
        self.unsafe = '--unsafe' in lowered_args

        # Manipulate positional arguments
        if pipe:
            sys_argv.append(pipe_value)

        self.pipe = pipe
        self.pipe_value = pipe_value

    def __call__(self, parser, namespace, values, option_string=None):
        urls = self.pipe_value if self.pipe else values

        if self.pipe and self.search:
            parser.error("search with pipe input are not supported")

        if not self.search:
            try:
                setattr(namespace, self.dest, validate_url(urls))
            except argparse.ArgumentTypeError as e:
                parser.error(str(e))
            return
        
        def print_err(text):
            print(f"\n{text}\n")

        # Begin searching
        iterator = search(urls, self.unsafe)
        count = 1
        choices = {}
        paginator = Paginator()

        # For next results
        choices['next'] = "next"

        # For previous results
        choices['previous'] = "previous"

        fetch = True
        while True:
            if fetch:
                mangas = []
                # 10 results displayed at the screen
                for _ in range(10):
                    try:
                        mangas.append(next(iterator))
                    except StopIteration:
                        pass
                
                if mangas:                    
                    paginator.add_page(*[manga.title for manga in mangas])

                    # Append choices for user input
                    for manga in mangas:
                        choices[str(count)] = manga
                        count += 1
                else:
                    try:
                        paginator.previous()
                    except IndexError:
                        parser.error(f"Search results \"{urls}\" are empty")
                    else:
                        print_err("[ERROR] There are no more results")

            def print_choices():
                text = f"Search results for \"{urls}\""

                # Build dynamic bars
                dynamic_bar = ""
                for _ in range(len(text)):
                    dynamic_bar += "="
                
                print(dynamic_bar)
                print(text)
                print(dynamic_bar)

                paginator.print()
                
                print("")

                print("type \"next\" to show next results")
                print("type \"previous\" to show previous results")

            print_choices()

            # User input
            _next = False
            previous = False
            while True:
                choice = input("=> ")
                try:
                    manga = choices[choice]
                except KeyError:
                    print_err('[ERROR] Invalid choice, try again')
                    print_choices()
                    continue
                else:
                    if manga == "next":
                        _next = True
                    elif manga == "previous":
                        try:
                            paginator.previous()
                        except IndexError:
                            print_err('[ERROR] Choices are out of range, try again')
                            print_choices()
                            continue

                        previous = True
                    break
            
            if _next:
                paginator.next()
                fetch = True
                continue
            elif previous:
                fetch = False
                continue
            else:
                break
        
        setattr(namespace, self.dest, validate_url(manga.id))        

def get_args(argv):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        'URL',
        action=InputHandler,
        help='MangaDex URL or a file containing MangaDex URLs',
        # type=validate_url,
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
    parser.add_argument('--unsafe', help='Enable unsafe mode', action='store_true')

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
        help='Use chapter title for each chapters. NOTE: This option is useless if used with any single format.'
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

    # Miscellaneous
    misc_group = parser.add_argument_group('Miscellaneous')
    misc_group.add_argument('-pipe', action='store_true', help="Download from pipe input")
    misc_group.add_argument(
        '--enable-legacy-sorting',
        action='store_true',
        help='Enable legacy sorting chapter images for old reader application'
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

    if args.type:
        urls = []
        for parsed_url, orig_url in args.URL:
            url = build_URL_from_type(args.type, parsed_url)
            urls.append(url)
        args.URL = urls
    else:
        urls = []
        for parsed_url, orig_url in args.URL:
            url = smart_select_url(orig_url)
            urls.append(url)
        args.URL = urls

    return args
