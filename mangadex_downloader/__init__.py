"""
Download manga from mangadex directly with web scrapping.
"""

import os
import random
import tqdm
import json
from download import download as dl
from mangadex_downloader.fetcher import (
    MangadexFetcher,
    MangadexChapterFetcher
)


class Mangadex:
    def __init__(self, language='English', verbose=False, output_folder=''):
        self.lang = language
        self._verbose = verbose
        self.output_folder = output_folder

    def _logger_info(self, message):
        if self._verbose:
            print('[INFO] %s' % (message))
        else:
            return

    def _get_file(self, title: str, volume: str, chapter: str, part: str):
        return os.path.join(self.output_folder, '%s/Vol. %s Ch. %s/%s.jpg') % (
            title,
            volume,
            chapter,
            part
        )

    def _get_folder(self, title: str, volume: str, chapter: str):
        return os.path.join(self.output_folder, '%s/Vol. %s Ch. %s') % (
            title,
            volume,
            chapter
        )

    def _get_cover(self, title: str):
        return '%s/cover.jpg' % (title)

    def _write_json(
        self,
        title: str,
        author: str,
        artist: str,
        description: str,
        genre: list,
        status: str,
    ):
        w = open(os.path.join(self.output_folder, title) + '/details.json', 'w')
        w.write(json.dumps({
            'title': title,
            'author': author,
            'artist': artist,
            'description': description,
            'genre': genre,
            'status': status,
            "_status values": ["0 = Unknown", "1 = Ongoing", "2 = Completed", "3 = Licensed"]
        }))
        w.close()

    def _create_directory(self, title: str):
        try:
            os.makedirs(title, exist_ok=False)
        except OSError:
            return

    def _download(self, mangadata, _tqdm, use_secondary_server=False):
        results = []
        for i in mangadata.chapters:
            fetch = MangadexChapterFetcher(i['chapter-id'])
            data = fetch.get()
            self._create_directory(os.path.join(self.output_folder, '%s/Vol. %s Ch. %s') % (
                mangadata.title,
                i['volume'],
                i['chapter']
            ))
            for manga in data:
                if use_secondary_server:
                    # force download if secondary url is not exist
                    if manga.secondary_url is None:
                        dl(
                            manga.primary_url,
                            self._get_file(
                                manga.title,
                                manga.volume,
                                manga.chapter,
                                manga.page
                            ),
                            verbose=False,
                            progressbar=False
                        )
                        results.append(manga)
                    else:
                        dl(
                            manga.secondary_url,
                            self._get_file(
                                manga.title,
                                manga.volume,
                                manga.chapter,
                                manga.page
                            ),
                            verbose=False,
                            progressbar=False
                        )
                        results.append(manga)
                else:
                    dl(
                        manga.primary_url,
                        self._get_file(
                            manga.title,
                            manga.volume,
                            manga.chapter,
                            manga.page
                        ),
                        verbose=False,
                        progressbar=False
                    )
                    results.append(manga)
            _tqdm.update(1)
        _tqdm.close()
        # Tachiyomi support
        self._logger_info('Downloading cover manga "%s"' % (mangadata.title))
        dl(mangadata.cover, self._get_cover(os.path.join(self.output_folder, mangadata.title)), verbose=False, progressbar=False)
        self._write_json(
            mangadata.title,
            mangadata.author,
            mangadata.artist,
            mangadata.description,
            mangadata.genres,
            mangadata.status
        )
        return results
        

    def download(self, *urls: str, use_secondary_server=False):
        """Download all mangas"""
        for url in urls:
            self.extract_info(url, True, use_secondary_server)

    def extract_info(
        self,
        url: str,
        download=True,
        use_secondary_server=False
    ):
        """Fetch manga information"""
        fetch = MangadexFetcher(url, self.lang)
        self._logger_info('Fetching "%s"' % (url))
        data = fetch.get()
        if download:
            self._logger_info('Downloading manga "%s"' % (data.title))
            t = tqdm.tqdm(
                desc='downloaded_chapters',
                total=len(data.chapters),
                unit='chapters'
            )
            self._create_directory(os.path.join(self.output_folder, data.title))
            chapters = self._download(data, t, use_secondary_server)
            for i in data.chapters:
                for a in chapters:
                    i['chapter-info'] = a
                    break
            return data
        else:
            return data
