import sys
import argparse
import logging
from .network import Net
from .main import download
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

def main(argv):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('URL', help='MangaDex URL')
    parser.add_argument('--folder', metavar='FOLDER', help='Store manga in given folder')
    parser.add_argument('--proxy', metavar='SOCKS / HTTP Proxy', help='Set http/socks proxy')
    parser.add_argument('--proxy-env', action='store_true', help='use http/socks proxy from environments')
    parser.add_argument('--verbose', help='Enable verbose output', action='store_true')
    args = parser.parse_args(argv)

    log = setup_logging('mangadex_downloader', args.verbose)

    # Give warning if --proxy and --proxy-env is present
    if args.proxy and args.proxy_env:
        log.warning('--proxy and --proxy-env options are present, --proxy option will be ignored')

    if args.proxy_env:
        log.debug('Using proxy from environments')
    Net.trust_env = args.proxy_env
    if args.proxy:
        log.debug('Setting up proxy from --proxy option')
        Net.set_proxy(args.proxy)
    download(args.URL, args.folder)

    log.debug('Closing network object')
    Net.close()



if __name__ == "__main__":
    main(sys.argv[1:])

