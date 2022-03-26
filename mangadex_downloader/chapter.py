import logging
import re
from typing import Dict, List

from .language import Language
from .fetcher import get_chapter_images, get_chapter, get_group
from .errors import ChapterNotFound

log = logging.getLogger(__name__)

# Helper for get group id
def get_group_id(chapter_data):
    chapter = chapter_data['data']['attributes']['chapter']

    group_id = None
    rels = chapter_data['data']['relationships']
    for rel in rels:
        _id = rel['id']
        _type = rel['type']
        if _type == 'scanlation_group':
            group_id = _id
    
    if group_id is None:
        raise RuntimeError("Cannot find scanlator group from chapter %s" % chapter)
    
    return group_id

class ChapterImages:
    def __init__(
        self,
        chapter_id,
        start_page=None,
        end_page=None,
        data_saver=False
    ) -> None:
        self.id = chapter_id
        self.data_saver = data_saver
        self._images = []
        self._low_images = []
        self._data = None
        self._base_url = None
        self._hash = None
        self.start_page = start_page
        self.end_page = end_page
    
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
            if self.start_page is not None:
                if not (page >= self.start_page):
                    log.info("Ignoring page %s as \"start_page\" is %s" % (
                        page,
                        self.start_page
                    ))

                    page += 1
                    continue
                
            if self.end_page is not None:
                if not (page <= self.end_page):
                    log.info("Ignoring page %s as \"end_page\" is %s" % (
                        page,
                        self.end_page
                    ))

                    page += 1
                    continue

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
        self.group = None
        self.name = None
        self.lang = None
        self.others_id = data.get('others')

    def get_lang_key(self):
        return Language(self.lang).name

    def get_name(self):
        if self.group is not None:
            return '[%s] %s' % (self.group, self.name)
        return self.name

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

    def iter_chapter_images(
        self,
        start_chapter=None,
        end_chapter=None,
        start_page=None,
        end_page=None,
        no_oneshot=False,
        data_saver=False,
        no_group_name=False,
        group=None,
        log_cache=False # For internal use only
    ):
        for volume, chapters in self._volumes.items():
            for chapter in chapters:
                if log_cache:
                    log.debug("Caching Volume. %s Chapter. %s" % (volume, chapter.chapter))

                num_chap = chapter.chapter
                if chapter.chapter != "none":
                    try:
                        num_chap = float(chapter.chapter)
                    except ValueError:
                        # Fix https://github.com/mansuf/mangadex-downloader/issues/7
                        # Sometimes chapter are in string value not in numbers
                        pass

                    # There is a chance that "Chapter 0" is Oneshot or prologue
                    # We need to verify that is valid oneshot chapter
                    # if it's valid oneshot chapter
                    # then we need to skip start_chapter and end_chapter checking
                    if isinstance(num_chap, float) and num_chap > 0.0:
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

                # Utility for re-use self._parse_vol_chap_imgs
                def parse(cd, no_group_name, group_name):
                    return self._parse_vol_chap_imgs(
                        volume,
                        chapter,
                        cd,
                        no_group_name,
                        group_name,
                        num_chap,
                        no_oneshot,
                        start_chapter,
                        start_page,
                        end_page,
                        data_saver
                    )

                if group is not None:
                    chapter_ids = [chapter.id]
                    chapter_ids.extend(chapter.others_id)
                    all_group = group.lower() == "all"

                    param_group_name = get_group(group)['data']['attributes']['name']
                    # Get chapter from different scanlation group
                    match = False
                    for chapter_id in chapter_ids:
                        cd = get_chapter(chapter_id)
                        group_id = get_group_id(cd)
                        group_name = get_group(group_id)['data']['attributes']['name']

                        if all_group:
                            # One chapter but all different scanlation groups
                            result = parse(cd, no_group_name, group_name)
                            if result is None:
                                continue
                            yield result

                            match = True

                        elif group != group_id:
                            continue
                        else:
                            # "group" is matching with "group_id"
                            match = True
                            break
                    
                    if not match:
                        log.info("Ignoring chapter %s, scanlator group \"%s\" is not match with \"%s\"" % (
                            num_chap,
                            group_name,
                            param_group_name
                        ))
                        continue
                    elif not all_group:
                        result = parse(cd, no_group_name, group_name)
                        if result is None:
                            continue

                        yield result
                else:
                    chapter_data = get_chapter(chapter.id)
                    
                    result = parse(chapter_data, no_group_name, None)
                    if result is None:
                        continue

                    yield result

    def _parse_vol_chap_imgs(
        self,
        volume,
        chapter,
        chapter_data,
        group_name,
        no_group_name,
        num_chap,
        no_oneshot,
        start_chapter,
        start_page,
        end_page,
        data_saver
    ):
        # Some manga has chapters where it has no pages / images inside of it.
        # We need to verify it, to prevent error when downloading the manga.
        pages = chapter_data['data']['attributes']['pages']
        if pages == 0:
            log.warning("Chapter %s has no images, ignoring..." % chapter.chapter)
            return None

        chapter_title = chapter_data['data']['attributes']['title']
        if chapter_title is None:
            lowered_chapter_title = ""
        else:
            lowered_chapter_title = chapter_title.lower()

        # Oneshot chapter checking
        chapter_name = ""
        if 'oneshot' in lowered_chapter_title and no_oneshot:
            log.info("Ignoring oneshot chapter since \"no_oneshot\" is True")
            return None
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
                    return None

            if volume != 'none':
                chapter_name += 'Volume. %s ' % volume
            chapter_name += 'Chapter. ' + chapter.chapter

        chapter.name = chapter_name

        # Set chapter language
        chapter.lang = chapter_data['data']['attributes']['translatedLanguage']

        # Get detailed info scanlator group
        if not no_group_name:
            chapter.group = group_name                    

        chap_imgs = ChapterImages(
            chapter.id,
            start_page,
            end_page,
            data_saver
        )

        return volume, chapter, chap_imgs

