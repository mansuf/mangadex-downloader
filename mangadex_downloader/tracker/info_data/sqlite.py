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
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ImageInfo:
    name: str
    hash: str
    chapter_id: str

    def __eq__(self, o):
        if not isinstance(o, ImageInfo):
            raise NotImplementedError

        return self.name == o.name and self.chapter_id == o.chapter_id


@dataclass
class ChapterInfo:
    name: str
    id: str

    def __eq__(self, o):
        compare = None

        if isinstance(o, ChapterInfo):
            compare = self.name == o.name and self.id == o.id
        elif isinstance(o, str):
            compare = self.id == o
        else:
            raise NotImplementedError

        return compare


class FileInfoCompletedField:
    def __init__(self, *args):
        pass

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        if obj is None:
            # By default file_info.completed is False
            # because the download is not completed (just started)
            return False

        val = getattr(obj, self._name)

        if not val:
            return 0
        else:
            return 1

    def __set__(self, obj, value):
        if not isinstance(value, bool):
            raise ValueError("value must be boolean type")

        setattr(obj, self._name, value)


class FileInfoDatetimeField:
    def __init__(self, *args):
        pass

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        val = getattr(obj, self._name)

        return val.isoformat()

    def __set__(self, obj, value):
        val = datetime.fromisoformat(value)

        setattr(obj, self._name, val)


@dataclass
class FileInfo:
    name: str
    manga_id: str
    ch_id: str
    hash: str
    last_download_time: datetime
    completed: int
    volume: int
    images: Union[None, List[ImageInfo]]
    chapters: Union[None, List[ChapterInfo]]

    @classmethod
    def dummy(cls):
        """Create dummy FileInfo for all formats if --no-track is used"""
        return cls()

    def __post_init__(self):
        if self.images is not None:
            self.images = [ImageInfo(*(i[0], i[1], i[2])) for i in self.images]

        if self.chapters is not None:
            self.chapters = [ChapterInfo(*(i[0], i[1])) for i in self.chapters]

        if self.last_download_time is not None:
            self.last_download_time = datetime.fromisoformat(self.last_download_time)

    def __eq__(self, o):
        if not isinstance(o, FileInfo):
            raise NotImplementedError

        return (
            self.name == o.name
            and self.manga_id == o.manga_id
            and self.ch_id == o.ch_id
        )
