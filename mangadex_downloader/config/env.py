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

import zipfile
import os
from pathlib import Path

from .utils import *
from ..errors import MangaDexException

__all__ = (
    "env", "base_path", "config_enabled", "init"
)

class EnvironmentVariables:
    # 4 values of tuple
    # (key_env: string, default_value: Any, validator_function: Callable, lazy_loading: boolean)
    _vars = [
        [
            'config_enabled',
            False,
            validate_bool,
            False,
        ],
        [
            'config_path',
            None,
            dummy_validator,
            False,
        ],
        [
            'zip_compression_type',
            zipfile.ZIP_STORED,
            validate_zip_compression_type,
            False,
        ],
        [
            'zip_compression_level',
            None,
            validate_int,
            False,
        ],
        [
            'user_blacklist',
            tuple(),
            validate_blacklist,
            False,
        ],
        [
            'group_blacklist',
            tuple(),
            validate_blacklist,
            False,
        ],
        [
            'tags_blacklist',
            tuple(),
            lambda x: validate_blacklist(x, validate_tag),
            
            # We need to use lazy loading for env MANGADEXDL_TAGS_BLACKLIST
            # to prevent "circular imports" problem when using `requestsMangaDexSession`.
            # Previously, it was using `requests.Session`
            # which is not respecting rate limit system from MangaDex API
            True,
        ]
    ]

    def __init__(self):
        self.data = {}

        for key, default_value, validator, lazy_loading in self._vars:
            env_key = f'MANGADEXDL_{key.upper()}'
            env_value = os.environ.get(env_key)
            if env_value is not None:
                if lazy_loading:
                    self.data[key] = LazyLoadEnv(env_key, env_value, validator)
                    continue

                self.data[key] = load_env(env_key, env_value, validator)
            else:
                self.data[key] = default_value
        
    def read(self, name):
        try:
            value = self.data[name]
        except KeyError:
            # This should not happened
            # unless user is hacking in the internal API
            raise MangaDexException(f'environment variable "{name}" is not exist')
        
        if not isinstance(value, LazyLoadEnv):
            return value
        
        self.data[name] = value.load()
        return self.data[name]

_env_orig = EnvironmentVariables()

class EnvironmentVariablesProxy:
    def __getattr__(self, name):
        return _env_orig.read(name)

    def __setattr__(self, name, value):
        raise NotImplementedError

# Allow library to get values from attr easily
env = EnvironmentVariablesProxy()

_env_dir = env.config_path
base_path = Path(_env_dir) if _env_dir is not None else (Path.home() / '.mangadex-dl')

_env_conf_enabled = env.config_enabled
try:
    config_enabled = validate_bool(_env_conf_enabled)
except ConfigTypeError:
    raise MangaDexException(
        f"Failed to load env MANGADEXDL_CONFIG_ENABLED, value '{_env_conf_enabled}' is not valid boolean value"
    )

def init():
    # Create config directory
    try:
        base_path.mkdir(exist_ok=True, parents=True)
    except Exception as e:
        raise MangaDexException(
            f"Failed to create config folder in '{base_path}', " \
            f"reason: {e}. Make sure you have permission to read & write in that directory " \
            "or you can set MANGADEXDL_CONFIG_DIR to another path " \
            "or you can disable config with MANGADEXDL_CONFIG_ENABLED=0"
        ) from None

