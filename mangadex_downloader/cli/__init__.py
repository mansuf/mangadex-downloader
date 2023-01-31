import sys
import traceback
from .update import check_update
from .args_parser import get_args
from .url import build_url
from .utils import (
    close_network_object,
    setup_logging,
    setup_network,
    register_keyboardinterrupt_handler,
    sys_argv
)
from .config import build_config
from .auth import login_with_err_handler, logout_with_err_handler
from .download import download

from ..errors import MangaDexException
from ..format import deprecated_formats

_deprecated_opts = {
    # I know this isn't deprecated
    # But i need the warning feature, hehe
    "range": "--range is disabled, because it's broken and need to rework",
    "no_chapter_info": "--no-chapter-info is deprecated and will be removed in v2.9.0. " \
                       "Please use --use-chapter-cover to enable chapter info (cover) creation"
}

def check_deprecated_options(log, args):
    for arg, msg in _deprecated_opts.items():
        deprecated = getattr(args, arg)
        if deprecated:
            log.warning(msg)

def check_deprecated_formats(log, args):
    if args.save_as in deprecated_formats:
        log.warning(
            f"format `{args.save_as}` is deprecated, " \
             "please use `raw` or `cbz` format with `--write-tachiyomi-info` instead"
        )

        # Enable `--write-tachiyomi-info` because it's using `tachiyomi` and `tachiyomi-zip` format
        args.write_tachiyomi_info = True

def _main(argv):
    parser = None
    try:
        # Signal handler
        register_keyboardinterrupt_handler()

        # Get command-line arguments
        parser, args = get_args(argv)

        # Setup logging
        log = setup_logging('mangadex_downloader', args.verbose)

        # Check deprecated
        check_deprecated_options(log, args)
        check_deprecated_formats(log, args)

        # Parse config
        build_config(parser, args)

        # Setup network
        setup_network(args)

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

