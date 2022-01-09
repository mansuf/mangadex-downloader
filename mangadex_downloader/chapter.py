import logging
import re
from typing import Dict, List
from .fetcher import get_chapter_images

log = logging.getLogger(__name__)

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
        volumes = self._data.get('volumes')
        # Retrieving volumes
        for volume, value in volumes.items():

            chapters = []
            
            # Retrieving chapters
            c = value.get('chapters')
            for value in c.values():
                chap = _Chapter(value)
                chapters.append(chap)
                self._chapters.append(chap.to_dict())

            self._volumes[volume] = chapters

    def iter_chapter_images(self, data_saver=False):
        for volume, chapters in self._volumes.items():
            for chapter in chapters:
                log.info('Getting images from chapter %s' % chapter.chapter)
                data = get_chapter_images(chapter.id)

                # Construct image url
                base_url = data.get('baseUrl')
                chapter_hash = data['chapter']['hash']
                quality_mode = 'data-saver' if data_saver else 'data'
                if data_saver:
                    images = data['chapter']['dataSaver']
                else:
                    images = data['chapter']['data']

                chapter_page = 1
                for img in images:
                    url = '{0}/{1}/{2}/{3}'.format(
                        base_url,
                        quality_mode,
                        chapter_hash,
                        img
                    )

                    # Yield it
                    yield volume, chapter.chapter, chapter_page, url, img

                    chapter_page += 1

