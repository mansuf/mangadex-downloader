import logging
from tqdm import tqdm
from pathlib import Path

from .legacy import DownloadTrackerJSON, FileInfo, ChapterInfo, ImageInfo
from .sqlite import DownloadTrackerSQLite

from ..utils import delete_file

log = logging.getLogger(__name__)

def _migrate_legacy_tracker_raw(
    legacy_tracker: DownloadTrackerJSON, 
    new_tracker: DownloadTrackerSQLite,
    manga_id: str,
    path: Path,
    progress_bar: tqdm
):
    fmt = legacy_tracker.format

    fi: FileInfo
    for fi in legacy_tracker.data["files"]:
        # File info
        new_tracker.add_file_info(
            name=fi.name,
            manga_id=manga_id,
            ch_id=fi.id,
            hash=fi.hash
        )

        if "single" in fmt or "volume" in fmt:
            # Chapter info
            ci_data = []
            ci: ChapterInfo
            for ci in fi.chapters:
                ci_data.append(
                    (ci.name, ci.id, fi.name)
                )
            new_tracker.add_chapters_info(ci_data)

        # Image info
        ii_data = []
        ii: ImageInfo
        for ii in fi.images:
            ii_data.append(
                (ii.name, ii.hash, ii.chapter_id, fi.name)
            )
        new_tracker.add_images_info(ii_data)

        new_tracker.toggle_complete(fi.name, True)
        progress_bar.update(1)

    delete_file(legacy_tracker.file)

def _migrate_legacy_tracker_any(
    legacy_tracker: DownloadTrackerJSON, 
    new_tracker: DownloadTrackerSQLite,
    manga_id: str,
    path: Path,
    progress_bar: tqdm
):
    fmt = legacy_tracker.format

    fi: FileInfo
    for fi in legacy_tracker.data["files"]:
        # File info
        new_tracker.add_file_info(
            name=fi.name,
            manga_id=manga_id,
            ch_id=fi.id,
            hash=fi.hash
        )

        if "single" in fmt or "volume" in fmt:
            # Chapter info
            ci_data = []
            ci: ChapterInfo
            for ci in fi.chapters:
                ci_data.append(
                    (ci.name, ci.id, fi.name)
                )
            new_tracker.add_chapters_info(ci_data)

        new_tracker.toggle_complete(fi.name, True)
        progress_bar.update(1)

    delete_file(legacy_tracker.file)

def _migrate_legacy_tracker(fmt, path):
    from ..chapter import Chapter

    new_tracker = DownloadTrackerSQLite(fmt, path)
    legacy_tracker = DownloadTrackerJSON(fmt, path)

    if legacy_tracker.empty:
        # We don't wanna migrate if it's empty
        # Just delete the old tracker file
        delete_file(legacy_tracker.file)
        del legacy_tracker

        return

    log.info("Legacy download tracker detected, migrating to new one...")
    log.warning(
        "Do not turn it off while migrating " \
        "or the migration will be failed and download tracker data will be lost"
    )
    progress_bar = tqdm(
        total=len(legacy_tracker.data["files"]),
        unit="files",
        desc="progress"
    )

    manga_id = None
    chapter_id = None

    # Since we only want to get manga id from old tracker
    # (because the old tracker doesn't have manga id)
    # we just fetch from single chapter id to prevent rate-limited from the API
    fi = legacy_tracker.data["files"][0]
    if "single" in fmt or "volume" in fmt:
        # Any `single` or `volume` formats
        # (raw-single, raw-volume, etc)
        for chapter_info in fi.chapters:
            chapter_id = chapter_info.id
            break
    else:
        # Any `chapter` formats
        # (raw, pdf, epub, etc)
        chapter_id = fi.id

    chapter = Chapter(_id=chapter_id)
    manga_id = chapter.manga_id

    args_migrate = (
        legacy_tracker,
        new_tracker,
        manga_id,
        path,
        progress_bar
    )

    # Begin migrating
    if "raw" in fmt:
        _migrate_legacy_tracker_raw(*args_migrate)
    else:
        _migrate_legacy_tracker_any(*args_migrate)

    return new_tracker

def get_tracker(fmt, path):
    # return DownloadTrackerSQLite(fmt, path)

    legacy_path = DownloadTrackerJSON.get_tracker_path(fmt, path)
    if legacy_path.exists():
        return _migrate_legacy_tracker(fmt, path)

    return DownloadTrackerSQLite(fmt, path)