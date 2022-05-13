# Based on https://github.com/mansuf/zippyshare-downloader/blob/main/zippyshare_downloader/downloader.py

import tqdm
import os
import time
import logging
from .network import Net
from .errors import HTTPException

log = logging.getLogger(__name__)

# For KeyboardInterrupt handler
_cleanup_jobs = []

# re.compile('bytes=([0-9]{1,}|)-([0-9]{1,}|)', re.IGNORECASE)

class BaseDownloader:
    def download(self):
        """Download the file"""
        raise NotImplementedError

    def cleanup(self):
        "Do the cleanup, Maybe close the session or the progress bar ? idk."
        raise NotImplementedError

class FileDownloader(BaseDownloader):
    def __init__(self, url, file, progress_bar=True, replace=False, **headers) -> None:
        self.url = url
        self.file = str(file) + '.temp'
        self.real_file = file
        self.progress_bar = progress_bar
        self.replace = replace
        self.headers_request = headers
        if headers.get('Range') is not None and self._get_file_size(self.file):
            raise ValueError('"Range" header is not supported while in resume state')

        self._tqdm = None
        
        self._register_keyboardinterrupt_handler()
    
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

    def download(self):
        initial_file_sizes = self._get_file_size(self.file)

        # Parse headers
        headers = self._parse_headers(initial_file_sizes)

        # Initiate request
        resp = Net.requests.get(self.url, headers=headers, stream=True)

        # Grab the file sizes
        file_sizes = float(resp.headers.get('Content-Length'))

        # If "Range" header request is present
        # Content-Length header response is not same as full size
        if initial_file_sizes:
            file_sizes += initial_file_sizes

        real_file_sizes = self._get_file_size(self.real_file)
        if real_file_sizes:
            if file_sizes == real_file_sizes and not self.replace:
                log.info('File exist and replace is False, cancelling download...')
                return

        # Build the progress bar
        self._build_progres_bar(initial_file_sizes, float(file_sizes))

        # Heavily adapted from https://github.com/choldgraf/download/blob/master/download/download.py#L377-L390
        chunk_size = 2 ** 16
        with open(self.file, 'ab' if initial_file_sizes else 'wb') as writer:
            while True:
                t0 = time.time()
                chunk = resp.raw.read(chunk_size)
                dt = time.time() - t0
                if dt < 0.005:
                    chunk_size *= 2
                elif dt > 0.1 and chunk_size > 2 ** 16:
                    chunk_size = chunk_size // 2
                if not chunk:
                    break
                writer.write(chunk)
                self._update_progress_bar(len(chunk))
        
        # Delete original file if replace is True and real file is exist
        if real_file_sizes and self.replace:
            os.remove(self.real_file)
        os.rename(self.file, self.real_file)

    def cleanup(self):
        # Close the progress bar
        if self._tqdm:
            self._tqdm.close()

class ChapterPageDownloader(FileDownloader):
    """Same with :class:`FileDownloader` but this one is specialized for chapter page download
    
    When the download is finished this downloader class will report the download info to MangaDex network.
    """

    def download(self):
        while True:
            initial_file_sizes = self._get_file_size(self.file)

            # Parse headers
            headers = self._parse_headers(initial_file_sizes)

            # Initiate request
            t1 = time.time()

            # Since server error are handled by session
            # We need to catch the error to report it to MangaDex network
            try:
                resp = Net.requests.get(self.url, headers=headers, stream=True)
            except HTTPException as e:
                resp = e.response

            # The downloader are requesting out of range bytes file
            # Because previous download are cancelled or error and .temp file are exists
            # and fully downloaded
            if resp.status_code == 416:
                # Mark it as finished
                self._write_final_file()
                return True

            # Report it to MangaDex network if failing
            if resp.status_code > 200 and not resp.status_code < 400:
                length = len(resp.content)
                t2 = time.time()
                self._report(resp, length, round((t2 - t1) * 1000), False)
                return False

            # Grab the file sizes
            file_sizes = float(resp.headers.get('Content-Length'))

            # If "Range" header request is present
            # Content-Length header response is not same as full size
            if initial_file_sizes:
                file_sizes += initial_file_sizes

            real_file_sizes = self._get_file_size(self.real_file)
            if real_file_sizes:
                if file_sizes == real_file_sizes and not self.replace:
                    log.info('File exist and replace is False, cancelling download...')
                    return True

            current_size = initial_file_sizes or 0

            # Build the progress bar
            self._build_progres_bar(initial_file_sizes, float(file_sizes))

            # Heavily adapted from https://github.com/choldgraf/download/blob/master/download/download.py#L377-L390
            report_total_size = 0
            chunk_size = 2 ** 16
            with open(self.file, 'ab' if initial_file_sizes else 'wb') as writer:
                while True:
                    t0 = time.time()
                    chunk = resp.raw.read(chunk_size)
                    report_total_size += len(chunk)
                    current_size += len(chunk)
                    dt = time.time() - t0
                    if dt < 0.005:
                        chunk_size *= 2
                    elif dt > 0.1 and chunk_size > 2 ** 16:
                        chunk_size = chunk_size // 2
                    if not chunk:
                        break
                    writer.write(chunk)
                    writer.flush()
                    self._update_progress_bar(len(chunk))
                t2 = time.time()

            # See #14
            # Download is not finished but marked as "finished"
            if current_size != file_sizes:
                self.cleanup()
                log.warning("File download is incomplete, restarting download...")
                continue

            self._write_final_file()

            # Finally report it to MangaDex network
            self._report(resp, report_total_size, round((t2 - t1) * 1000), True)
            return True

    def _write_final_file(self):
        # "Circular imports" problem
        from .format.utils import delete_file

        if os.path.exists(self.real_file):
            delete_file(self.real_file)

        chunk_size = 2 ** 16

        w_fp = open(self.real_file, 'wb')
        r_fp =  open(self.file, 'rb')
        while True:
            data = r_fp.read(chunk_size)
            if not data:
                break
            w_fp.write(data)

        w_fp.close()
        r_fp.close()

        delete_file(self.file)

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
        Net.requests.report(data)