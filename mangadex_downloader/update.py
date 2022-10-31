# MIT License

# Copyright (c) 2022 Rahman Yusuf

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

import hashlib
import os
import re
import sys
import subprocess
import sys
import logging
import tempfile
import zipfile
import shutil
from packaging.version import parse as parse_version
from pathlib import Path

from .network import Net
from .downloader import FileDownloader
from . import __version__

current_version = parse_version(__version__)

log = logging.getLogger(__name__)

# A trick for checking if this in independent executable or not
executable = hasattr(sys, 'frozen')

is_64bits = sys.maxsize > 2**32

architecture = 'x64' if is_64bits else 'x86'

# Helper functions
def _get_api_tags():
    versions = []
    r = Net.requests.get('https://api.github.com/repos/mansuf/mangadex-downloader/git/refs/tags')
    for version_info in r.json():
        versions.append(version_info['ref'].replace('refs/tags/', ''))
    return versions

def _get_asset(_version):
    version = str(_version)
    if not version.startswith('v'):
        version = 'v' + version

    r = Net.requests.get('https://api.github.com/repos/mansuf/mangadex-downloader/releases')
    rinfo = None
    assets = None
    download_url = None
    file_hash = None
    filename = None
    for release_info in r.json():
        if version == release_info['tag_name']:
            rinfo = release_info
            assets = release_info['assets']
            break

    # Find download url
    for asset in assets:
        filename = 'mangadex-dl_{arch}_{version}.zip'.format(arch=architecture, version=version)
        if asset['name'] == filename:
            download_url = asset['browser_download_url']
            break
    
    re_hash = r'%s \| (?P<hash>.{1,}) \|' % filename.replace('.', '\\.')
    match = re.search(re_hash, rinfo['body'])
    file_hash = match.group('hash')

    return filename, download_url, file_hash

def check_version():
    # Get latest version
    try:
        versions = _get_api_tags()
        latest_version = parse_version(max(versions, key=parse_version))
    except Exception as e:
        log.error("Failed to check update, reason: %s" % e)
        return False

    if latest_version > current_version:
        return latest_version

    return None

def update_app():
    latest_version = check_version()

    if latest_version == False:
        sys.exit(1)

    if latest_version:

        log.info("Found latest version mangadex-downloader (v%s)" % latest_version)

        # Get url update
        try:
            filename, url_update, file_hash = _get_asset(latest_version)
        except Exception as e:
            log.error("Failed to get update url, reason: %s" % e) 
            sys.exit(1)

        current_path = Path(sys.executable).parent

        if executable:
            try:
                temp_folder = Path(tempfile.mkdtemp(suffix='md_downloader_update'))
            except Exception as e:
                log.error("Failed to create temporary folder, reason: %s" % e)
                sys.exit(1)

            update_file_path = str(temp_folder / filename)

            log.info("Downloading update v%s" % latest_version)
            # Download update
            try:
                fd = FileDownloader(url_update, update_file_path, use_requests=True)
                fd.download()
                fd.cleanup()
            except Exception as e:
                log.error("Failed to download update, reason: %s" % e)
                shutil.rmtree(temp_folder, ignore_errors=True)
                sys.exit(1)

            # Verify downloaded file
            log.info("Verifying update...")
            file_sha256 = hashlib.sha256()
            with open(update_file_path, 'rb') as o:
                file_sha256.update(o.read())
            
            if file_sha256.hexdigest() != file_hash:
                log.error("Failed to verify downloaded file, reason: File hash is not matching")
                shutil.rmtree(temp_folder, ignore_errors=True)
                sys.exit(1)

            log.info("Update file is verified")

            log.info("Installing update...")
            # Extract update
            try:
                with zipfile.ZipFile(update_file_path, 'r') as update:
                    update.extractall(Path(update_file_path).parent)
            except Exception as e:
                log.error("Failed to extract update, reason: %s" % e)
                shutil.rmtree(temp_folder, ignore_errors=True)
                sys.exit(1)

            extracted_update_path = str(temp_folder / 'mangadex-dl')

            install_script = open((temp_folder / "install.bat"), "w")
            install_script.write("@echo off\n")
            install_script.write("title mangadex-downloader updater\n")
            install_script.write("timeout 1 >nul 2>&1 \n")
            install_script.write("echo Updating mangadex-downloader from v%s to v%s\n" % (
                current_version,
                latest_version
            ))
            install_script.write("xcopy /S /E /Y \"%s\" \"%s\" >nul 2>&1 \n" % (extracted_update_path, current_path))
            install_script.write("start cmd /c \"rmdir /Q /S \"%s\"\"\n" % temp_folder)
            install_script.write("echo Successfully updated mangadex-downloader to v%s\n" % latest_version)
            install_script.write("echo You may close this window\n")
            install_script.write("pause >nul 2>&1 \n")
            install_script.write("exit\n")
            install_script.close()
            
            os.system("start cmd /c \"\"%s\"\"" % (temp_folder / "install.bat"))
            sys.exit(0)
        else:
            subprocess.run([
                sys.executable,
                '-m',
                'pip',
                'install',
                '-U',
                'mangadex-downloader',
            ])
    else:
        log.info('This version mangadex-downloader is up-to-date')


