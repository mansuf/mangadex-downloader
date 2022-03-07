import logging
import sys

from ..errors import MangaDexException

log = logging.getLogger(__name__)

def download(args):
    for url in args.URL:
        err = True
        try:
            url(args, args.type)
        except MangaDexException as e:
            # The error is already explained
            log.error(str(e))
        else:
            err = False
        
        if err:
            sys.exit(1)
