import queue
import threading
import time

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

        self._shutdown_event = threading.Event()
        self._queue = queue.Queue()

    def register_keyboardinterrupt_handler(self):
        # If CTRL+C is pressed all process is interrupted, right ?
        # Now when this happens in PDF or ZIP processing, this can cause
        # corrupted files.
        # The process is queue-based
        thread = threading.Thread(target=self._main)
        thread.start()

        # Thread to check if mainthread is alive or not
        # if not, then thread queue must be shutted down too
        shutdown_thread = threading.Thread(target=self._loop_check_mainthread)
        shutdown_thread.start()

    def _loop_check_mainthread(self):
        is_alive = lambda: threading.main_thread().is_alive()
        alive = is_alive()
        while alive:
            time.sleep(0.3)
            if self._shutdown_event.is_set():
                break
            alive = is_alive()
        self._shutdown_main()

    def _submit(self, job):
        event = threading.Event()
        data = [event, job]
        self._queue.put(data)
        event.wait()

    def _shutdown_main(self):
        # Shutdown only to _main function
        self._queue.put(None)

    def _shutdown(self):
        # Shutdown both
        self._shutdown_event.set()

    def _main(self):
        while True:
            data = self._queue.get()
            if data is None:
                return
            else:
                event, job = data
                try:
                    job()
                except Exception:
                    pass
                event.set()

    def main(self):
        """Execute main format

        Subclasses must implement this.
        """
        raise NotImplementedError