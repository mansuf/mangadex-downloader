"""
Download manga from mangadex directly with web scrapping.
"""

import os
import random
import tqdm
import json
import requests
from download import download as dl
from mangadex_downloader.fetcher import (
    MangadexFetcher,
    MangadexChapterFetcher
)


class Mangadex:
    def __init__(self, verbose=False, output_folder=''):
        self._verbose = verbose
        self.output_folder = output_folder

    def _logger_info_main(self, message):
        if self._verbose:
            print('[INFO] [MAIN] %s' % (message))
        else:
            return

    def _logger_warn_main(self, message):
        if self._verbose:
            print('[WARNING] [MAIN] %s' % (message))
        else:
            return

    def _logger_info_downloader(self, message):
        if self._verbose:
            print('[INFO] [DOWNLOADER] %s' % (message))
        else:
            return

    def _logger_warn_downloader(self, message):
        if self._verbose:
            print('[WARNING] [MAIN] %s' % (message))
        else:
            return

    def _get_file(self, manga_data):
        return os.path.join(self.output_folder, '%s/Vol. %s Ch. %s/%s.jpg') % (
            manga_data.title,
            manga_data.volume,
            manga_data.chapter,
            manga_data.page
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
            os.mkdir(title)
        except FileExistsError:
            return

    def _download(self, mangadata, use_secondary_server=False, data_saver=False):
        # Reverse the chapters to begin download from zero
        mangadata.chapters.reverse()
        missing_chapters = min([float(i['chapter']) for i in mangadata.chapters]) - 1
        if missing_chapters > 0:
            self._logger_warn_downloader('Manga "%s" is missing %s chapters' % (mangadata.title, int(missing_chapters)))
        for i in mangadata.chapters:
            fetch = MangadexChapterFetcher(i['id'], data_saver=data_saver)
            data = fetch.get()
            self._create_directory(os.path.join(self.output_folder, '%s/Vol. %s Ch. %s') % (
                mangadata.title,
                i['volume'],
                i['chapter']
            ))
            for manga in data:
                word = 'Downloading "%s" chapter %s/%s page %s/%s' % (
                    manga.title,
                    manga.chapter,
                    mangadata._get_total_chapters(),
                    manga.page,
                    len(data)
                )
                if use_secondary_server:
                    if manga.secondary_url is None:
                        self._logger_warn_downloader('Secondary server not found, forcing using primary server')
                        word += ' using primary server'
                    else:
                        word += ' using secondary server'
                else:
                    word += ' using primary server'
                if data_saver:
                    word += ' and data saver'
                if os.path.exists(self._get_file(manga)):
                    self._logger_info_downloader('Manga "%s" chapter %s page %s is already exist, skipping...' % (
                        mangadata.title,
                        manga.chapter,
                        manga.page
                    ))
                    continue
                self._logger_info_downloader(word)
                if use_secondary_server:
                    # force download if secondary url is not exist
                    if manga.secondary_url is None:
                        dl(manga.primary_url, self._get_file(manga), verbose=False)
                    else:
                        dl(manga.secondary_url, self._get_file(manga), verbose=False)
                else:
                    dl(manga.primary_url, self._get_file(manga), verbose=False)
        # Tachiyomi support
        self._logger_info_downloader('Downloading cover manga "%s"' % (mangadata.title))
        dl(mangadata.cover, self._get_cover(os.path.join(self.output_folder, mangadata.title)), verbose=False, progressbar=False)
        self._logger_info_downloader('Writing Manga information in details.json')
        self._write_json(
            mangadata.title,
            mangadata.author,
            mangadata.artist,
            mangadata.description,
            mangadata.genres,
            mangadata.status
        )
        self._logger_info_main('Finished download manga "%s"' % (mangadata.title))
        
    def extract_basic_info(self, url: str):
        """
        Fetch basic manga information
        without chapters
        """
        fetch = MangadexFetcher(url, self._verbose)
        self._logger_info_main('Fetching "%s"' % (url))
        return fetch.get(fetch_chapters=False)


    def download(self, *urls: str, use_secondary_server=False, data_saver=False):
        """Download all mangas"""
        for url in urls:
            self.extract_info(url, True, use_secondary_server, data_saver)

    def extract_info(
        self,
        url: str,
        download=True,
        use_secondary_server=False,
        data_saver=False
    ):
        """Fetch manga information"""
        fetch = MangadexFetcher(url, self._verbose)
        self._logger_info_main('Fetching "%s"' % (url))
        data = fetch.get()
        if download:
            self._logger_info_downloader('Downloading manga "%s"' % (data.title))
            self._create_directory(os.path.join(self.output_folder, data.title))
            self._download(data, use_secondary_server, data_saver)
            return data
        else:
            return data
