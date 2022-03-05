import queue
import sys
import threading
import logging
import traceback
from concurrent.futures import Future

log = logging.getLogger(__name__)

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
        result = fut.result()
        if isinstance(result, Exception):
            # Error is raised
            # Exit app with code 1
            sys.exit(1)

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
                    log.error("Exception raised in worker thread, %s: %s" % (
                        err.__class__.__name__,
                        str(err)
                    ))
                    traceback.print_exception(type(err), err, err.__traceback__, file=sys.stderr)
                    fut.set_result(err)
                fut.set_result(None)

class BaseFormat:
    def __init__(
        self,
        path,
        manga,
        compress_img,
        replace,
        kwargs_iter_chapter_img
    ):
        self.path = path
        self.manga = manga
        self.compress_img = compress_img
        self.replace = replace
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