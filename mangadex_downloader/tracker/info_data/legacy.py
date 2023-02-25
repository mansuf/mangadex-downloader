from typing import Union, List
from dataclasses import dataclass

class BaseInfo:
    """Base info for download tracker in JSON format"""

    @property
    def data(self):
        """Return data that is ready to compare"""
        raise NotImplementedError

    def __eq__(self, o) -> bool:
        if not isinstance(o, BaseInfo):
            raise NotImplementedError

        return self.data == o.data

@dataclass
class ImageInfo(BaseInfo):
    name: str
    hash: str
    chapter_id: str

    @property
    def data(self):
        return {
            "name": self.name,
            "hash": self.hash,
            "chapter_id": self.chapter_id
        }

@dataclass
class ChapterInfo(BaseInfo):
    name: str
    id: str

    @property
    def data(self):
        return {
            "name": self.name,
            "id": self.id
        }
    
    def __eq__(self, o) -> bool:
        if isinstance(o, str):
            return self.id == o
        
        return super().__eq__(o)

@dataclass
class FileInfo(BaseInfo):
    name: str
    id: str
    hash: str
    completed: str
    images: Union[None, List[ImageInfo]]
    chapters: Union[None, List[ChapterInfo]]

    def __post_init__(self):
        if self.images is not None:
            self.images = [ImageInfo(**i) for i in self.images]

        if self.chapters is not None:
            self.chapters = [ChapterInfo(**i) for i in self.chapters]

    @property
    def data(self):
        return {
            "name": self.name,
            "id": self.id,
            "hash": self.hash,
            "completed": self.completed,
            "images": self.images,
            "chapters": self.chapters
        }