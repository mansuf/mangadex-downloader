import logging
import sys
from ..config import (
    set_config_from_cli_opts,
    config_enabled,
    config, # High-level access config
    _conf, # Low-level access config for debugging
    ConfigTypeError,
    reset_config
)

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

        # Initial value splitted into "key_conf=value_conf"
        value = url.strip().split(':')

        # Split key and value config into ["key", "value_piece1", "value_piece2"]
        conf = "".join(value[1:]).split('=')

        conf_key = conf[0]

        if not conf_key:
            parser.error("There is no config key")

        # Merge value pieces
        conf_value = "".join(conf[1:])

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

        if not conf_value:
            parser.error(f"{conf_key}: There is no config value")

        try:
            previous_value = getattr(config, conf_key)
        except AttributeError:
            parser.error(f"Config '{conf_key}' is not exist")

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

    # Print all config to debug
    log.debug(f"Loaded config from path '{_conf.path}' = {_conf._data}")

    set_config_from_cli_opts(args)

    log.debug(f"Loaded config from cli args = {_conf._data}")
        
        

        
