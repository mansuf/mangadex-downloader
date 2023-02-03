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

# Based on https://github.com/mansuf/zippyshare-downloader/blob/main/zippyshare_downloader/network.py

import requests
import itertools
import urllib.parse
import time
import logging
import sys
import threading
from . import __version__, __repository__
from .errors import (
    AlreadyLoggedIn,
    HTTPException,
    LoginFailed,
    MangaDexException,
    NotLoggedIn,
    UnhandledHTTPError
)
from .auth import OAuth2, LegacyAuth
from .utils import QueueWorker
from requests_doh import DNSOverHTTPSAdapter, set_dns_provider
from concurrent.futures import Future, TimeoutError

try:
    import orjson
except ImportError:
    have_orjson = False
else:
    have_orjson = True

# Apply json loader into :class:`requests.Response`
def loads_json(self):
    return orjson.loads(self.content)

if have_orjson:
    requests.Response.json = loads_json

DEFAULT_RATE_LIMITED_TIMEOUT = 120

log = logging.getLogger(__name__)

__all__ = (
    'Net', 'NetworkManager',
    'set_proxy', 'clear_proxy',
    'base_url', 'uploads_url'
)

base_url = 'https://api.mangadex.org'
auth_url = 'https://auth.mangadex.org'
origin_url = 'https://mangadex.org'
uploads_url = 'https://uploads.mangadex.org'
forums_url = 'https://forums.mangadex.org'

# A utility to get shortened url from full URL
# (scheme, netloc, and path only)
def _get_netloc(url):
    result = urllib.parse.urlparse(url)
    return result.scheme + '://' + result.netloc + result.path

class ModifiedSession(requests.Session):
    """Modified requests session with ability to set timeout for each requests"""
    def __init__(self):
        super().__init__()

        self._timeout = None

    def set_timeout(self, time):
        self._timeout = time

    def send(self, r, **kwargs):
        kwargs.update({'timeout': self._timeout})
        return super().send(r, **kwargs)

class requestsMangaDexSession(ModifiedSession):
    # For be able inside class can access global variables in network.py module
    base_url = base_url
    auth_url = auth_url
    origin_url = origin_url
    uploads_url = uploads_url
    forums_url = forums_url

    """A requests session for MangaDex only. 

    Sending other HTTP(s) requests to other sites will break the session
    """
    def __init__(self, trust_env=True, auth_cls=LegacyAuth) -> None:
        # "Circular imports" problem
        from .config import login_cache, config_enabled, config

        super().__init__()
        self.trust_env = trust_env
        self.user = None
        self.delay = None
        self.config = config
        user_agent = 'mangadex-downloader {0} (https://github.com/mansuf/mangadex-downloader) '.format(__version__)
        user_agent += 'Python/{0[0]}.{0[1]} '.format(sys.version_info)
        user_agent += 'requests/{0}'.format(
            requests.__version__
        )
        self.headers = {
            "User-Agent": user_agent
        }
        self._session_token = None
        self._refresh_token = None

        self._config_enabled = config_enabled
        self._login_cache = login_cache

        # For auto-renew login
        # i ran out of ideas how to name this
        # so i name it _login_fut
        self._login_fut = Future()

        # QueueWorker for MangaDex network report
        self._worker_report = QueueWorker()
        self._worker_report.start()

        # To prevent conflict with `requests.Session.auth`
        self.api_auth = auth_cls(self)

    def set_auth(self, auth_cls):
        self.api_auth = auth_cls(self)

    def login_from_cache(self):
        if self.check_login():
            raise AlreadyLoggedIn("User already logged in")
        
        session_token = self._login_cache.get_session_token()
        refresh_token = self._login_cache.get_refresh_token()

        if session_token and refresh_token is None:
            # We assume this as invalid
            # Because we can login to MangaDex with session token
            # But, we cannot renew the session because refresh token is missing
            return

        elif session_token is None and refresh_token is None:
            # No cached token
            return

        log.info("Logging in to MangaDex from cache")

        if session_token is None and refresh_token:
            log.debug("Session token in cache is expired, renewing...")

            # Session token is expired and refresh token is exist
            # Renew login with refresh token
            self._refresh_token = refresh_token
            self.api_auth.update_token(refresh=refresh_token)
            self.refresh_login()
        else:
            # Session and refresh token are still valid in cache
            # Login with this
            self._update_token(
                {
                    "refresh": refresh_token,
                    "session": session_token
                }
            )

        # Start "auto-renew session token" process
        self._start_renew_login()

        log.info("Logged in to MangaDex")

    def _request(self, attempt, *args, **kwargs):
        try:
            resp = super().request(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            log.error("Failed connect to \"%s\", reason: %s. Trying... (attempt: %s)" % (
                _get_netloc(e.request.url),
                str(e),
                attempt
            ))
            return None
        except requests.exceptions.ReadTimeout as e:
            log.error("Failed connect to '%s', reason: Connection timed out. Trying... (attempt: %s)" % (
                _get_netloc(e.request.url),
                attempt
            ))
            return None

        # We are being rate limited
        if resp.status_code == 429:

            # x-ratelimit-retry-after is from MangaDex and
            # Retry-After is from DDoS-Guard
            if resp.headers.get('x-ratelimit-retry-after'):
                delay = float(resp.headers.get('x-ratelimit-retry-after')) - time.time()
            
            elif resp.headers.get('Retry-After'):
                delay = float(resp.headers.get('Retry-After'))
            else:
                # Somehow `x-ratelimit-retry-after` and `Retry-After` header are not exist
                # and they sending 429 response which should be marked as rate limited
                # Since we have no idea how many seconds we should do for `time.sleep()`
                # the app is sleeping for 120 seconds if happened like this, 
                delay = DEFAULT_RATE_LIMITED_TIMEOUT

            log.info('We being rate limited, sleeping for %0.2f (attempt: %s)' % (delay, attempt))
            time.sleep(delay)
            return None

        # Server error
        elif resp.status_code >= 500:
            url = _get_netloc(resp.url)
            if 'mangadex.network' in url and 'api.mangadex.network/report' not in url:
                # Return here anyway to not wasting time to retry to faulty node
                return resp

            log.info(
                f"Failed to connect to \"{url}\", " \
                f"reason: Server throwing error code {resp.status_code}. "  \
                f"Trying... (attempt: {attempt})"
            )
            return None

        return resp

    # Ratelimit handler
    def request(self, *args, **kwargs):
        attempt = 1
        resp = None
        retries = self.config.http_retries

        if isinstance(retries, int):
            iterator = range(retries)
        else:
            iterator = itertools.count()

        for _ in iterator:
            resp = self._request(attempt, *args, **kwargs)

            if self.delay:
                delay = self.delay
            elif resp is not None:
                delay = None
            elif attempt >= 5:
                # We don't wanna go further
                delay = 2.5
            else:
                delay = attempt * 0.5

            if delay:
                time.sleep(delay)

            if resp is not None:
                return resp

            attempt += 1
            continue

        if resp is not None and resp.status_code >= 500:
            # 5 attempts request failed caused by server error
            # raise error
            raise HTTPException('Server sending %s code' % resp.status_code, resp=resp)

        raise UnhandledHTTPError("Unhandled HTTP error")

    def _update_token(self, token):
        session_token = token['session']
        refresh_token = token['refresh']

        self._refresh_token = refresh_token
        self._session_token = session_token
        self.headers['Authorization'] = 'Bearer %s' % session_token

        self._login_cache.set_refresh_token(refresh_token)
        self._login_cache.set_session_token(session_token)

    def _is_token_cached(self):
        return bool(self._login_cache.get_session_token or self._login_cache.get_refresh_token())

    def _reset_token(self):
        self._refresh_token = None
        self._session_token = None
        self.headers.pop('Authorization')

    def _notify_login_fut(self):
        """Usually this will be called when :meth:`requestsMangaDexSession.logout()` 
        is called to stop auto-renew login process
        """
        self._login_fut.set_result(True)
    
    def _renew_login(self):
        """Renew login process

        Wait session token until 30 seconds expiration time (for re-login)
        and then renew the session token
        """
        while True:
            exp_time = (
                self._login_cache.get_expiration_time(self._session_token) -
                self._login_cache._get_datetime_now()
            ).total_seconds()
            delay = exp_time - self._login_cache.delay_login_time
            try:
                logout = self._login_fut.result(delay)
            except TimeoutError:
                logout = False

            # Time has expired
            if not logout:
                self.refresh_login()
            # self.logout() is called
            else:
                break

    def refresh_login(self):
        """Refresh login session with refresh token"""
        if self._refresh_token is None:
            raise LoginFailed("User are not logged in")
        
        new_token = self.api_auth.refresh_token()
        self._update_token(new_token)

    def check_login(self):
        """Check if user are still logged in"""
        if self._refresh_token is None and self._session_token is None:
            return False

        return self.api_auth.check_login()

    def login(self, password, username=None, email=None):
        """Login to MangaDex"""
        # Raise error if already logged in
        if self.check_login():
            raise AlreadyLoggedIn("User already logged in")

        log.info('Logging in to MangaDex')

        token = self.api_auth.login(username, email, password)
        self._update_token(token)

        self._start_renew_login()

        log.info("Logged in to MangaDex")

    def _start_renew_login(self):
        """Start auto-renew login process in another thread"""
        # "Circular imports" problem
        from .user import User

        r = self.get(f'{base_url}/user/me')
        self.user = User(data=r.json()['data'])

        t = threading.Thread(target=self._renew_login, daemon=True)
        t.start()

    def logout(self, purge=False):
        """Logout from MangaDex"""
        if not self.check_login():
            raise NotLoggedIn("User are not logged in")

        if not purge and self._is_token_cached():
            # To prevent error "Missing session" when renewing session token
            return

        log.info("Logging out from MangaDex")

        self.api_auth.logout()
        self._reset_token()
        self._notify_login_fut()
        self._login_fut = Future()

        if purge and self._config_enabled:
            self._login_cache.purge()

        log.info("Logged out from MangaDex")

    def _report(self, data):
        log.debug('Reporting %s to MangaDex network' % data)
        r = self.post('https://api.mangadex.network/report', json=data)

        if r.status_code != 200:
            log.debug('Failed to report %s to MangaDex network' % data)
        else:
            log.debug('Successfully send report %s to MangaDex network' % data)

    def report(self, data):
        """Report to MangaDex network"""
        job = lambda: self._report(data)
        self._worker_report.submit(job, blocking=False)

class NetworkManager:
    """A requests and MangaDex session manager"""

    available_auth_cls = {
        "oauth2": OAuth2,
        "legacy": LegacyAuth
    }
    default_auth_method = "legacy"
    def __init__(self, proxy=None, trust_env=False) -> None:
        self._proxy = proxy
        self._trust_env = trust_env

        self._mangadex = None
        self._requests = None

        self._doh = None

    @property
    def proxy(self):
        """Return HTTP/SOCKS proxy, return ``None`` if not configured"""
        return self._proxy

    @proxy.setter
    def proxy(self, proxy):
        self.set_proxy(proxy)

    @property
    def trust_env(self):
        """Return ``True`` if http/socks proxy are grabbed from env"""
        return self._trust_env

    @trust_env.setter
    def trust_env(self, yes):
        self._trust_env = yes
        if self._mangadex:
            self._mangadex.trust_env = yes
        if self._requests:
            self._requests.trust_env = yes

    def is_proxied(self):
        """Return ``True`` if requests and MangaDex session from :class:`NetworkObject`
        are configured using proxy.
        """
        return self.proxy is not None

    def set_proxy(self, proxy):
        """Setup HTTP/SOCKS proxy for requests and MangaDex session"""
        if not proxy:
            self.clear_proxy()
        self._proxy = proxy
        if self._mangadex:
            self._update_mangadex_proxy(proxy)
        if self._requests:
            self._update_requests_proxy(proxy)

    def clear_proxy(self):
        """Remove all proxy from requests and MangaDex session and disable environments proxy"""
        self._proxy = None
        self._trust_env = False
        if self._mangadex:
            self._mangadex.proxies.clear()
            self._mangadex.trust_env = False
        if self._requests:
            self._requests.proxies.clear()
            self._requests.trust_env = False

    def _update_mangadex_proxy(self, proxy):
        if self._mangadex:
            pr = {
                'http': proxy,
                'https': proxy
            }
            self._mangadex.proxies.update(pr)
            self._mangadex.trust_env = self._trust_env

    def _create_mangadex(self):
        if self._mangadex is None:
            self._mangadex = requestsMangaDexSession(self._trust_env)
            self._update_mangadex_proxy(self.proxy)

    @property
    def mangadex(self):
        """Return proxied requests for MangaDex (if configured)
        
        This session only for MangaDex, sending http requests to other sites will break the session.
        """
        self._create_mangadex()
        return self._mangadex

    def _update_requests_proxy(self, proxy):
        if self._requests:
            pr = {
                'http': proxy,
                'https': proxy
            }
            self._requests.proxies.update(pr)
            self._requests.trust_env = self._trust_env
    
    def _create_requests(self):
        if self._requests is None:
            self._requests = ModifiedSession()
            self._update_requests_proxy(self.proxy)
    
    @property
    def requests(self):
        """Return proxied requests (if configured)"""
        self._create_requests()
        return self._requests

    def set_delay(self, delay=None):
        """Add delay for each requests for MangaDex session"""
        self.mangadex.delay = delay

    def set_doh(self, provider):
        """Set DoH (DNS-over-HTTPS) for MangaDex and requests session
        
        See https://requests-doh.mansuf.link/en/stable/doh_providers.html for all available DoH providers
        """
        try:
            if self._doh is not None:
                set_dns_provider(provider)
                return

            doh = DNSOverHTTPSAdapter(provider)
        except ValueError as e:
            raise MangaDexException(e)

        self._doh = doh

        self.mangadex.mount('https://', doh)
        self.mangadex.mount('http://', doh)

        self.requests.mount('https://', doh)
        self.requests.mount('http://', doh)

    def set_auth(self, auth_method):
        """Set Authentication method for MangaDex API (default to :class:`LegacyAuth`)"""
        self.mangadex.set_auth(self.available_auth_cls[auth_method])

    def set_timeout(self, time):
        """Set timeout for each requests for MangaDex and requests session"""
        self.mangadex.set_timeout(time)
        self.requests.set_timeout(time)

    def close(self):
        """Close requests and MangaDex session"""
        self._mangadex.close()
        self._mangadex = None

        self._requests.close()
        self._requests = None

Net = NetworkManager()