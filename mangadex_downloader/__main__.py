import sys
import argparse
from .network import Net
from .main import download
from . import __description__

def main(argv):
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('URL', help='MangaDex URL')
    parser.add_argument('--folder', metavar='FOLDER', help='Store manga in given folder')
    parser.add_argument('--proxy', metavar='SOCKS / HTTP Proxy', help='Set http/socks proxy')
    parser.add_argument('--proxy-env', action='store_true', help='use http/proxy from environments')
    args = parser.parse_args(argv)
    Net.trust_env = args.proxy_env
    if args.proxy:
        Net.set_proxy(args.proxy)
    download(args.URL, args.folder)
    Net.close()



if __name__ == "__main__":
    main(sys.argv[1:])

