import logging
import sys
import traceback

from ..errors import MangaDexException

log = logging.getLogger(__name__)

def download(args):
    # Single download
    if len(args.URL) == 1:
        url = args.URL[0]
        
        # Start downloading
        url(args, args.type)
        return
    
    # Multiple downloads
    for url in args.URL:
        try:
            url(args, args.type)
        except MangaDexException as e:
            # The error already explained
            log.error(e)
            traceback.print_exception(type(e), e, e.__traceback__)
            continue
