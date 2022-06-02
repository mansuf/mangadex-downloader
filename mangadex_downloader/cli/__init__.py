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
from ..errors import MangaDexException

_deprecated_opts = {
    'enable_legacy_sorting': '--enable-legacy-sorting is deprecated and will be removed in v1.3.0.',
}

def _check_deprecations(log, args):
    for arg, msg in _deprecated_opts.items():
        deprecated = getattr(args, arg)
        if deprecated:
            log.warning(msg)

def _main(argv):
    parser = None
    try:
        # Signal handler
        register_keyboardinterrupt_handler()

        # Get command-line arguments
        parser, args = get_args(argv)

        # Setup logging
        log = setup_logging('mangadex_downloader', args.verbose)

        # Setup proxy
        setup_proxy(args.proxy, args.proxy_env)

        # Check deprecation options
        _check_deprecations(log, args)

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

    # library error
    except MangaDexException as e:
        err_msg = str(e)
        return parser, 1, err_msg
    
    # Other exception
    except Exception as e:
        log.error("Unhandled exception, %s: %s" % (e.__class__.__name__, str(e)))
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        return parser, 1, None
    
    else:
        # We're done here
        return parser, 0, None

def main(argv=None):
    _argv = sys_argv if argv is None else argv

    args_parser, exit_code, err_msg = _main(_argv)
    
    if args_parser is not None and exit_code > 0 and err_msg:
        # It has error message, exit with .error()
        args_parser.error(err_msg)

    # There is no error during execution
    # or an error occured during parsing arguments
    # or another error that the program itself cannot handle it
    sys.exit(exit_code)

