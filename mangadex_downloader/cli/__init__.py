import sys
import time
import traceback
from .update import check_update
from .args_parser import get_args
from .url import build_url
from .utils import (
    cleanup_app,
    setup_logging,
    setup_network,
    register_keyboardinterrupt_handler,
    sys_argv,
)
from .config import build_config
from .auth import login_with_err_handler, logout_with_err_handler
from .download import download

from ..errors import MangaDexException
from ..format import deprecated_formats
from ..utils import queueworker_active_threads

_deprecated_opts = {
    # I know this isn't deprecated
    # But i need the warning feature, hehe
    "range": "--range is disabled, because it's broken and need to rework",
}


def check_deprecated_options(log, args):
    for arg, msg in _deprecated_opts.items():
        deprecated = getattr(args, arg)
        if deprecated:
            log.warning(msg)


def check_deprecated_formats(log, args):
    if args.save_as in deprecated_formats:
        log.warning(
            f"format `{args.save_as}` is deprecated, "
            "please use `raw` or `cbz` format with `--write-tachiyomi-info` instead"
        )


def check_conflict_options(args, parser):
    if args.ignore_missing_chapters and args.no_track:
        parser.error("--ignore-missing-chapters cannot be used when --no-track is set")

    if args.group and args.no_group_name:
        raise MangaDexException("--group cannot be used together with --no-group-name")

    if args.start_chapter is not None and args.end_chapter is not None:
        if args.start_chapter > args.end_chapter:
            raise MangaDexException("--start-chapter cannot be more than --end-chapter")

        if args.start_chapter < 0 and args.end_chapter >= 0:
            raise MangaDexException(
                "--end-chapter cannot be positive number while --start-chapter is negative number"
            )

    if args.start_page is not None and args.end_page is not None:
        if args.start_page > args.end_page:
            raise MangaDexException("--start-page cannot be more than --end-page")

        if args.start_page < 0 and args.end_page >= 0:
            raise MangaDexException(
                "--end-page cannot be positive number while --start-page is negative number"
            )


def _main(argv):
    parser = None
    try:
        # Signal handler
        register_keyboardinterrupt_handler()

        # Get command-line arguments
        parser, args = get_args(argv)

        # Setup logging
        log = setup_logging(
            "mangadex_downloader", True if args.log_level == "DEBUG" else False
        )

        # Check deprecated
        check_deprecated_options(log, args)
        check_deprecated_formats(log, args)

        # Check conflict options
        check_conflict_options(args, parser)

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

    # library error
    except MangaDexException as e:
        err_msg = str(e)
        return parser, 1, err_msg

    # Other exception
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        return parser, 2, None

    else:
        # We're done here
        return parser, 0, None


def main(argv=None):
    _argv = sys_argv if argv is None else argv

    # Notes for exit code
    # 0 Means it has no error
    # 1 is library error (at least we can handle it)
    # 2 is an error that we cannot handle (usually from another library or Python itself)

    if "--run-forever" in [i.lower() for i in _argv]:
        while True:
            args_parser, exit_code, err_msg = _main(_argv)

            if exit_code == 2:
                # Hard error
                # an error that we cannot handle
                # exit the application
                break

            # Shutdown worker threads
            # to prevent infinite worker threads
            for worker_thread in queueworker_active_threads:
                worker_thread.shutdown(blocking=True, blocking_timeout=3)

            time.sleep(5)
    else:
        args_parser, exit_code, err_msg = _main(_argv)

    cleanup_app()

    if args_parser is not None and exit_code > 0 and err_msg:
        # It has error message, exit with .error()
        args_parser.error(err_msg)

    # There is no error during execution
    # or an error occurred during parsing arguments
    # or another error that the program itself cannot handle it
    sys.exit(exit_code)
