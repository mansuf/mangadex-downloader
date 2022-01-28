import sys
import argparse
import logging
import signal
from getpass import getpass
from .network import Net
from .main import download, login, logout
from .utils import validate_url as _validate
from .utils import _keyboard_interrupt_handler
from .errors import InvalidURL
from . import __description__

def setup_logging(name_module, verbose=False):
    log = logging.getLogger(name_module)
    handler = logging.StreamHandler()
    fmt = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(fmt)
    log.addHandler(handler)
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    return log

def validate_url(url):
    try:
        _id = _validate(url)
    except InvalidURL as e:
        raise argparse.ArgumentTypeError(str(e))
    return _id

def _main(argv):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('URL', type=validate_url, help='MangaDex URL')
    parser.add_argument('--folder', metavar='FOLDER', help='Store manga in given folder')
    parser.add_argument('--replace', help='Replace manga if exist', action='store_true')
    parser.add_argument('--proxy', metavar='SOCKS / HTTP Proxy', help='Set http/socks proxy')
    parser.add_argument('--proxy-env', action='store_true', help='use http/socks proxy from environments')
    parser.add_argument('--verbose', help='Enable verbose output', action='store_true')
    parser.add_argument(
        '--start-chapter',
        type=float,
        help='Start download chapter from given chapter number',
        metavar='CHAPTER'
    )
    parser.add_argument(
        '--end-chapter',
        type=float,
        help='Stop download chapter from given chapter number',
        metavar='CHAPTER'
    )
    parser.add_argument('--use-compressed-image', help='Use low size images manga (compressed quality)', action='store_true')
    parser.add_argument('--no-oneshot-chapter', help='If exist, don\'t download oneshot chapter', action='store_true')
    parser.add_argument('--login', help='Login to MangaDex', action='store_true')
    parser.add_argument(
        '--login-username',
        help='Login to MangaDex with username (you will be prompted to input password if --login-password are not present)',
        metavar='USERNAME'
    )
    parser.add_argument(
        '--login-password',
        help='Login to MangaDex with password (you will be prompted to input username if --login-username are not present)',
        metavar='PASSWORD'
    )
    args = parser.parse_args(argv)

    log = setup_logging('mangadex_downloader', args.verbose)

    if args.login:
        if not args.login_username:
            username = input("MangaDex username => ")
        else:
            username = args.login_username
        if not args.login_password:
            password = getpass("MangaDex password => ")
        else:
            password = args.login_password

        # Logging in
        login(password, username)

    # Give warning if --proxy and --proxy-env is present
    if args.proxy and args.proxy_env:
        log.warning('--proxy and --proxy-env options are present, --proxy option will be ignored')

    if args.proxy_env:
        log.debug('Using proxy from environments')
    Net.trust_env = args.proxy_env
    if args.proxy:
        log.debug('Setting up proxy from --proxy option')
        Net.set_proxy(args.proxy)
    download(
        args.URL,
        args.folder,
        args.replace,
        args.use_compressed_image,
        args.start_chapter,
        args.end_chapter,
        args.no_oneshot_chapter
    )

    if args.login:
        logout()

    log.info("Cleaning up...")
    log.debug('Closing network object')
    Net.close()

def main(argv=None):
    # Register KeyboardInterrupt handler
    signal.signal(signal.SIGINT, _keyboard_interrupt_handler)

    if argv is None:
        _main(sys.argv[1:])
    else:
        _main(argv)

if __name__ == "__main__":
    main()

