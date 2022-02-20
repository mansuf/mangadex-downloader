# Based on https://github.com/mansuf/zippyshare-downloader/blob/main/zippyshare_downloader/network.py

import requests
import aiohttp
import asyncio
import queue
import time
import logging
import sys
import threading
from . import __version__
from .errors import AlreadyLoggedIn, HTTPException, LoginFailed, NotLoggedIn
from concurrent.futures import Future, TimeoutError

EXP_LOGIN_SESSION = (15 * 60) - 30 # 14 min 30 seconds timeout, 30 seconds delay for re-login

log = logging.getLogger(__name__)

__all__ = (
    'Net', 'NetworkObject',
    'set_proxy', 'clear_proxy',
    'base_url', 'uploads_url'
)

base_url = 'https://api.mangadex.org'
uploads_url = 'https://uploads.mangadex.org'

# Modified requests session class with __del__ handler
# so the session will be closed properly
class requestsMangaDexSession(requests.Session):
    def __init__(self, trust_env=True) -> None:
        super().__init__()
        self.trust_env = trust_env
        user_agent = 'mangadex-downloader (https://github.com/mansuf/mangadex-downloader {0}) '.format(__version__)
        user_agent += 'Python/{0[0]}.{0[1]} '.format(sys.version_info)
        user_agent += 'aiohttp/{0} requests/{1}'.format(
            aiohttp.__version__,
            requests.__version__
        )
        self.headers = {
            "User-Agent": user_agent
        }
        self._session_token = None
        self._refresh_token = None

        # For login
        self._login_lock = Future()

        self._queue_report = queue.Queue()

        # Run the queue worker report
        t = threading.Thread(target=self._worker_queue_report)
        t.start()

        # Run mainthread shutdown handler for queue worker
        t = threading.Thread(target=self._worker_queue_report_handler)
        t.start()

    # Ratelimit handler
    def request(self, *args, **kwargs):
        attempt = 1
        for _ in range(5):
            try:
                resp = super().request(*args, **kwargs)
            except requests.exceptions.ConnectionError as e:
                attempt += 1
                log.error("Failed to connect to \"%s\", reason: %s. Trying... (attempt: %s)" % (
                    e.request.url,
                    str(e),
                    attempt
                ))
                continue

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
                attempt += 1
                continue

            # Server error
            elif resp.status_code >= 500:
                raise HTTPException('Server sending %s code' % resp.status_code, resp=resp)

            return resp
        
        raise RuntimeError("Unhandled HTTP error")

    def _worker_queue_report_handler(self):
        """If mainthread is shutted down all queue worker must shut down too"""
        is_alive = lambda: threading.main_thread().is_alive()
        alive = is_alive()
        while alive:
            time.sleep(0.3)
            alive = is_alive()
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

    def _reset_token(self):
        self._refresh_token = None
        self._session_token = None
        self.headers.pop('Authorization')

    def _notify_login_lock(self):
        self._login_lock.set_result(True)
    
    def _wait_login_lock(self):
        """Wait until time is running out and then re-login with refresh token or logout() is called"""
        while True:
            try:
                logout = self._login_lock.result(EXP_LOGIN_SESSION)
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

        t = threading.Thread(target=self._wait_login_lock, daemon=True)
        t.start()

        log.info("Logged in to MangaDex")

    def logout(self):
        """Logout from MangaDex"""
        if not self.check_login():
            raise NotLoggedIn("User are not logged in")
        
        log.info("Logging out from MangaDex")

        self.post("{0}/auth/logout".format(base_url))
        self._reset_token()
        self._notify_login_lock()
        self._login_lock = Future()

        log.info("Logged out from MangaDex")
    
    def report(self, data):
        """Report to MangaDex network"""
        self._queue_report.put(data)

# Because aiohttp doesn't support proxy from session
# we need to subclass it to proxy each requests without
# add "proxy" parameter to each requests
class aiohttpProxiedSession(aiohttp.ClientSession):
    def __init__(self, proxy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy = proxy

    def set_proxy(self, proxy):
        self.proxy = proxy
    
    def remove_proxy(self):
        self.proxy = None

    async def _request(self, *args, **kwargs):
        kwargs.update(proxy=self.proxy)
        return await super()._request(*args, **kwargs)

class NetworkObject:
    def __init__(self, proxy=None, trust_env=False) -> None:
        self._proxy = proxy
        self._aiohttp = None # type: aiohttpProxiedSession
        self._trust_env = trust_env

        # This will be disable proxy from environtments
        self._requests = None

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
        if self._aiohttp:
            self._aiohttp._trust_env = yes
        if self._requests:
            self._requests.trust_env = yes

    def is_proxied(self):
        """Return ``True`` if requests/aiohttp from :class:`NetworkObject`
        are configured using proxy.
        """
        return self.proxy is not None

    def set_proxy(self, proxy):
        """Setup HTTP/SOCKS proxy for aiohttp/requests"""
        if not proxy:
            self.clear_proxy()
        self._proxy = proxy
        if self._requests:
            self._update_requests_proxy(proxy)
        if self._aiohttp:
            self._update_aiohttp_proxy(proxy)

    def clear_proxy(self):
        """Remove all proxy from aiohttp/request and disable environments proxy"""
        self._proxy = None
        self._trust_env = False
        if self._requests:
            self._requests.proxies.clear()
            self._requests.trust_env = False
        if self._aiohttp:
            self._aiohttp.remove_proxy()
            self._aiohttp._trust_env = False

    def _update_aiohttp_proxy(self, proxy):
        if self._aiohttp:
            self._aiohttp.set_proxy(proxy)
            self._aiohttp._trust_env = self._trust_env

    @property
    def aiohttp(self):
        """Return proxied aiohttp (if configured)"""
        self._create_aiohttp()
        return self._aiohttp

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
            self._requests = requestsMangaDexSession(self._trust_env)
            self._update_requests_proxy(self.proxy)

    @property
    def requests(self):
        """Return proxied requests (if configured)"""
        self._create_requests()
        return self._requests

    def _create_aiohttp(self):
        # Check if current asyncio loop is running
        # if running create aiohttp session
        # if not don't create it
        loop = asyncio.get_event_loop()

        # Raise error if using in another thread
        if self._aiohttp and self._aiohttp._loop != loop:
            raise RuntimeError('created aiohttp session cannot be used in different thread')

        if self._aiohttp is None:
            self._aiohttp = aiohttpProxiedSession(self.proxy)
            self._update_aiohttp_proxy(self.proxy)

    def close(self):
        """Close requests session only"""
        self._requests.close()
        self._requests = None

    async def close_async(self):
        """Close aiohttp & requests session"""
        self.close()
        if not self._aiohttp.closed:
            await self._aiohttp.close()
        self._aiohttp = None

Net = NetworkObject()

def set_proxy(proxy):
    """Setup HTTP/SOCKS proxy for aiohttp/requests
    
    This is shortcut for :meth:`NetworkObject.set_proxy`.
    This will apply to ``Net`` object globally.
    """
    Net.set_proxy(proxy)

def clear_proxy():
    """Remove all proxy from aiohttp/requests
    
    This is shortcut for :meth:`NetworkObject.clear_proxy`. 
    This will apply to ``Net`` object globally.
    """
    Net.clear_proxy()