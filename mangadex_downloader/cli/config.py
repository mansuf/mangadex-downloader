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
import sys

from .utils import get_key_value
from ..config import (
    config, 
    _conf, 
    config_enabled,
    set_config_from_cli_opts,
    reset_config,
    get_all_configs
)
from ..config.utils import ConfigTypeError

log = logging.getLogger(__name__)

def build_config_from_url_arg(parser, urls):
    if not urls.startswith('conf'):
        return

    if not config_enabled:
        parser.error(
            "Config is not enabled, " \
            "you must set MANGADEXDL_CONFIG_ENABLED=1 in your env"
        )

    for url in urls.splitlines():

        val = url.strip()
        # Just ignore it if empty lines
        if not val:
            continue
        # Invalid config
        elif not val.startswith('conf'):
            continue

        # Split from "conf:config_key=config_value"
        # to ["conf", "config_key=config_value"] 
        _, conf = get_key_value(val, sep=':')

        # Split string from "config_key=config_value"
        # to ["config_key", "config_value"]
        conf_key, conf_value = get_key_value(conf)

        if not conf_key:
            for name, value in get_all_configs():
                print(f"Config '{name}' is set to '{value}'")
            continue

        # Reset config (if detected)
        if conf_key.startswith('reset'):
            try:
                reset_config(conf_value)
            except AttributeError:
                parser.error(f"Config '{conf_key}' is not exist")

            if conf_value:
                print(f"Successfully reset config '{conf_value}'")
            else:
                # Reset all configs
                print(f"Successfully reset all configs")

            continue

        try:
            previous_value = getattr(config, conf_key)
        except AttributeError:
            parser.error(f"Config '{conf_key}' is not exist")

        if not conf_value:
            print(f"Config '{conf_key}' is set to '{previous_value}'")
            continue

        try:
            setattr(config, conf_key, conf_value)
        except ConfigTypeError as e:
            parser.error(str(e))

        conf_value = getattr(config, conf_key)

        print(f"Successfully changed config {conf_key} from '{previous_value}' to '{conf_value}'")

    # Changing config require users to input config in URL argument
    # If the app is not exited, the app will continue and throwing error
    # because of invalid URL given
    sys.exit(0)
        
def build_config(parser, args):
    build_config_from_url_arg(parser, args.URL)

    if not config_enabled and args.login_cache:
        parser.error(
            "You must set MANGADEXDL_CONFIG_ENABLED=1 in your env " \
            "in order to enable login caching"
        )

    # Automatically set config.login_cache to True 
    # if args.login_cache is True and config.login_cache is False
    if not config.login_cache and args.login_cache:
        config.login_cache = args.login_cache

    # Print all config to debug
    if config_enabled:
        log.debug(f"Loaded config from path '{_conf.path}' = {_conf._data}")

    set_config_from_cli_opts(args)

    log.debug(f"Loaded config from cli args = {_conf._data}")
        
        

        
