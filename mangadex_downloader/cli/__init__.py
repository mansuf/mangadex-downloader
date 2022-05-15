import logging
import sys
import traceback
from .update import check_update
from .args_parser import get_args
from .validator import build_url
from .utils import (
    close_network_object,
    setup_logging,
    setup_proxy,
    register_keyboardinterrupt_handler,
    sys_argv
)
from .auth import login_with_err_handler, logout_with_err_handler
from .download import download
from ..errors import UnhandledHTTPError

def _main(argv):
    try:
        # Signal handler
        register_keyboardinterrupt_handler()

        # Get command-line arguments
        parser, args = get_args(argv)

        # Setup logging
        log = setup_logging('mangadex_downloader', args.verbose)

        # Setup proxy
        setup_proxy(args.proxy, args.proxy_env)

        # Login
        login_with_err_handler(args)

        # Building url
        build_url(parser, args)

        # Download the manga
        download(args)

        # Logout when it's finished
        logout_with_err_handler(args)

        # Check update
        check_update()

        # Cleaning up
        close_network_object()

    # HTTP error
    except UnhandledHTTPError as e:
        log.error(str(e))
        return 1
    
    # Other exception
    except Exception as e:
        log.error("Unhandled exception, %s: %s" % (e.__class__.__name__, str(e)))
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        return 1
    
    else:
        # We're done here
        return 0

def main(argv=None):
    if argv is None:
        exit_code = _main(sys_argv)
    else:
        exit_code = _main(argv)
    sys.exit(exit_code)