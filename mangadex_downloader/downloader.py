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

import tqdm
import os
import time
import logging
import re
from .utils import delete_file
from .network import Net
from .errors import HTTPException

log = logging.getLogger(__name__)

# For KeyboardInterrupt handler
_cleanup_jobs = []

class FileDownloader:
    def __init__(self, url, file, progress_bar=True, replace=False, use_requests=False, **headers) -> None:
        self.url = url
        self.file = str(file) + '.temp'
        self.real_file = file
        self.progress_bar = progress_bar
        self.replace = replace
        self.headers_request = headers
        self.chunk_size = 2 ** 13

        # If somehow this is used to sending HTTP requests from another websites (not mangadex)
        # then use requests.Session instead
        if use_requests:
            self.session = Net.requests
        else:
            self.session = Net.mangadex

        if headers.get('Range') is not None and self._get_file_size(self.file):
            raise ValueError('"Range" header is not supported while in resume state')

        self._tqdm = None
        
        self._register_keyboardinterrupt_handler()

        # If file exist, delete it
        if self.replace:
            delete_file(self.file)
    
    def _register_keyboardinterrupt_handler(self):
        _cleanup_jobs.append(lambda: self.cleanup())

    def _build_progres_bar(self, initial_size, file_sizes, desc='file_sizes'):
        if self.progress_bar:
            kwargs = {
                'initial': initial_size or 0,
                'total': file_sizes,
                'unit': 'B',
                'unit_scale': True
            }

            # Determine ncols progress bar
            length = len(desc)
            if length < 20:
                kwargs.setdefault('ncols', 80)
            elif length > 20 and length < 50:
                kwargs.setdefault('dynamic_ncols', True)
            # Length desc is more than 40 or 50
            elif length >= 50:
                desc = desc[:20] + '...'
                kwargs.setdefault('ncols', 90)

            kwargs.setdefault('desc', desc)

            self._tqdm = tqdm.tqdm(**kwargs)

    def _update_progress_bar(self, n):
        if self._tqdm:
            self._tqdm.update(n)

    def _get_file_size(self, file):
        if os.path.exists(file):
            return os.path.getsize(file)
        else:
            return None

    def _parse_headers(self, initial_sizes):
        headers = self.headers_request or {}

        if initial_sizes:
            headers['Range'] = 'bytes=%s-' % initial_sizes
        return headers

    def on_prepare(self):
        """This will be called before sending request to given url"""
        pass

    def on_read(self, chunk):
        """This will be called when reading data

        NOTE: this function will be called after :meth:`requests.Response.raw.read()` has been called
        """
        pass

    def on_finish(self):
        """This will be called when download is finished"""
        pass

    def on_error(self, err, resp):
        """Register event when downloader are having problem"""
        pass

    def on_receive_response(self, resp):
        """Register event when :class:`requests.Response` from given url are arrived"""
        pass

    def download(self):
        error = None
        resp = None
        for attempt, _ in enumerate(range(5), start=1):
            error = None
            resp = None
            self.on_prepare()

            initial_file_sizes = self._get_file_size(self.file)

            # Parse headers
            headers = self._parse_headers(initial_file_sizes)

            try:
                resp = self.session.get(self.url, headers=headers, stream=True, timeout=15)
            except Exception as e:
                # Other Exception
                error = e
            
            # The downloader are requesting out of range bytes file
            # Because previous download are cancelled or error and .temp file are exists
            # and fully downloaded
            if resp is not None and resp.status_code == 416:
                # Mark it as finished
                self.on_finish()
                self._write_final_file()
                return True

            # Request failed
            if error is not None or (
                resp is not None and
                resp.status_code > 200 and not resp.status_code < 400
            ):
                self.on_error(error, resp)
                return False

            # Response are arrived !
            self.on_receive_response(resp)

            # Grab the file sizes
            file_sizes = float(resp.headers.get('Content-Length'))

            # Try to check if the server support `Range` header
            content_range = resp.headers.get("content-range", "")
            if initial_file_sizes:
                cr_match = re.match("bytes %s\-[0-9]{1,}\/[0-9]{1,}" % initial_file_sizes, content_range)
            else:
                # This is hack, trust me
                cr_match = True
            accept_range = resp.headers.get('accept-ranges')
            if accept_range is None and not cr_match and os.path.exists(self.file):
                # Server didn't support `Range` header
                log.warning(
                    f"Server didn't support resume download, deleting '{os.path.basename(self.file)}'"
                )
                delete_file(self.file)
                
                initial_file_sizes = None

            # If "Range" header request is present
            # Content-Length header response is not same as full size
            if initial_file_sizes:
                file_sizes += initial_file_sizes

            # Check if file is exist or not
            real_file_sizes = self._get_file_size(self.real_file)
            if real_file_sizes:
                if file_sizes == real_file_sizes and not self.replace:
                    log.info('File exist and replace is False, cancelling download...')
                    self.on_finish()
                    return True

            # Build the progress bar
            self._build_progres_bar(initial_file_sizes, float(file_sizes))

            # Begin downloading
            current_size = 0
            with open(self.file, 'ab' if initial_file_sizes else 'wb') as writer:
                while True:
                    chunk = resp.raw.read(self.chunk_size)
                    current_size += len(chunk)
                    self.on_read(chunk)
                    if not chunk:
                        break
                    writer.write(chunk)
                    writer.flush()
                    self._update_progress_bar(len(chunk))

            # See #14
            # Download is not finished but marked as "finished"
            if current_size < file_sizes:
                self.cleanup()
                log.warning(
                    f"File download is incomplete, restarting download... (attempt: {attempt})"
                )
                continue

            self.on_finish()
            self._write_final_file()
            return True

        # Usually this will happend if 
        # - downloader trying to resume download but the server didn't support `Range` header
        # - The server didn't send full content of file (received bytes and `Content-Length` header are not same)
        if resp is not None:
            self.on_error(None, resp)
        return False

    def _write_final_file(self):
        if os.path.exists(self.real_file):
            delete_file(self.real_file)

        w_fp = open(self.real_file, 'wb')
        r_fp =  open(self.file, 'rb')
        while True:
            data = r_fp.read(self.chunk_size)
            if not data:
                break
            w_fp.write(data)

        w_fp.close()
        r_fp.close()

        delete_file(self.file)

    def cleanup(self):
        # Close the progress bar
        if self._tqdm:
            self._tqdm.close()

class ChapterPageDownloader(FileDownloader):
    """Same with :class:`FileDownloader` but this one is specialized for chapter page download
    
    When the download is finished this downloader class will report the download info to MangaDex network.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.on_prepare()
    
    def on_prepare(self):
        self.t1 = time.perf_counter()
        self.report_total_size = 0

        # Value will be changed in on_receive_response()
        self.resp = None

    def on_read(self, chunk):
        self.report_total_size += len(chunk)

    def on_finish(self):
        t2 = time.perf_counter()

        if self.report_total_size != 0:
            # To prevent "unsupported operand" error
            # Because if file exist and replace is `False`, on_finish() will be called (success)
            self._report(self.resp, self.report_total_size, round((t2 - self.t1) * 1000), True)

    def on_error(self, err, resp):
        if not isinstance(err, HTTPException) and resp is None:
            return

        response = resp if resp is not None else err.response
        content = response.content
        t2 = time.perf_counter()

        self._report(response, len(content), round((t2 - self.t1) * 1000), False)

    def on_receive_response(self, resp):
        self.resp = resp

    def _report(self, resp, size, _time, success):
        self.cleanup()

        # According to MangaDex devs
        # domain that not from mangadex.network are not allowed to report
        # so skip it
        if 'uploads.mangadex.org' in self.url:
            log.debug('Endpoint are not from mangadex.network, skipping report')
            return

        # Check if cached
        # If failed to retrieve images, mark cached as "False"
        cached = False
        # Fix #18
        # Random NoneType error while downloading
        # Whenever downloader get server error, Response headers are not parsed properly
        if success:
            cache_header = resp.headers.get('x-cache')

            # Just in case something is happened
            if cache_header is not None:
                cached = cache_header.startswith('HIT')

        data = {
            'url': self.url,
            'success': success,
            'cached': cached,
            'bytes': size,
            'duration': _time
        }
        Net.mangadex.report(data)