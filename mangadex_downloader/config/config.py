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

import threading
import logging
from requests_doh import get_all_dns_provider

from .env import base_path, config_enabled, init
from .utils import (
    validate_bool,
    validate_language,
    validate_value_from_iterator,
    validate_format,
    validate_dummy,
    validate_doh_provider,
    validate_sort_by,
    validate_http_retries,
    validate_download_mode,
    validate_stacked_progress_bar_order,
    validate_group_nomatch_behaviour,
    validate_log_level,
    validate_progress_bar_layout,
    validate_int,
    validate_order,
    convert_string_lowercase,
    ConfigTypeError,
)
from .. import format as fmt, json_op
from ..cover import default_cover_type, valid_cover_types
from ..language import Language
from ..errors import MangaDexException

# Fix #28
_doh_providers = [None]
_doh_providers.extend(get_all_dns_provider())

log = logging.getLogger(__name__)

__all__ = (
    "set_config_from_cli_opts",
    "reset_config",
    "get_all_configs",
    "config",  # High-level access for normal use
    "_conf",  # Low-level access for debugging
)


class _Config:
    path = base_path / "config.json"
    confs = {
        # 2 values in tuple in config keys
        # (default_value, validator_function)
        "login_cache": (
            False,
            validate_bool,
        ),
        "language": (
            Language.English.value,
            validate_language,
        ),
        "cover": (
            default_cover_type,
            lambda x: validate_value_from_iterator(x, valid_cover_types),
        ),
        "save_as": (fmt.default_save_as_format, validate_format),
        "use_chapter_title": (False, validate_bool),
        "use_compressed_image": (False, validate_bool),
        "force_https": (False, validate_bool),
        "path": ("./{manga.title}", validate_dummy),
        "filename_chapter": ("{chapter.simple_name}{file_ext}", validate_dummy),
        "filename_volume": ("Vol. {volume}{file_ext}", validate_dummy),
        "filename_single": ("All chapters{file_ext}", validate_dummy),
        "dns_over_https": (None, validate_doh_provider),
        "no_group_name": (False, validate_bool),
        "sort_by": ("volume", validate_sort_by),
        "http_retries": (5, validate_http_retries),
        "download_mode": ("default", validate_download_mode),
        "use_chapter_cover": (False, validate_bool),
        "use_volume_cover": (False, validate_bool),
        "no_track": (False, validate_bool),
        "volume_cover_language": (None, validate_language),
        "stacked_progress_bar_order": (
            "volumes, chapters, pages, file sizes, convert",
            validate_stacked_progress_bar_order,
        ),
        "log_level": ("INFO", validate_log_level),
        "progress_bar_layout": ("default", validate_progress_bar_layout),
        "ignore_missing_chapters": (False, validate_bool),
        "create_no_volume": (False, validate_bool),
        "create_manga_info": (False, validate_bool),
        "manga_info_format": ("csv", convert_string_lowercase),
        "manga_info_filepath": (
            "{download_path}/manga_info.{manga_info_format}",
            validate_dummy,
        ),
        "manga_info_only": (False, validate_bool),
        "no_metadata": (False, validate_bool),
        "page_size": (0, validate_int),
        "order": ("newest", validate_order),
        "group_nomatch_behaviour": ("ignore", validate_group_nomatch_behaviour),
        "upscale": (False, validate_bool),
        "upscale_scale": (2, validate_int),
        "upscale_concurrency": (2, validate_int),
    }
    default_conf = {x: y for x, (y, _) in confs.items()}

    def __init__(self):
        self._data = None
        self._lock = threading.Lock()
        self.no_read = False

        # Load the config
        self._load()

    def _write(self, obj, write_to_path=True):
        """Write config file without lock"""
        data = {}

        # Remove unnecessary config
        for d_key, d_value in self.default_conf.items():
            found = False
            for key, value in obj.items():
                if key == d_key:
                    data[d_key] = value
                    found = True
                    break

            if not found:
                # Pass the default config
                data[d_key] = d_value

        # Validation tests
        for conf_key, conf_value in obj.items():
            try:
                default_value, validator = self.confs[conf_key]
            except KeyError:
                # Backward compatibility support to prevent crash
                continue

            try:
                validator(conf_value)
            except Exception as e:
                # If somehow config file is messed up
                # because validator is failed to pass the test
                # fallback to default value
                log.debug(
                    f"Config '{conf_key}' (value: {conf_value}) "
                    "is not passed validator test, "
                    f"reason: {e}. Falling back to default value"
                )
                data[conf_key] = default_value

        self._data = data

        if config_enabled and write_to_path:
            self.path.write_text(json_op.dumps(data))

    def _write_default(self):
        self._write(self.default_conf)

    def _load(self):
        # Initialize config
        if config_enabled:
            init()

        if not config_enabled:
            # If config is not enabled
            # use default config
            # useful for passing default arguments in argparse
            if self._data is None:
                self._write_default()

            return

        with self._lock:
            success = False
            err = None
            data = None

            # Very tricky lmao
            for attempt, _ in enumerate(range(5), start=1):
                try:
                    if not self.path.exists():
                        self._write_default()

                    data = json_op.loads(self.path.read_bytes())
                except json_op.JSONDecodeError as e:
                    err = e
                    log.error(
                        "Failed to decode json data "
                        f"from config file = {self.path.resolve()} "
                        f"reason: {e}, retrying... (attempt: {attempt})"
                    )
                    # If somehow failed to decode JSON data, delete it and try it again
                    self.path.unlink(missing_ok=True)
                    continue
                except Exception as e:
                    err = e
                    log.error(
                        f"Failed to load json data "
                        f"from config file = {self.path.resolve()} "
                        f"reason: {e}, retrying... (attempt: {attempt})"
                    )
                else:
                    success = True
                    break

            if not success:
                raise MangaDexException(
                    f"Failed to load config file = {self.path}, reason: {err}. "
                    "Make sure you have permission to write & read in that directory"
                )

            # Write new config
            self._write(data)

    def read(self, name):
        if not self.no_read:
            self._load()
        return self._data[name]

    def write(self, name, value):
        """Write config file with lock"""
        if not config_enabled and not self.no_read:
            raise MangaDexException(
                "Config is not enabled. "
                "You can enable it by set MANGADEXDL_CONFIG_ENABLED to 1"
            )

        with self._lock:
            obj = self._data.copy()
            obj[name] = value
            self._write(obj, write_to_path=not self.no_read)


_conf = _Config()


def set_config_from_cli_opts(args):
    """Set config from cli opts"""
    data = {}
    for key in _conf.default_conf.keys():
        value = getattr(args, key)
        _, validator = _conf.confs[key]
        value = validator(value)
        data[key] = value
        setattr(args, key, value)

    _conf._write(data, write_to_path=False)
    _conf.no_read = True


def reset_config(name=None):
    """Reset config. If ``name`` is not given, reset all configs"""
    if not name:
        _conf._write(_conf.default_conf)
    else:
        try:
            default_value = _conf.default_conf[name]
        except KeyError:
            raise AttributeError(
                f"type object '{_Config.__name__}' has no attribute '{name}'"
            ) from None

        _conf.write(name, default_value)


def get_all_configs():
    """Return a generator that will yield ``(config_name, config_value)``"""
    return _conf._data.items()


class ConfigProxy:
    def __getattr__(self, name: str):
        try:
            return _conf.read(name)
        except KeyError:
            raise AttributeError(
                f"type object '{_Config.__name__}' has no attribute '{name}'"
            ) from None

    def __setattr__(self, name, value):
        try:
            _, validator = _conf.confs[name]
        except KeyError:
            raise AttributeError(
                f"type object '{_Config.__name__}' has no attribute '{name}'"
            ) from None

        try:
            val = validator(value)
        except Exception as e:
            # Provide more details about error
            # Which config triggered this
            err = f"{name}: " + str(e)
            raise ConfigTypeError(err) from None

        _conf.write(name, val)


# Allow to library to use _Config objects easily
config = ConfigProxy()
