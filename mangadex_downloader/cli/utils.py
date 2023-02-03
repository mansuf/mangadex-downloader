# MIT License

# Copyright (c) 2022 Rahman Yusuf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import signal
import sys

from .. import __version__, __repository__, __url_repository__
from ..update import architecture, executable
from ..network import Net
from ..downloader import _cleanup_jobs
from ..errors import MangaDexException, NotLoggedIn

log = logging.getLogger(__name__)

# Will be used in main() and get_args()
sys_argv = sys.argv[1:]

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

def setup_proxy(proxy=None, from_env=False):
    if proxy and from_env:
        raise MangaDexException("--proxy and --proxy-env cannot be together")

    if from_env:
        log.debug("Using proxy from environments")

    if proxy:
        log.debug('Setting up proxy from --proxy option')
        Net.set_proxy(proxy)

def setup_network(args):
    # Build proxy
    setup_proxy(args.proxy, args.proxy_env)

    # Setup delay requests (if set)
    Net.set_delay(args.delay_requests)

    if args.dns_over_https:
        Net.set_doh(args.dns_over_https)
    
    if args.timeout:
        Net.set_timeout(args.timeout)

    Net.set_auth(args.login_method)

def _keyboard_interrupt_handler(*args):
    print("Cleaning up...")
    # Downloader are not cleaned up
    for job in _cleanup_jobs:
        job()

    # Logging out
    try:
        Net.mangadex.logout()
    except NotLoggedIn:
        pass

    print("Action interrupted by user", file=sys.stdout)
    sys.exit(0)

def register_keyboardinterrupt_handler():
    # CTRL+C is pressed
    signal.signal(signal.SIGINT, _keyboard_interrupt_handler)

    # CTRL+D (in Unix) is pressed or taskkill without force (in Windows)
    signal.signal(signal.SIGTERM, _keyboard_interrupt_handler)

def close_network_object():
    log.info("Cleaning up...")
    log.debug("Closing netwok object")
    Net.close()

class IteratorEmpty(Exception):
    pass

# Honestly, this code was total messed up
# I don't know how to make pagination correctly
class Paginator:
    """A tool to create sequence of pages"""
    def __init__(self, iterator, limit=10):
        self._pages = []

        self._pos = 0
        self.iterator = iter(iterator)
        self.limit = limit

        self.duplicates = []

    @property
    def pos(self):
        """"Return current position"""
        return self._pos

    def _get_data(self):
        items = []
        for _ in range(self.limit):
            try:
                item = next(self.iterator)
            except StopIteration:
                break

            # To prevent duplicated results
            item_id = getattr(item, "id", None)
            if item_id is None:
                is_duplicate = item in self.duplicates
            else:
                is_duplicate = item_id in self.duplicates

            if is_duplicate:
                continue

            items.append(item)
            self.duplicates.append(item if item_id is None else item_id)
        
        return items

    def _add_page(self, until_pos):
        # To prevent for loop is not executed
        until_pos = until_pos + 1

        for _ in range(self._pos, until_pos):
            items = self._get_data()
            if not items:
                break
            self._pages.append(items)

    def _load_page_from_pos(self, for_pos):
        try:
            self._pages[for_pos]
        except IndexError:
            return False
        else:
            return True

    def _try_load(self, for_pos):
        """Try to load page data for given pos
        
        If not exist it will add page until given pos.
        """
        success = self._load_page_from_pos(for_pos)
        
        if success:
            return True

        # Add page if pages for given pos is empty
        self._add_page(for_pos)

        # Try to load again
        return self._load_page_from_pos(for_pos)

    def next(self):
        """Return next position items"""
        pos = self._pos

        success = self._try_load(pos)
        if not success:
            raise IteratorEmpty()

        # Retrieving page
        items = self._pages[pos]
        start_item_pos = pos * self.limit
        result = [
            (pos, item) for pos, item in enumerate(items, start=start_item_pos + 1)
        ]

        self._pos += 1

        return result

    def previous(self):
        """Return previous current position items"""
        pos = self._pos - 2
        if pos < 0:
            raise IndexError()

        items = self._pages[pos]
        start_item_pos = pos * self.limit
        result = [
            (pos, item) for pos, item in enumerate(items, start=start_item_pos + 1)
        ]

        self._pos -= 1

        return result

def print_version_info():
    bundled_executable = 'yes' if executable else 'no'

    print(f"mangadex-downloader v{__version__} ({__url_repository__}/{__repository__})")
    print("Python: {0[0]}.{0[1]}.{0[2]}".format(sys.version_info))
    print(f"arch: {architecture}")
    print(f"bundled executable: {bundled_executable}")

def dynamic_bars(length):
    if isinstance(length, str):
        length = len(length)

    bar = ""
    for _ in range(length):
        bar += "="
    
    return bar

def get_key_value(text, sep='='):
    splitted = text.split(sep, maxsplit=1)
    key = splitted[0]
    value = "".join(splitted[1:])
    return key, value

def split_comma_separated(text, single_value_to_list=False):
    if ',' not in text:
        return [text] if single_value_to_list else  text
    
    return [i.strip() for i in text.split(',')]

def check_group_all(args):
    """Check `--group` is containing `all` value with another `--group <group_id>` """
    if args.group is None:
        return

    is_all = filter(lambda x: x.lower().strip() == "all", args.group)

    try:
        next(is_all)
    except StopIteration:
        pass
    else:
        if len(args.group) > 1:
            raise MangaDexException("'--group all' cannot be used with another '--group <group_id>'")