import webbrowser
import logging
from requests.auth import AuthBase
from multiprocessing import Process, Manager

from .base import MangaDexAuthBase
from ..errors import MangaDexException

log = logging.getLogger(__name__)

try:
    from authlib.oauth2.auth import ClientAuth
    from authlib.oauth2 import OAuth2Client
    from flask import Flask, request
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
    class OAuth2CallbackHandler:
        def __init__(self, namespace, event):
            self.namespace = namespace
            self.event = event
            self.server = Flask("mangadex-downloader-oauth-callback", static_folder=None)

            self.server.add_url_rule('/', view_func=self.handle_auth, methods=["GET"])

        def run(self):
            self.server.run("localhost", "3000", debug=False, load_dotenv=False)

        def handle_auth(self):
            state = self.namespace.state

            if state != request.args.get("state"):
                return "Invalid state, please try again"

            self.namespace.result = request.args.to_dict()
            self.event.set()
            return "You're logged in now, check your 'mangadex-downloader' app"

class OAuth2(MangaDexAuthBase):
    callback_host = "localhost"
    callback_port = "3000"

    def __init__(self, *args, **kwargs):

        if not oauth_ready:
            raise MangaDexException("Library 'Flask' and 'authlib' is not installed")

        super().__init__(*args, **kwargs)

        self.openid_config_url = f"https://{self.session.auth_url}/realms/mangadex/.well-known/openid-configuration"
        self.openid_config = self.session.get(self.openid_config_url).json()

        self.authorization_endpoint = self.openid_config["authorization_endpoint"]
        self.token_endpoint = self.openid_config["token_endpoint"]
        self.revocation_endpoint = self.openid_config["revocation_endpoint"]

        self.client = OAuth2Client(
            session=self.session, 
            client_id="THE STABLE API ARE NOT ALLOWED TO MAKE CUSTOM ID YET, PLEASE CHANGE THIS ONCE IT'S ALLOWED",
            scope="openid profile roles groups",
            redirect_uri=f"http://{self.callback_host}:{self.callback_port}",
        )

        # OAuth2 callback handler
        self.callback_handler = None

        # Authentication result from OAuth2
        self.session_state = None
        self.authorization_code = None
        self.token = None

    def run_callback_handler(self, n, e):
        self.callback_handler = OAuth2CallbackHandler(n, e)        
        self.callback_handler.event("localhost", 3000, debug=False, load_dotenv=False)

    def _make_ready_token(self, token):
        return {
            "session": token["access_token"],
            "refresh": token["refresh_token"]
        }

    def login(self):
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
            event.wait()

            result_auth = namespace.result

            log.debug("Terminating OAuth2 callback handler")
            proc.terminate()

            self.session_state = result_auth["session_state"]
            self.authorization_code = result_auth["code"]

            self.token = self.client.fetch_token(
                url=self.token_endpoint,
                grant_type="authorization_code",
                code=self.authorization_code
            )

            return self._make_ready_token(self.token)

    def refresh_token(self):
        self.token = self.client.refresh_token(self.token["refresh_token"])

        return self._make_ready_token(self.token)

    def check_login(self):
        # TODO: Use OAuth2 introspect token instead of /auth/check
        # We don't know that '/auth/check` will be deprecated soon

        url = '{0}/auth/check'.format(self.session.base_url)
        r = self.session.get(url)

        return r.json()['isAuthenticated']

    def _revoke_token(self, type_token):
        response = self.client.revoke_token(
            url=self.revocation_endpoint,
            token=self.token[type_token],
            token_type_hint=type_token
        )

        if not response.ok:
            log.error(f"Failed to revoke 'access_token', reason: {response.content}")

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