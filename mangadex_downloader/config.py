import json
import threading
import logging
import os
from pathlib import Path

from . import format as fmt
from .language import Language, get_language
from .errors import MangaDexException
from .cover import default_cover_type, valid_cover_types

log = logging.getLogger(__name__)

class ConfigTypeError(MangaDexException):
    pass

# Utilities
def _validate_bool(val):
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

def _validate_language(val):
    lang = get_language(val)
    return lang.value

def _validate_cover(val):
    if val not in valid_cover_types:
        raise ConfigTypeError(f"'{val}' is not valid cover type")
    
    return val

def _validate_format(val):
    fmt.get_format(val)
    return val

_env_dir = os.environ.get('MANGADEXDL_CONFIG_DIR')
home_path = Path(_env_dir) if _env_dir is not None else Path.home()
config_enabled = _validate_bool(os.environ.get('MANGADEXDL_CONFIG_ENABLED'))

# .mangadex-dl dir in home directory
base_path = home_path / '.mangadex-dl'

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

class _Config:
    path = base_path / 'config.json'
    confs = {
        "login_cache": [
            False, # default value
            _validate_bool, # validator value
        ],
        "language": [
            Language.English.value, # Enum object are not JSON serializable
            _validate_language,
        ],
        "cover": [
            default_cover_type,
            _validate_cover
        ],
        "unsafe": [
            False, # unsafe always False
            _validate_bool
        ],
        "save_as": [
            fmt.default_save_as_format,
            _validate_format
        ],
        "use_chapter_title": [
            False,
            _validate_bool
        ],
        "use_compressed_image": [
            False,
            _validate_bool
        ],
    }
    default_conf = {
        x: y for x, (y, _) in confs.items()
    }

    def __init__(self):
        self._data = None
        self._lock = threading.Lock()

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
            default_value, validator = self.confs[conf_key]

            try:
                validator(conf_value)
            except Exception as e:
                # If somehow config file is messed up
                # because validator is failed to pass the test
                # fallback to default value
                log.debug(
                    f"Config '{conf_key}' (value: {conf_value}) is not passed validator test, " \
                    f"reason: {e}. Falling back to default value"
                )
                data[conf_key] = default_value

        self._data = data

        if config_enabled and write_to_path:
            self.path.write_text(json.dumps(data))

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

                    data = json.loads(self.path.read_bytes())
                except json.JSONDecodeError as e:
                    err = e
                    log.error(
                        f'Failed to decode json data from config file = {self.path.resolve()} ' \
                        f'reason: {e}, retrying... (attempt: {attempt})'
                    )
                    # If somehow failed to decode JSON data, delete it and try it again
                    self.path.unlink(missing_ok=True)
                    continue
                except Exception as e:
                    err = e
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
                    f"reason: {err}. Make sure you have permission to write & read in that directory"
                )

            # Write new config
            self._write(data)

    def read(self, name):
        self._load()
        return self._data[name]

    def write(self, name, value):
        """Write config file with lock"""
        if not config_enabled:
            raise MangaDexException(
                "Config is not enabled. " \
                "You can enable it by set MANGADEXDL_CONFIG_ENABLED to 1"
            )

        with self._lock:
            obj = self._data.copy()
            obj[name] = value
            self._write(obj)

_conf = _Config()

def set_config_from_cli_opts(args):
    """Set config from cli opts"""
    data = {}
    for key in _conf.default_conf.keys():
        value = getattr(args, key)
        _, validator = _conf.confs[key]
        data[key] = validator(value)
    
    _conf._write(data, write_to_path=False)

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
            raise AttributeError(f"type object '{_Config.__name__}' has no attribute '{name}'") from None
    
    def __setattr__(self, name, value):
        try:
            _, validator = _conf.confs[name]
        except KeyError:
            raise AttributeError(f"type object '{_Config.__name__}' has no attribute '{name}'") from None

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