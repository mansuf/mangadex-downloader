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

import threading
import base64
import json
import binascii
import logging
import traceback
import sys
import jwt
from datetime import datetime

from .env import *
from .config import *
from ..errors import MangaDexException

log = logging.getLogger(__name__)

__all__ = ("login_cache",)

class AuthCacheManager:
    path = base_path / 'auth.cache'
    default = {
        "session": {
            "token": None,
            "exp": None
        },
        "refresh": {
            "token": None,
            "exp": None
        }
    }
    fmt_exp_datetime = "%d:%m:%YT%H:%M:%S"
    delay_login_time = 30

    def __init__(self):
        self._data = None
        self._lock = threading.Lock()

        if config_enabled and config.login_cache:
            init()

        # Load the authentication cache
        self._load()

    def _parse_expired_time(self, data):
        """Convert string datetime to :class:`datetime.datetime` object"""
        exp_refresh_token = data['refresh']['exp']
        exp_session_token = data['session']['exp']

        parsed_exp_refresh_token = None
        if exp_refresh_token is not None:
            parsed_exp_refresh_token = datetime.strptime(
                exp_refresh_token,
                self.fmt_exp_datetime
            )

        parsed_exp_session_token = None
        if exp_session_token is not None:
            parsed_exp_session_token = datetime.strptime(
                exp_session_token,
                self.fmt_exp_datetime
            )

        data['refresh']['exp'] = parsed_exp_refresh_token
        data['session']['exp'] = parsed_exp_session_token

    def _read(self):
        if not self.path.exists():
            data = base64.b64encode(json.dumps(self.default).encode())
            self.path.write_bytes(data)

        data = self.path.read_bytes()
        decoded = base64.b64decode(data)
        final_data = json.loads(decoded)
        self._parse_expired_time(final_data)
        return final_data

    def _serialize_exp_time(self, obj):
        """Convert :class:`datetime.datetime` to formatted string"""
        exp_refresh_token = obj['refresh']['exp']
        exp_session_token = obj['session']['exp']

        serialized_exp_refresh_token = None
        if exp_refresh_token is not None:
            serialized_exp_refresh_token = exp_refresh_token.strftime(self.fmt_exp_datetime)

        serialized_exp_session_token = None
        if exp_session_token is not None:
            serialized_exp_session_token = exp_session_token.strftime(self.fmt_exp_datetime)

        obj['refresh']['exp'] = serialized_exp_refresh_token
        obj['session']['exp'] = serialized_exp_session_token

    def _write(self, obj):
        self._serialize_exp_time(obj)
        data = json.dumps(obj).encode()
        self.path.write_bytes(base64.b64encode(data))
        self._parse_expired_time(obj)
        self._data = obj

    def _load(self):
        if not config_enabled or not config.login_cache:
            self._data = self.default.copy()
            return

        success = False
        err = None
        data = None

        for attempt, _ in enumerate(range(5), start=1):
            try:
                data = self._read()
            except binascii.Error as e:
                err = e
                # Failed to decode base64
                log.error(
                    f"Failed to decode auth cache file, reason: {e}. " \
                    "Authentication cache file will be re-created and previous auth cached will be lost. " \
                    f"Recreating... (attempt: {attempt})"
                )
            except json.JSONDecodeError as e:
                err = e
                # Failed to deserialize json
                log.error(
                    f"Failed to deserialize json auth cache file, reason: {e}. " \
                    "Authentication cache file will be re-created and previous auth cached will be lost. " \
                    f"Recreating... (attempt: {attempt})"
                )
            except Exception as e:
                err = e
                # another error
                log.warning(
                    f"Failed to load auth cache file, reason: {e}. " \
                    "Authentication cache file will be re-created and previous auth cached will be lost. " \
                    f"Recreating... (attempt: {attempt})"
                )
            else:
                success = True
                break

            if not success:
                # Try to delete the auth cache file, and try it again
                try:
                    self.path.unlink(missing_ok=True)
                except Exception as e:
                    log.debug(f"Failed to delete auth cache file, reason: {e}")
                    pass

        if not success:
            exc = MangaDexException(
                f"Failed to load auth cache file ({self.path}), reason: {err}" \
                f"Make sure you have permission to read & write in that directory"
            )
            print("Traceback of last error when loading auth cache file", file=sys.stderr)
            traceback.print_exception(type(err), err, err.__traceback__, file=sys.stderr)

            raise exc

        self._data = data

    def _get_datetime_now(self) -> datetime:
        return datetime.now()

    def _reset_session_token(self):
        data = self._data.copy()

        data['session']['token'] = None
        data['session']['exp'] = None

        self._write(data)

    def _reset_refresh_token(self):
        data = self._data.copy()

        data['refresh']['token'] = None
        data['refresh']['exp'] = None

        self._write(data)

    def get_expiration_time(self, token):
        data = jwt.decode(token, options={'verify_signature': False})
        return datetime.fromtimestamp(data['exp'])

    def get_session_token(self):
        """Union[:class:`str`, ``None``]: A session token for authentication to MangaDex"""
        if not config_enabled or not config.login_cache:
            return

        with self._lock:
            self._load()
            token = self._data['session']['token']
            exp = self._data['session']['exp']
            now = self._get_datetime_now()

            if token is None and exp is None:
                return None

            if exp > now:
                # exp_time must have at least above 30 seconds (30 seconds for re-login)
                exp_time = (exp - now).total_seconds()

                if (exp_time - 30) <= 0:
                    # The expiration time is less than 30 seconds
                    # Mark is as expired
                    self._reset_session_token()
                    return None

                return token
            else:
                # Token is expired
                self._reset_session_token()
                return None

    def set_session_token(self, token):
        """Write session token to cache file
        
        Parameters
        -----------
        token: :class:`str`
            A valid session token
        """
        if not config_enabled or not config.login_cache:
            return

        with self._lock:
            data = self._data.copy()
            data['session']['token'] = token
            data['session']['exp'] = self.get_expiration_time(token)
            self._write(data)

    def get_refresh_token(self):
        """Union[:class:`str`, ``None``]: A refresh token for renew session token"""
        if not config_enabled or not config.login_cache:
            return

        with self._lock:
            self._load()
            token = self._data['refresh']['token']
            exp = self._data['refresh']['exp']
            now = self._get_datetime_now()

            if token is None and exp is None:
                return None

            if exp > now:
                return token
            else:
                # Token is expired
                self._reset_refresh_token()
                return None

    def set_refresh_token(self, token):
        """Write refresh token to cache file
        
        Parameters
        -----------
        token: :class:`str`
            A valid refresh token
        """
        if not config_enabled or not config.login_cache:
            return

        with self._lock:
            data = self._data.copy()
            data['refresh']['token'] = token
            data['refresh']['exp'] = self.get_expiration_time(token)
            self._write(data)

    def purge(self):
        """Purge session and refresh token cache"""
        if not config_enabled or not config.login_cache:
            return

        with self._lock:
            self._reset_session_token()
            self._reset_refresh_token()

login_cache = AuthCacheManager()