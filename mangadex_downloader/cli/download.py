import logging
import sys

from ..errors import MangaDexException
from ..main import download as _download

log = logging.getLogger(__name__)

def download(args):
    for url in args.URL:
        err = True
        try:
            _download(
                url,
                args.folder,
                args.replace,
                args.use_compressed_image,
                args.start_chapter,
                args.end_chapter,
                args.no_oneshot_chapter,
                args.language,
                args.cover,
                args.save_as
            )
        except MangaDexException as e:
            # The error is already explained
            log.error(str(e))
        else:
            err = False
        
        if err:
            sys.exit(1)
