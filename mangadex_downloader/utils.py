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

import os
import re
import time
import signal
import json
import logging
import sys
import threading
import queue
from io import BytesIO
from pathvalidate import sanitize_filename
from enum import Enum
from getpass import getpass
from concurrent.futures import Future
from .errors import InvalidURL, NotLoggedIn

log = logging.getLogger(__name__)

def validate_url(url):
    """Validate mangadex url and return the uuid"""
    re_url = re.compile(r'([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})')
    match = re_url.search(url)
    if match is None:
        raise InvalidURL('\"%s\" is not valid MangaDex URL' % url)
    return match.group(1)

def validate_legacy_url(url):
    """Validate old mangadex url and return the id"""
    re_url = re.compile(r'mangadex\.org\/(title|manga|chapter)\/(?P<id>[0-9]{1,})')
    match = re_url.search(url)
    if match is None:
        raise InvalidURL('\"%s\" is not valid MangaDex URL' % url)
    return match.group('id')

def validate_group_url(url):
    """Validate group mangadex url and return the id"""
    if url is None:
        return
    all_group = url.lower().strip() == "all"
    if not all_group:
        return validate_url(url)
    else:
        return "all"

def create_chapter_folder(base_path, chapter_title):
    chapter_path = base_path / sanitize_filename(chapter_title)
    if not chapter_path.exists():
        chapter_path.mkdir(exist_ok=True)

    return chapter_path

# This is shortcut to extract data from localization dict structure
# in MangaDex JSON data
# For example: 
# {
#     'attributes': {
#         'en': '...' # This is what we need 
#     }
# }
def get_local_attr(data):
    if not data:
        return ""
    for key, val in data.items():
        return val

class File:
    """A utility for file naming

    Parameter ``file`` can take IO (must has ``name`` object) or str
    """
    def __init__(self, file):
        if hasattr(file, 'name'):
            full_name = file.name
        else:
            full_name = file
    
        name, ext = os.path.splitext(full_name)

        self.name = name
        self.ext = ext

    def __repr__(self) -> str:
        return self.full_name

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """Return file name with extension file"""
        return self.name + self.ext

    def change_name(self, new_name):
        """Change file name to new name, but the extension file will remain same"""
        self.name = new_name

def input_handle(*args, **kwargs):
    """Same as input(), except when user hit EOFError the function automatically called sys.exit(0)"""
    try:
        return input(*args, **kwargs)
    except EOFError:
        sys.exit(0)

def getpass_handle(*args, **kwargs):
    """Same as getpass(), except when user hit EOFError the function automatically called sys.exit(0)"""
    try:
        return getpass(*args, **kwargs)
    except EOFError:
        sys.exit(0)

def comma_separated_text(array):
    # Opening square bracket
    text = "["

    # Append first item
    text += array.pop(0)

    # Add the rest of items
    for item in array:
        text += ', ' + item

    # Closing square bracket
    text += ']'
    
    return text

def delete_file(file):
    """Helper function to delete file, retry 5 times if error happens"""
    if not os.path.exists(file):
        return

    err = None
    for attempt in range(5):
        try:
            os.remove(file)
        except Exception as e:
            log.debug("Failed to delete file \"%s\", reason: %s. Trying... (attempt: %s)" % (
                file,
                str(e),
                attempt 
            ))
            err = e
            time.sleep(attempt * 0.5) # Possible value 0.0 (0 * 0.5) lmao
            continue
        else:
            break

    # If 5 attempts is failed to delete file (ex: PermissionError, or etc.)
    # raise error
    if err is not None:
        raise err

class QueueWorker(threading.Thread):
    """A queue-based worker run in another thread"""
    def __init__(self) -> None:
        threading.Thread.__init__(self)

        self._queue = queue.Queue()

        # Thread to check if mainthread is alive or not
        # if not, then thread queue must be shutted down too
        self._thread_wait_mainthread = threading.Thread(target=self._wait_mainthread)

    def start(self):
        super().start()
        self._thread_wait_mainthread.start()

    def _wait_mainthread(self):
        """Wait for mainthread to exit and then shutdown :class:`QueueWorker` thread"""
        main_thread = threading.main_thread()
        main_thread.join()
        self._queue.put(None)

    def submit(self, job, blocking=True):
        """Submit a job and return the result
        
        If ``blocking`` is ``True``, the function will wait until job is finished. 
        If ``blocking`` is ``False``, it will return :class:`concurrent.futures.Future` instead. 
        The ``job`` parameter must be function without parameters or lambda wrapped.
        """
        fut = Future()
        data = [fut, job]
        self._queue.put(data)

        if not blocking:
            return fut

        err = fut.exception()
        if err:
            raise err
        
        return fut.result()

    def shutdown(self):
        """Shutdown the thread by passing ``None`` value to queue"""
        self._queue.put(None)

    def run(self):
        while True:
            data = self._queue.get()
            if data is None:
                # Shutdown signal is received
                # begin shutting down
                return

            fut, job = data
            try:
                job()
            except Exception as err:
                fut.set_exception(err)
            else:
                fut.set_result(None)