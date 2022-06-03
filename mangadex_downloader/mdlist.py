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

        self.id = data.get('id')
        self.data = data

        attr = data['attributes']

        self.name = attr.get('name')

        self.visibility = attr.get('visibility')

    def total(self) -> int:
        """Return total manga in the list"""
        rels = self.data['relationships']

        count = 0
        for rel in rels:
            _type = rel['type']
            
            if _type == "manga":
                count += 1

        return count

    def __str__(self) -> str:
        return f'{self.name} ({self.total()} total)'

    def __repr__(self) -> str:
        return f'{self.name} ({self.total()} total)'

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

