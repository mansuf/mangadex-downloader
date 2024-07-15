# MIT License

# Copyright (c) 2022-present Rahman Yusuf

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
        return {"name": self.name, "hash": self.hash, "chapter_id": self.chapter_id}


@dataclass
class ChapterInfo(BaseInfo):
    name: str
    id: str

    @property
    def data(self):
        return {"name": self.name, "id": self.id}

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
            "chapters": self.chapters,
        }
