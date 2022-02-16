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

    def main(self):
        """Execute main format

        Subclasses must implement this.
        """
        raise NotImplementedError