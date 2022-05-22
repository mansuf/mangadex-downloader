import queue
import sys
import threading
import logging
import traceback
from concurrent.futures import Future

log = logging.getLogger(__name__)

class WorkerThreadError(Exception):
    """Raised when error is happened in worker thread"""
    pass

class _Worker:
    def __init__(self) -> None:
        self._queue = queue.Queue()
        self._shutdown_event = threading.Event()

        self._thread_main = threading.Thread(target=self._main)
        # Thread to check if mainthread is alive or not
        # if not, then thread queue must be shutted down too
        self._thread_shutdown = threading.Thread(target=self._loop_check_mainthread)

    def start(self):
        self._thread_main.start()
        self._thread_shutdown.start()

    def _loop_check_mainthread(self):
        main_thread = threading.main_thread()
        main_thread.join()
        self._shutdown_main()

    def submit(self, job):
        fut = Future()
        data = [fut, job]
        self._queue.put(data)
        err = fut.exception()
        if err:
            raise err

    def _shutdown_main(self):
        # Shutdown only to _main function
        self._queue.put(None)

    def shutdown(self):
        # Shutdown both
        self._shutdown_event.set()

    def _main(self):
        while True:
            data = self._queue.get()
            if data is None:
                return
            else:
                fut, job = data
                try:
                    job()
                except Exception as err:
                    fut.set_exception(err)
                else:
                    fut.set_result(None)

class BaseFormat:
    def __init__(
        self,
        path,
        manga,
        compress_img,
        replace,
        legacy_sorting,
        no_verify,
        kwargs_iter_chapter_img
    ):
        self.path = path
        self.manga = manga
        self.compress_img = compress_img
        self.replace = replace
        self.legacy_sorting = legacy_sorting
        self.verify = not no_verify
        self.kwargs_iter = kwargs_iter_chapter_img

    def create_worker(self):
        # If CTRL+C is pressed all process is interrupted, right ?
        # Now when this happens in PDF or ZIP processing, this can cause
        # corrupted files.
        # The purpose of this function is to prevent interrupt from CTRL+C
        # Let the job done safely and then shutdown gracefully
        worker = _Worker()
        worker.start()
        return worker

    def main(self):
        """Execute main format

        Subclasses must implement this.
        """
        raise NotImplementedError