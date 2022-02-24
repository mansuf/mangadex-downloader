import logging
import sys

from getpass import getpass
from ..main import login, logout
from ..errors import HTTPException, LoginFailed
from ..network import Net

log = logging.getLogger(__name__)

def logout_with_err_handler(args):
    if args.login:
        # Make sure that we are really LOGGED IN
        # To prevent error while logging out
        try:
            logged_in = Net.requests.check_login()
        except Exception:
            logged_in = False
        
        if not logged_in:
            return

        logout_success = False
        for _ in range(5):
            attempt = _ + 1
            try:
                logout()
            except HTTPException as e:
                log.info(
                    'Logout failed because of MangaDex server error, status code: %s. ' \
                    'Trying again... (attempt: %s)',
                    e.response.status_code,
                    attempt
                )
            except RuntimeError as e:
                log.error(str(e))
                return
            except Exception as e:
                log.error("Unhandled exception, %s: %s" % (e.__class__.__name__, str(e)))
                return
            else:
                logout_success = True
                break
        
        if not logout_success:
            log.error("5 attempts logout failed, ignoring...")

def login_with_err_handler(args):
    if args.login:
        if not args.login_username:
            try:
                username = input("MangaDex username => ")
            except EOFError:
                sys.exit(0)
        else:
            username = args.login_username
        if not args.login_password:
            try:
                password = getpass("MangaDex password => ")
            except EOFError:
                sys.exit(0)
        else:
            password = args.login_password

        # Logging in
        login_success = False
        for _ in range(5):
            attempt = _ + 1
            try:
                login(password, username)
            except LoginFailed as e:
                sys.exit(1)
            except ValueError as e:
                log.error(e)
                sys.exit(1)
            except HTTPException as e:
                log.info(
                    'Login failed because of MangaDex server error, status code: %s. ' \
                    'Trying again... (attempt: %s)',
                    e.response.status_code,
                    attempt
                )
            except RuntimeError as e:
                log.error(str(e))
                sys.exit(1)
            except Exception as e:
                log.error("Unhandled exception, %s: %s" % (e.__class__.__name__, str(e)))
                sys.exit(1)
            else:
                login_success = True
                break

        if not login_success:
            log.error("5 attempts login failed, exiting...")
            sys.exit(1)