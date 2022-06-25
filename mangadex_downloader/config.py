import json
import threading
import logging
import os
from pathlib import Path

from .language import Language
from .errors import MangaDexException

log = logging.getLogger(__name__)

_env_dir = os.environ.get('MANGADEXDL_CONFIG_DIR')
home_path = Path(_env_dir) if _env_dir is not None else Path.home()

# .mangadex-dl dir in home directory
base_path = home_path / '.mangadex-dl'

# Create config directory
try:
    base_path.mkdir(exist_ok=True, parents=True)
except Exception as e:
    raise MangaDexException(
        f"Failed to create config folder in '{base_path}'. " \
         "Make sure you have permission to read & write in that directory " \
         "or you can set MANGADEXDL_CONFIG_DIR to another path"
    ) from None

class _Config:
    path = base_path / 'config.json'
    default_conf = {
        "auth_cache": False,
        "language": Language.English.value # Enum object are not JSON serializable
    }

    def __init__(self):
        self._data = None
        self._lock = threading.Lock()

        # Load the config
        self._load()

    def __write(self, obj):
        """Write config file without lock"""
        self.path.write_text(json.dumps(obj))

    def _write_default(self):
        self.path.write_text(json.dumps(self.default_conf))

    def _load(self):
        with self._lock:
            success = False
            data = None

            # Very tricky lmao
            for attempt, _ in enumerate(range(5), start=1):
                try:
                    if not self.path.exists():
                        self._write_default()

                    data = json.loads(self.path.read_bytes())
                except json.JSONDecodeError as e:
                    log.error(
                        f'Failed to decode json data from config file = {self.path.resolve()} ' \
                        f'reason: {e}, retrying... (attempt: {attempt})'
                    )
                    # If somehow failed to decode JSON data, delete it and try it again
                    self.path.unlink(missing_ok=True)
                    continue
                except Exception as e:
                    log.error(
                        f'Failed to load json data from config file = {self.path.resolve()} ' \
                        f'reason: {e}, retrying... (attempt: {attempt})'
                    )
                else:
                    success = True
                    break

            if not success:
                raise MangaDexException(
                    f"Failed to load config file = {self.path}, " \
                    "make sure you have permission to write & read in that directory"
                )

            parsed_data = {}
            
            # Remove unnecessary config
            for key, value in data.items():
                if key in self.default_conf.keys():
                    parsed_data[key] = value
            
            self._data = parsed_data

            # Write new config
            self.__write(parsed_data)

    def read(self, name):
        self._load()
        return self._data[name]

    def write(self, name, value):
        """Write config file with lock"""
        with self._lock:
            self._data[name] = value
            self.__write(self._data)

_conf = _Config()

class ConfigProxy:
    def __getattr__(self, name: str):
        try:
            return _conf.read(name)
        except KeyError:
            raise AttributeError(f"type object '{_Config.__name__}' has no attribute '{name}'") from None
    
    def __setattr__(self, name, value):
        try:
            _conf.write(name, value)
        except KeyError:
            raise AttributeError(f"type object '{_Config.__name__}' has no attribute '{name}'") from None

# Allow to library to use _Config objects easily
config = ConfigProxy()