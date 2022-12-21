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

import logging
import re
import sys

from .utils import dynamic_bars, get_key_value
from ..config import config, login_cache
from ..utils import getpass_handle, input_handle
from ..errors import HTTPException, LoginFailed
from ..network import Net

# I know this sound stupid
# But i only know this to check if it's email or username
email_regex = r'.{1,}@.{1,}\..{1,}'

log = logging.getLogger(__name__)

def print_auth_cache_help():
    text = "Available commands"
    print(text)
    print(dynamic_bars(text))
    print()

    print("purge = 'Purge cached authentication tokens'")
    print("show = 'Show expiration time cached authentication tokens'")
    print("show_unsafe = 'Show cached authentication tokens (NOT RECOMMENDED)'")

def print_auth_cache_expire():
    """Print expiration time auth tokens"""
    session_token = login_cache.get_session_token()
    if session_token:
        exp_session_token = login_cache.get_expiration_time(session_token).isoformat()
    else:
        exp_session_token = "Token is not cached or expired"

    print(f"Session token expiration time: {exp_session_token}")

    refresh_token = login_cache.get_refresh_token()
    if refresh_token:
        exp_refresh_token = login_cache.get_expiration_time(refresh_token).isoformat()
    else:
        exp_refresh_token = "Token is not cached or expired"

    print(f"Refresh token expiration time: {exp_refresh_token}")

def print_auth_cache_unsafe():
    """Print auth cache tokens"""
    print(
        "WARNING: You should not use 'login_cache:show_unsafe', " \
        "because it exposing your auth tokens to terminal screen. " \
        "Use this if you know what are you doing."
    )

    result = input("[Yes / Y, No / N]\n=> ")
    result = result.lower()
    if not (result.startswith('yes') or result.startswith('y')) or not result:
        return

    # Show the auth tokens anyway
    header = f"MangaDex cached authentication tokens, stored in '{login_cache.path}'"
    print(header)
    print(dynamic_bars(header))
    print()

    session_token = login_cache.get_session_token()
    if session_token:
        exp_session_token = login_cache.get_expiration_time(session_token).isoformat()
    else:
        exp_session_token = "Token is not cached or expired"

    print(f"Session token: {session_token}")
    print(f"Session token expiration time: {exp_session_token}")

    print()

    refresh_token = login_cache.get_refresh_token()
    if refresh_token:
        exp_refresh_token = login_cache.get_expiration_time(refresh_token).isoformat()
    else:
        exp_refresh_token = "Token is not cached or expired"

    print(f"Refresh token: {refresh_token}")
    print(f"Refresh token expiration time: {exp_refresh_token}")

def purge_cache(args):
    string = args.URL

    if not string.startswith('login_cache'):
        return

    # Get value from "login_cache:{VALUE}"
    _, value = get_key_value(string, sep=':')

    # Reset authentication cache
    if value.startswith('purge'):
        Net.mangadex.login_from_cache()
        Net.mangadex.logout(purge=True)
        print("Succesfully invalidate and purge authentication cache tokens")
    elif value.startswith('show_unsafe'):
        print_auth_cache_unsafe()
    elif value.startswith('help'):
        print_auth_cache_help()
    elif value.startswith('show'):
        print_auth_cache_expire()
    else:
        print_auth_cache_expire()

    sys.exit(0)

def logout_with_err_handler(args):
    if args.login:
        # Make sure that we are really LOGGED IN
        # To prevent error while logging out
        try:
            logged_in = Net.mangadex.check_login()
        except Exception:
            logged_in = False
        
        if not logged_in:
            return

        logout_success = False
        for _ in range(5):
            attempt = _ + 1
            try:
                Net.mangadex.logout()
            except HTTPException as e:
                log.info(
                    'Logout failed because of MangaDex server error, status code: %s. ' \
                    'Trying again... (attempt: %s)',
                    e.response.status_code,
                    attempt
                )
            else:
                logout_success = True
                break
        
        if not logout_success:
            log.error("5 attempts logout failed, ignoring...")

def login_with_err_handler(args):
    purge_cache(args)

    if not args.login and config.login_cache:
        Net.mangadex.login_from_cache()

        if Net.mangadex.check_login():
            return

    if args.login:
        email = None
        username = None
        password = None

        if args.login_method != "oauth2":
            if not args.login_username:
                username = input_handle("MangaDex username / email => ")
            else:
                username = args.login_username
            if not args.login_password:
                password = getpass_handle("MangaDex password => ")
            else:
                password = args.login_password

            # Ability to login with email
            is_email = re.match(email_regex, username)
            if is_email is not None:
                email = is_email.group()
                username = None

        # Logging in
        login_success = False
        for _ in range(5):
            attempt = _ + 1
            try:
                Net.mangadex.login(password, username, email)
            except LoginFailed as e:
                log.error(e)
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
            else:
                login_success = True
                break

        if not login_success:
            log.error("5 attempts login failed, exiting...")
            sys.exit(1)