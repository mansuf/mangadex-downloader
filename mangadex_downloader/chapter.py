import logging
import re
from typing import Dict, List
from .fetcher import get_chapter_images

log = logging.getLogger(__name__)

class ChapterImages:
    def __init__(self, chapter_id, data_saver=False) -> None:
        self.id = chapter_id
        self.data_saver = data_saver
        self._images = []
        self._low_images = []
        self._data = None
        self._base_url = None
        self._hash = None
    
    def fetch(self):
        data = get_chapter_images(self.id)
        # Construct image url
        self._data = data
        self._base_url = data.get('baseUrl')
        self._hash = data['chapter']['hash']
        self._images = data['chapter']['data']
        self._low_images = data['chapter']['dataSaver']

    def iter(self):
        if self._data is None:
            raise Exception("fetch() is not called")

        quality_mode = 'data-saver' if self.data_saver else 'data'
        images = self._low_images if self.data_saver else self._images

        page = 1
        for img in images:
            url = '{0}/{1}/{2}/{3}'.format(
                self._base_url,
                quality_mode,
                self._hash,
                img
            )

            yield page, url, img

            page += 1

class _Chapter:
    def __init__(self, data) -> None:
        self.id = data.get('id')
        self.chapter = data.get('chapter')

    def to_dict(self):
        return {'Chapter %s' % self.chapter: self.id}

class Chapter:
    def __init__(self, data) -> None:
        self._data = data
        self._volumes = {} # type: Dict[str, List[_Chapter]]
        self._chapters = [] # type: List
        self._parse_volumes()
    
    def _parse_volumes(self):
        data = self._data.get('volumes')

        # Sorting volumes
        volumes = []
        none_volume = False
        none_value = None
        for num in data.keys():
            try:
                volumes.append(int(num))
            except ValueError:
                # none volume detected
                none_volume = True
                none_value = num
        volumes = sorted(volumes)
        if none_volume:
            volumes.append(none_value)
        for volume in volumes:

            chapters = []

            # Retrieving chapters
            value = data[str(volume)]
            c = value.get('chapters')
            for value in c.values():
                chap = _Chapter(value)
                chapters.append(chap)
                self._chapters.append(chap.to_dict())

            chapters.reverse()
            self._volumes[volume] = chapters

    def iter_chapter_images(self, start_chapter=None, end_chapter=None, no_oneshot=False, data_saver=False):
        for volume, chapters in self._volumes.items():
            for chapter in chapters:
                if no_oneshot and chapter.chapter == "none":
                    log.warning("Ignoring oneshot chapter since \"no_oneshot\" is True")
                    continue
                if chapter.chapter != "none":
                    num_chap = float(chapter.chapter)
                    if start_chapter is not None:
                        # Lifehack
                        if not (num_chap >= start_chapter):
                            log.warning("Ignoring chapter %s as \"start_chapter\" is %s" % (
                                num_chap,
                                start_chapter
                            ))
                            continue

                    if end_chapter is not None:
                        # Lifehack
                        if not (num_chap <= end_chapter):
                            log.warning("Ignoring chapter %s as \"end_chapter\" is %s" % (
                                num_chap,
                                end_chapter
                            ))
                            continue

                yield volume, chapter.chapter, ChapterImages(chapter.id, data_saver)

