# Based on https://github.com/mansuf/zippyshare-downloader/blob/main/zippyshare_downloader/network.py

import requests
import urllib.parse
import queue
import time
import logging
import sys
import threading
from . import __version__
from .errors import (
    AlreadyLoggedIn,
    HTTPException,
    LoginFailed,
    MangaDexException,
    NotLoggedIn,
    UnhandledHTTPError
)
from requests_doh import DNSOverHTTPSAdapter
from concurrent.futures import Future, TimeoutError

EXP_LOGIN_SESSION = (15 * 60) - 30 # 14 min 30 seconds timeout, 30 seconds delay for re-login

log = logging.getLogger(__name__)

__all__ = (
    'Net', 'NetworkObject',
    'set_proxy', 'clear_proxy',
    'base_url', 'uploads_url'
)

origin_url = 'https://mangadex.org'
base_url = 'https://api.mangadex.org'
uploads_url = 'https://uploads.mangadex.org'

# A utility to get shortened url from full URL
# (scheme, netloc, and path only)
def _get_netloc(url):
    result = urllib.parse.urlparse(url)
    return result.scheme + '://' + result.netloc + result.path

# Modified requests session with ability to set timeout for each requests
class ModifiedSession(requests.Session):
    def __init__(self):
        super().__init__()

        self._timeout = None

    def set_timeout(self, time):
        self._timeout = time

    def send(self, r, **kwargs):
        kwargs.update({'timeout': self._timeout})
        return super().send(r, **kwargs)

class requestsMangaDexSession(ModifiedSession):
    def __init__(self, trust_env=True) -> None:
        # "Circular imports" problem
        from .config import login_cache

        super().__init__()
        self.trust_env = trust_env
        self.user = None
        self.delay = None
        user_agent = 'mangadex-downloader (https://github.com/mansuf/mangadex-downloader {0}) '.format(__version__)
        user_agent += 'Python/{0[0]}.{0[1]} '.format(sys.version_info)
        user_agent += 'requests/{0}'.format(
            requests.__version__
        )
        self.headers = {
            "User-Agent": user_agent
        }
        self._session_token = None
        self._refresh_token = None

        self._login_cache = login_cache

        # For login
        self._login_lock = Future()

        self._queue_report = queue.Queue()

        # Run the queue worker report
        t = threading.Thread(target=self._worker_queue_report)
        t.start()

        # Run mainthread shutdown handler for queue worker
        t = threading.Thread(target=self._worker_queue_report_handler)
        t.start()

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
            self.refresh_login()

            # Start "auto-renew session token" process
            self._start_timer_thread()
        else:
            # Session and refresh token are still valid in cache
            # Login with this
            self._update_token(
                {"token": {
                    "refresh": refresh_token,
                    "session": session_token
                }}
            )
            self._start_timer_thread()
        
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
        for _ in range(5):
            resp = self._request(attempt, *args, **kwargs)
            if resp is not None:
                return resp
            
            if self.delay:
                delay = self.delay
            else:
                delay = attempt * 0.5
            
            time.sleep(delay)
            attempt += 1
            continue

        if resp is not None and resp.status_code >= 500:
            # 5 attempts request failed caused by server error
            # raise error
            raise HTTPException('Server sending %s code' % resp.status_code, resp=resp)

        raise UnhandledHTTPError("Unhandled HTTP error")

    def _worker_queue_report_handler(self):
        """If mainthread is shutted down all queue worker must shut down too"""
        main_thread = threading.main_thread()
        main_thread.join()
        self.report(None)

    def _worker_queue_report(self):
        """Queue worker for reporting MangaDex network
        
        This function will run in another thread.
        """
        while True:
            data = self._queue_report.get()
            if data is None:
                return
            else:
                log.debug('Reporting %s to MangaDex network' % data)
                r = self.post('https://api.mangadex.network/report', json=data)

                if r.status_code != 200:
                    log.debug('Failed to report %s to MangaDex network' % data)
                else:
                    log.debug('Successfully send report %s to MangaDex network' % data)

    def _shutdown_report_queue_worker(self):
        """Shutdown queue worker for reporting MangaDex network
        
        client should not call this.
        """
        self._queue_report.put(None)

    def _update_token(self, result):
        session_token = result['token']['session']
        refresh_token = result['token']['refresh']

        self._refresh_token = refresh_token
        self._session_token = session_token
        self.headers['Authorization'] = 'Bearer %s' % session_token

        self._login_cache.set_refresh_token(refresh_token)
        self._login_cache.set_session_token(session_token)

    def _is_token_cached(self):
        if self._login_cache.get_session_token():
            return True

        if self._login_cache.get_refresh_token():
            return True
        
        return False

    def _reset_token(self):
        self._refresh_token = None
        self._session_token = None
        self.headers.pop('Authorization')

    def _notify_login_lock(self):
        self._login_lock.set_result(True)
    
    def _wait_login_lock(self):
        """Wait until time is running out and then re-login with refresh token or logout() is called"""
        while True:
            exp_time = (
                self._login_cache.get_expiration_time(self._session_token) -
                self._login_cache._get_datetime_now()
            ).total_seconds()
            delay = exp_time - self._login_cache.delay_login_time
            try:
                logout = self._login_lock.result(delay)
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
            raise RuntimeError("User are not logged in")
        
        url = '{0}/auth/refresh'.format(base_url)
        r = self.post(url, json={"token": self._refresh_token})
        result = r.json()

        if r.status_code != 200:
            raise LoginFailed("Refresh token failed, reason: %s" % result["errors"][0]["detail"])

        self._update_token(result)

    def check_login(self):
        """Check if user are still logged in"""
        if self._refresh_token is None and self._session_token is None:
            return False

        url = '{0}/auth/check'.format(base_url)
        r = self.get(url)

        return r.json()['isAuthenticated']

    def login(self, password, username=None, email=None):
        """Login to MangaDex"""
        # Raise error if already logged in
        if self.check_login():
            raise AlreadyLoggedIn("User already logged in")

        # Type checking
        if not isinstance(password, str):
            raise ValueError("password must be str, not %s" % type(password))
        if username and not isinstance(username, str):
            raise ValueError("username must be str, not %s" % type(username))
        if email and not isinstance(email, str):
            raise ValueError("email must be str, not %s" % type(email))

        if not username and not email:
            raise LoginFailed("at least provide \"username\" or \"email\" to login")

        # Raise error if password length are less than 8 characters
        if len(password) < 8:
            raise ValueError("password length must be more than 8 characters")

        log.info('Logging in to MangaDex')

        url = '{0}/auth/login'.format(base_url)
        data = {"password": password}
        
        if username:
            data['username'] = username
        if email:
            data['email'] = email
        
        # Begin to log in
        r = self.post(url, json=data)
        if r.status_code == 401:
            result = r.json()
            err = result["errors"][0]["detail"]
            log.error("Login to MangaDex failed, reason: %s" % err)
            raise LoginFailed(err)
        
        result = r.json()
        self._update_token(result)

        self._start_timer_thread()

        log.info("Logged in to MangaDex")

    def _start_timer_thread(self):
        # "Circular imports" problem
        from .user import User

        r = self.get(f'{base_url}/user/me')
        self.user = User(data=r.json()['data'])

        t = threading.Thread(target=self._wait_login_lock, daemon=True)
        t.start()

    def logout(self):
        """Logout from MangaDex"""
        if not self.check_login():
            raise NotLoggedIn("User are not logged in")

        if self._is_token_cached():
            # To prevent error "Missing session" when renewing session token
            return

        log.info("Logging out from MangaDex")

        self.post("{0}/auth/logout".format(base_url))
        self._reset_token()
        self._notify_login_lock()
        self._login_lock = Future()

        log.info("Logged out from MangaDex")
    
    def report(self, data):
        """Report to MangaDex network"""
        self._queue_report.put(data)

class NetworkObject:
    def __init__(self, proxy=None, trust_env=False) -> None:
        self._proxy = proxy
        self._trust_env = trust_env

        # This will be disable proxy from environtments
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
        """Return ``True`` if requests from :class:`NetworkObject`
        are configured using proxy.
        """
        return self.proxy is not None

    def set_proxy(self, proxy):
        """Setup HTTP/SOCKS proxy for requests"""
        if not proxy:
            self.clear_proxy()
        self._proxy = proxy
        if self._mangadex:
            self._update_mangadex_proxy(proxy)
        if self._requests:
            self._update_requests_proxy(proxy)

    def clear_proxy(self):
        """Remove all proxy from requests and disable environments proxy"""
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
        """Set DoH (DNS-over-HTTPS) for MangaDex and requests session"""
        try:
            doh = DNSOverHTTPSAdapter(provider)
        except ValueError as e:
            raise MangaDexException(e)

        self.mangadex.mount('https://', doh)
        self.mangadex.mount('http://', doh)

        self.requests.mount('https://', doh)
        self.requests.mount('http://', doh)
    
    def set_timeout(self, time):
        self.mangadex.set_timeout(time)
        self.requests.set_timeout(time)

    def close(self):
        self._mangadex.close()
        self._mangadex = None

        self._requests.close()
        self._requests = None

Net = NetworkObject()

def set_proxy(proxy):
    """Setup HTTP/SOCKS proxy for requests
    
    This is shortcut for :meth:`NetworkObject.set_proxy`.
    This will apply to ``Net`` object globally.
    """
    Net.set_proxy(proxy)

def clear_proxy():
    """Remove all proxy from requests
    
    This is shortcut for :meth:`NetworkObject.clear_proxy`. 
    This will apply to ``Net`` object globally.
    """
    Net.clear_proxy()