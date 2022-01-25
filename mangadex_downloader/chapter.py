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

