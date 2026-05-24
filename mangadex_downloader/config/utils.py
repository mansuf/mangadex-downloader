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

import logging
import zipfile
import os
import typing
from dataclasses import dataclass
from urllib.parse import urlparse
from requests_doh import get_all_dns_provider, add_dns_provider

from .. import format as fmt
from ..errors import MangaDexException, InvalidURL
from ..language import get_language
from ..utils import validate_url
from ..progress_bar import progress_bar_manager

__all__ = (
    "validate_bool",
    "validate_order",
    "validate_language",
    "validate_value_from_iterator",
    "validate_format",
    "validate_dummy",
    "validate_zip_compression_type",
    "validate_int",
    "validate_tag",
    "validate_blacklist",
    "validate_sort_by",
    "validate_http_retries",
    "validate_download_mode",
    "validate_doh_provider",
    "validate_log_level",
    "validate_progress_bar_layout",
    "validate_stacked_progress_bar_order",
    "validate_group_nomatch_behaviour",
    "validate_upscale_scale",
    "load_env",
    "LazyLoadEnv",
    "ConfigTypeError",
    "convert_string_lowercase",
)

log = logging.getLogger(__name__)


class ConfigTypeError(MangaDexException):
    pass


# Utilities
def convert_string_lowercase(val):
    if isinstance(val, str):
        return val.lower()
    else:
        return str(val).lower()


def validate_bool(val):
    if isinstance(val, str):
        value = val.strip().lower()

        # Is it 1 or 0 ?
        try:
            return bool(int(value))
        except ValueError:
            pass

        # This is dumb
        if value == "true":
            return True
        elif value == "false":
            return False
        else:
            raise ConfigTypeError(f"'{val}' is not valid boolean value")
    else:
        return bool(val)


def validate_language(val):
    lang = get_language(val)
    return lang.value


def validate_value_from_iterator(val, iterator):
    values = [i for i in iterator]
    if val not in values:
        raise ConfigTypeError(
            f"'{val}' is not valid value, available values are {values}"
        )

    return val


def validate_format(val):
    fmt.get_format(val)
    return val


def validate_dummy(val):
    return val


def validate_zip_compression_type(val):
    types = {
        "stored": zipfile.ZIP_STORED,
        "deflated": zipfile.ZIP_DEFLATED,
        "bzip2": zipfile.ZIP_BZIP2,
        "lzma": zipfile.ZIP_LZMA,
    }

    try:
        return types[val]
    except KeyError:
        raise ConfigTypeError(f"zip compression type '{val}' is not valid")


def validate_int(val):
    try:
        return int(val)
    except ValueError:
        raise ConfigTypeError(f"'{val}' is not valid integer")

def validate_upscale_scale(val):
    val = validate_int(val)
    if val not in [2, 4]:
        raise ConfigTypeError(
            f"Upscale scale must be 2 or 4, got {val}"
        )
    return val

def validate_tag(tag):
    # "Circular imports" problem smh
    from ..tag import get_all_tags

    tags = {i.name.lower(): i for i in get_all_tags()}

    # Keyword
    try:
        t = tags[tag]
    except KeyError:
        pass
    else:
        return t.id

    # UUID
    return validate_url(tag)


def validate_blacklist(val, validate=validate_url):
    values = [i.strip() for i in val.split(",")]

    blacklisted = []
    for url in values:
        if os.path.exists(url):
            fp = open(url, "r")
            try:
                content = [validate(i) for i in fp.read().splitlines()]
            except InvalidURL as e:
                # Verbose error
                # Provide more useful information rather than
                # "invalid url, {url} is not valid MangaDex url"
                raise MangaDexException(f'Invalid url detected in file "{url}", {e}')
            finally:
                fp.close()
        else:
            content = [validate(url)]

        blacklisted.extend(content)

    return blacklisted


def validate_sort_by(val):
    sort_by = ["volume", "chapter"]
    if val not in sort_by:
        raise ConfigTypeError(f"'{val}' is not valid sort by value, must be {sort_by}")

    return val


def validate_http_retries(val):
    try:
        return int(val)
    except ValueError:
        # Not a number
        pass

    val = val.lower().strip()

    if val != "unlimited":
        raise ConfigTypeError(
            f"'{val}' is not valid 'http_retries' value, it must be numbers or 'unlimited'"
        )

    return val


def validate_download_mode(val):
    val = val.lower().strip()

    if val not in ["default", "unread"]:
        raise ConfigTypeError(
            f"'{val}' is not valid 'download_mode' value, it must be 'default' or 'unread'"
        )

    return val


def validate_doh_provider(val):
    providers = [None]
    providers.extend(get_all_dns_provider())
    try:
        validate_value_from_iterator(val, providers)
    except ConfigTypeError:
        pass
    else:
        return val

    try:
        parsed = urlparse(val)
    except Exception as e:
        log.debug(
            "Failed to parse url from validate_doh_provider",
            exc_info=e,
            stack_info=True,
        )
        raise ConfigTypeError(
            f"'{val}' is not valid DoH providers, available values are {providers}"
        )

    # Validate HTTP(s) URL
    # https://stackoverflow.com/a/38020041
    valid_http = [parsed.scheme in ["http", "https"], parsed.netloc]
    if not any(valid_http):
        raise ConfigTypeError(
            f"'{val}' is not valid DoH providers, available values are {providers}"
        )

    # Create new DoH provider
    add_dns_provider("custom-doh", val, switch=True)

    return "custom-doh"


def load_env(env_key, env_value, validator):
    try:
        return validator(env_value)
    except Exception as e:
        raise MangaDexException(
            f"An error happened when validating env {env_key}. " f"Reason: {e}"
        ) from None


# A utility class as indicator for lazy load environments in `EnvironmentVariables` class
@dataclass
class LazyLoadEnv:
    env_key: str
    env_value: str
    validator: typing.Callable

    def load(self):
        return load_env(self.env_key, self.env_value, self.validator)


valid_output_modes = ["logger", "stacked-progress-bar", "progress-bar"]

valid_stacked_progress_bar_types = [
    "volumes",
    "chapters",
    "pages",
    "file sizes",
    "converted files",
]


def validate_log_level(val):
    val = val if isinstance(val, int) else val.upper()
    log_level = logging.getLevelName(val)
    if log_level == f"Level {val}":
        # Instead of raising exception,
        # logging.getLevelName will return string "Level {level}"
        raise ConfigTypeError(f"{val!r} is not valid logger level")

    log = logging.getLogger("mangadex_downloader")
    log.setLevel(log_level)
    return val


def validate_progress_bar_layout(val):
    valid_progress_bar_layouts = ["default", "stacked", "none"]
    if val not in valid_progress_bar_layouts:
        raise ConfigTypeError(f"'{val}' is not valid progress bar layout")

    if val == "none":
        progress_bar_manager.disabled = True

    return val


def validate_stacked_progress_bar_order(val):
    if isinstance(val, str):
        values = (i.strip() for i in val.split(","))
        values = [value for value in values if value]
    else:
        values = val

    for value in values:
        if value not in progress_bar_manager.valid_types_order:
            raise ConfigTypeError(f"'{val}' is not valid stacked progress bar order")

    progress_bar_manager.set_types_order(*values)
    return values


def validate_order(val):
    val = val.strip().lower()
    if val not in ["newest", "oldest"]:
        raise ConfigTypeError(f"'{val}' is not valid order")

    return val


def validate_group_nomatch_behaviour(val):
    val = val.strip().lower()
    if val not in ["ignore", "fallback"]:
        raise ConfigTypeError(f"'{val}' is not valid order")

    return val
