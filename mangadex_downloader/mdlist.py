from .fetcher import get_list

# Why "MangaDexList" ? why not "List" ?
# to prevent typing.List conflict
class MangaDexList:
    def __init__(self, _id=None, data=None):
        if _id is None and data is None:
            raise ValueError("at least provide _id or data")
        elif _id and data:
            raise ValueError("_id and data cannot be together")

        if _id is not None:
            data = get_list(_id)['data']

        self.data = data

        attr = data['attributes']

        self.name = attr.get('name')

        self.visibility = attr.get('visibility')

    def iter_manga(self, unsafe=False):
        """Yield :class:`Manga` from a list

        Parameters
        -----------
        unsafe: Optional[:class:`bool`]
            If ``True``, allow users to get porn mangas in the list.
        """
        # "Circular imports" problem
        from .iterator import IteratorMangaFromList

        return IteratorMangaFromList(data=self.data.copy(), unsafe=unsafe)

