import logging
import sys

from ..update import check_version

log = logging.getLogger(__name__)

def check_update():
    log.debug('Checking update...')
    latest_version = check_version()
    if latest_version:
        log.info("There is new version mangadex-downloader ! (%s), you should update it with \"%s\" option" % (
            latest_version,
            '--update'
        ))
    elif latest_version == False:
        sys.exit(1)
    else:
        log.debug("No update found")