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

import webbrowser
import logging
import time
import shutil
import io
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from requests.auth import AuthBase
from multiprocessing import Process, Manager

from .base import MangaDexAuthBase
from ..errors import MangaDexException, LoginFailed

log = logging.getLogger(__name__)

try:
    from authlib.oauth2.auth import ClientAuth
    from authlib.oauth2 import OAuth2Client
except ImportError:
    oauth_ready = False
else:
    oauth_ready = True


if oauth_ready:
    # For `authlib.oauth2.OAuth2Client.client_auth_class`
    class OAuth2ClientAuth(AuthBase, ClientAuth):
        """Attaches OAuth Client Authentication to the given Request object.
        """
        def __call__(self, req):
            req.url, req.headers, req.body = self.prepare(
                req.method, req.url, req.headers, req.body
            )
            return req

# For callback handler (`redirect_uri`)
class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    invalid_path_response = b"""
    <html>
        <head>
            <title>Error happened</title>
        </head>
        
        <body>
            <p>Invalid request, please try again</p>
        </body>
    </html>
    """

    invalid_state_response = b"""
    <html>
        <head>
            <title>Error happened</title>
        </head>
        
        <body>
            <p>Invalid state, please try again</p>
        </body>
    </html>
    """

    good_response = b"""
    <html>
        <head>
            <title>Success</title>
        </head>
        
        <body>
            <p>You're logged in now, check your 'mangadex-downloader' app</p>
        </body>
    </html>
    """

    def send_invalid_request(self):
        self.send_response(400)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(self.invalid_path_response))
        self.end_headers()

        fp = io.BytesIO(self.invalid_path_response)
        shutil.copyfileobj(fp, self.wfile)

    def send_invalid_state(self):
        self.send_response(400)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(self.invalid_state_response))
        self.end_headers()

        fp = io.BytesIO(self.invalid_state_response)
        shutil.copyfileobj(fp, self.wfile)

    def send_success(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(self.good_response))
        self.end_headers()

        fp = io.BytesIO(self.good_response)
        shutil.copyfileobj(fp, self.wfile)

    def send_login_error(self, err_type, message):
        error_response = """
        <html>
            <head>
                <title>Error happened</title>
            </head>
            
            <body>
                <p>{msg}</p>
            </body>
        </html>
        """.format(
            msg=f"Login Failed (err_type: {err_type}). Description: '{message}'" \
                ". Please check your 'mangadex-downloader' app"
        )

        self.send_response(403)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(error_response))
        self.end_headers()

        fp = io.BytesIO(error_response.encode())
        shutil.copyfileobj(fp, self.wfile)

    def do_GET(self):
        orig_state = self.namespace.state
        host = self.request.getsockname()
        url = urlparse(f"http://{host[0]}:{host[1]}" + self.path)

        if url.path != "/":
            self.send_invalid_request()
            return

        query = parse_qs(url.query)
        state = query.get("state")

        if not state:
            self.send_invalid_request()
            return
        
        state = state[0]

        if state != orig_state:
            self.send_invalid_state()
            return

        new_args = {}
        for key, value in query.items():
            new_args[key] = value[0]

        error = new_args.get("error")
        if error:
            self.send_login_error(error, new_args["error_description"])
            self.namespace.result = {
                "error": error,
                "description": new_args["error_description"]
            }
            self.event.set()
            return

        self.send_success()

        self.namespace.result = new_args
        self.event.set()

class OAuth2CallbackHandleBuilder:
    def __init__(self, namespace, event) -> None:
        self.namespace = namespace
        self.event = event

    def __call__(self, *args, **kwargs):
        OAuth2CallbackHandler.namespace = self.namespace
        OAuth2CallbackHandler.event = self.event
        return OAuth2CallbackHandler(*args, **kwargs)

class OAuth2(MangaDexAuthBase):
    callback_host = "localhost"
    callback_port = 3000

    def __init__(self, *args, **kwargs):

        if not oauth_ready:
            raise MangaDexException("Library 'authlib' is not installed")

        super().__init__(*args, **kwargs)

        self.openid_config_url = f"{self.session.auth_url}/realms/mangadex/.well-known/openid-configuration"
        self.openid_config = self.session.get(self.openid_config_url).json()

        self.authorization_endpoint = self.openid_config["authorization_endpoint"]
        self.token_endpoint = self.openid_config["token_endpoint"]
        self.revocation_endpoint = self.openid_config["revocation_endpoint"]

        self.client = OAuth2Client(
            session=self.session,
            # THE STABLE API ARE NOT ALLOWED TO MAKE CUSTOM ID YET, PLEASE CHANGE THIS ONCE IT'S ALLOWED
            client_id="thirdparty-oauth-client",
            scope="openid groups profile roles",
            redirect_uri=f"http://{self.callback_host}:{self.callback_port}",
        )
        self.client.client_auth_class = OAuth2ClientAuth

        # OAuth2 callback handler
        self.callback_handler = None

        # Authentication result from OAuth2
        self.session_state = None
        self.authorization_code = None
        self.token = {}

    def run_callback_handler(self, n, e):
        self.callback_handler = HTTPServer(
            (self.callback_host, self.callback_port), 
            OAuth2CallbackHandleBuilder(n, e)
        )
        self.callback_handler.serve_forever()

    def _make_ready_token(self, token):
        return {
            "session": token["access_token"],
            "refresh": token["refresh_token"]
        }

    def login(self, username, email, password):
        log.debug("Creating Manager for multiprocessing")
        with Manager() as manager:
            namespace = manager.Namespace()
            event = manager.Event()

            url, state = self.client.create_authorization_url(self.authorization_endpoint)
            namespace.state = state

            log.debug("Starting OAuth2 callback handler")
            proc = Process(target=self.run_callback_handler, args=(namespace, event), daemon=True)
            proc.start()

            open_browser_success = webbrowser.open(url, new=2, autoraise=True)
            if not open_browser_success:
                log.info(f"Failed to open browser. Please open this url to authenticate => {url}")

            log.info("Waiting OAuth2 callback handler response")
            time.sleep(1)
            event.wait()

            result_auth = namespace.result

            log.debug("Terminating OAuth2 callback handler")
            proc.terminate()

            # Check for errors
            error = result_auth.get("error")
            err_description = result_auth.get("description")
            if error:
                raise LoginFailed(f"Login to MangaDex failed, reason: {err_description}")

            self.session_state = result_auth["session_state"]
            self.authorization_code = result_auth["code"]

            self.token = self.client.fetch_token(
                url=self.token_endpoint,
                grant_type="authorization_code",
                code=self.authorization_code
            )

            return self._make_ready_token(self.token)

    def refresh_token(self):
        self.token = self.client.refresh_token(
            url=self.token_endpoint,
            refresh_token=self.token["refresh_token"]
        )

        return self._make_ready_token(self.token)

    def check_login(self):
        # TODO: Use OAuth2 introspect token instead of /auth/check
        # We don't know that '/auth/check` will be deprecated soon

        url = '{0}/auth/check'.format(self.session.base_url)
        r = self.session.get(url)

        return r.json()['isAuthenticated']

    def update_token(self, session=None, refresh=None):
        if session:
            self.token["access_token"] = session

        if refresh:
            self.token["refresh_token"] = refresh

    def _revoke_token(self, type_token):
        response = self.client.revoke_token(
            url=self.revocation_endpoint,
            token=self.token[type_token],
            token_type_hint=type_token
        )

        if not response.ok:
            log.error(f"Failed to revoke '{type_token}', reason: {response.content}")

    def logout(self):
        # XXX: Now, i'm confused with logout in OAuth2
        # Should we just revoke the "access_token" and "refresh_token" only ?
        # or we should revoke the tokens + end the session ?
        # ======================================================================
        # Method "revoke the tokens only" will revoke the tokens.
        # but not logout from client "..." immediately and it will NOT be prompted to login
        # when trying to authenticate
        # ======================================================================
        # Method "revoke the tokens + end the session" will revoke the tokens
        # and logout from client "..." completely. The user will be prompted to login
        # when trying to authenticate
        # ======================================================================

        # For now let's do the "revoke the tokens only" method.
        # I will ask MangaDex devs about this
        self._revoke_token("access_token")
        self._revoke_token("refresh_token")

        self.session_state = None
        self.authorization_code = None
        self.token = None