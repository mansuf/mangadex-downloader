import logging
import re
from typing import Dict, List

from .utils import Language
from .fetcher import get_chapter_images, get_chapter
from .errors import ChapterNotFound

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
    def __init__(self, data, title, lang) -> None:
        self._data = data
        self._volumes = {} # type: Dict[str, List[_Chapter]]
        self._chapters = [] # type: List
        self._lang = lang
        self._title = title
        self._parse_volumes()
    
    def _parse_volumes(self):
        data = self._data.get('volumes')

        # if translated language is not found in selected manga
        # raise error
        if not data:
            raise ChapterNotFound("Manga \"%s\" with %s language has no chapters" % (
                self._title,
                Language(self._lang).name
            ))

        # Sorting volumes
        volumes = []

        # I forgot if variables are inside functions they become local not global
        # rofl
        class _dummy:
            pass
        vol = _dummy()
        vol.none_volume = False
        vol.none_value = None

        def append_volumes(num):
            try:
                volumes.append(int(num))
            except ValueError:
                # none volume detected
                vol.none_volume = True
                vol.none_value = num

        # Sometimes volumes are in list not in dict
        # wtf
        # Reference: https://api.mangadex.org/manga/d667637e-9e6d-4c5a-89c4-0faba6f96338/aggregate?translatedLanguage[]=en
        if isinstance(data, list):
            for info in data:
                num = info['volume']
                append_volumes(num)
        else:
            for num in data.keys():
                append_volumes(num)

        volumes = sorted(volumes)
        if vol.none_volume:
            volumes.append(vol.none_value)
        for volume in volumes:

            chapters = []

            # As far as i know, if volumes are in list, the list only have 1 data
            if isinstance(data, list):
                value = data[0]
            else:
                value = data[str(volume)]

            # Retrieving chapters
            c = value.get('chapters')

            def append_chapters(value):
                chap = _Chapter(value)
                chapters.append(chap)
                self._chapters.append(chap.to_dict())

            # Sometimes chapters are in list not in dict
            # I don't know why
            # Reference: https://api.mangadex.org/manga/433e77d2-5a58-48a3-95b8-e3c02f309255/aggregate?translatedLanguage[]=en
            if isinstance(c, list):
                for value in c:
                    append_chapters(value)
            else:
                for value in c.values():
                    append_chapters(value)

            chapters.reverse()
            self._volumes[volume] = chapters

    def iter_chapter_images(self, start_chapter=None, end_chapter=None, no_oneshot=False, data_saver=False):
        for volume, chapters in self._volumes.items():
            for chapter in chapters:
                if chapter.chapter != "none":
                    try:
                        num_chap = float(chapter.chapter)
                    except ValueError:
                        # Fix https://github.com/mansuf/mangadex-downloader/issues/7
                        # Sometimes chapter are in string value not in numbers
                        num_chap = chapter.chapter

                    # There is a chance that "Chapter 0" is Oneshot or prologue
                    # We need to verify that is valid oneshot chapter
                    # if it's valid oneshot chapter
                    # then we need to skip start_chapter and end_chapter checking
                    if isinstance(num_chap, float):
                        if num_chap == 0.0:
                            pass
                        else:
                            if start_chapter is not None:
                                # Lifehack
                                if not (num_chap >= start_chapter):
                                    log.info("Ignoring chapter %s as \"start_chapter\" is %s" % (
                                        num_chap,
                                        start_chapter
                                    ))
                                    continue

                            if end_chapter is not None:
                                # Lifehack
                                if not (num_chap <= end_chapter):
                                    log.info("Ignoring chapter %s as \"end_chapter\" is %s" % (
                                        num_chap,
                                        end_chapter
                                    ))
                                    continue

                # Some manga has chapters where it has no pages / images inside of it.
                # We need to verify it, to prevent error when downloading the manga.
                chapter_data = get_chapter(chapter.id)
                pages = chapter_data['data']['attributes']['pages']
                if pages == 0:
                    log.warning("Chapter %s has no images, ignoring..." % chapter.chapter)
                    continue

                chapter_title = chapter_data['data']['attributes']['title']
                if chapter_title is None:
                    lowered_chapter_title = ""
                else:
                    lowered_chapter_title = chapter_title.lower()

                # Oneshot chapter checking
                chapter_name = ""
                if 'oneshot' in lowered_chapter_title and no_oneshot:
                    log.info("Ignoring oneshot chapter since \"no_oneshot\" is True")
                    continue
                elif 'oneshot' in lowered_chapter_title:
                    chapter_name += "Oneshot"
                else:
                    # If chapter 0 is prologue or whatever and not oneshot
                    # Re-check start_chapter
                    if start_chapter is not None and isinstance(num_chap, float):
                        # Lifehack
                        if not (num_chap >= start_chapter):
                            log.info("Ignoring chapter %s as \"start_chapter\" is %s" % (
                                num_chap,
                                start_chapter
                            ))
                            continue

                    if volume != 'none':
                        chapter_name += 'Volume. %s ' % volume
                    chapter_name += 'Chapter. ' + chapter.chapter


                yield volume, chapter.chapter, chapter_name, ChapterImages(chapter.id, data_saver)

