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

import queue
import sys
import threading
import logging
import traceback
from ..utils import QueueWorker

log = logging.getLogger(__name__)

class BaseFormat:
    def __init__(
        self,
        path,
        manga,
        compress_img,
        replace,
        no_verify,
        kwargs_iter_chapter_img
    ):
        self.path = path
        self.manga = manga
        self.compress_img = compress_img
        self.replace = replace
        self.verify = not no_verify
        self.kwargs_iter = kwargs_iter_chapter_img

    def create_worker(self):
        # If CTRL+C is pressed all process is interrupted, right ?
        # Now when this happens in PDF or ZIP processing, this can cause
        # corrupted files.
        # The purpose of this function is to prevent interrupt from CTRL+C
        # Let the job done safely and then shutdown gracefully
        worker = QueueWorker()
        worker.start()
        return worker

    def main(self):
        """Execute main format

        Subclasses must implement this.
        """
        raise NotImplementedError