#!/usr/bin/env python3

import sys
import os
import yaml

_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_CONFIG_FILE_PATH = "{SCRIPT_DIR}/versioning_config.yml"
_CONFIG = {}
_ENVIRONMENT = "dev"
_ENV_DATA = None
_OVERRIDE_PASSWORD = ''
_YES = False


def set_script_directory(directory):
    global _SCRIPT_DIR
    _SCRIPT_DIR = directory


def get_script_directory():
    return _SCRIPT_DIR


def get_filepath():
    return _CONFIG_FILE_PATH.replace("{SCRIPT_DIR}", _SCRIPT_DIR)


def get_config_dir():
    return os.path.dirname(get_filepath())


def get():
    return _CONFIG


def set_filepath(filepath):
    print("overriding config filepath with [%s]" % filepath)
    global _CONFIG_FILE_PATH
    _CONFIG_FILE_PATH = filepath


def set_override_password(password):
    global _OVERRIDE_PASSWORD
    _OVERRIDE_PASSWORD = password


def set_yes(yes):
    global _YES
    _YES = yes

def load_config():
    global _CONFIG
    print("Loading YAML config file [%s]..." % get_filepath())
    with open(get_filepath(), 'r') as f:
        _CONFIG = yaml.load(f)


def get_env():
    global _ENV_DATA
    if _ENV_DATA is None:
        _ENV_DATA = next(e for e in _CONFIG["Environments"] if e[
                         "Name"] == _ENVIRONMENT)
    if _OVERRIDE_PASSWORD != '':
        if _ENV_DATA is not None and _ENV_DATA["SQLConfig"] is not None:
            _ENV_DATA["SQLConfig"]["Password"] = _OVERRIDE_PASSWORD
    return _ENV_DATA


def set_env(env):
    global _ENVIRONMENT
    _ENVIRONMENT = validate_environment(env)


def validate_environment(env):
    if len(env) == 0:
        env = default_env()
        print("Running in default environment [%s]" % env)
    else:
        envs = [str(e["Name"]) for e in _CONFIG["Environments"]]
        if env not in envs:
            print("Not a valid environment, environment must be in %s" % envs)
            sys.exit(2)
        if env not in ("test", "dev"):
            msg = "Are you sure you want to use the '%s' env [yes/No]? " % env
            if not confirm(msg, "yes"):
                print("Environment not confirmed")
                sys.exit(2)
        print("Running in environment [%s]" % env)

    return env


def get_env_sql_cfg():
    env = get_env()
    return env["SQLConfig"]


def default_env():
    if len(_CONFIG["DefaultEnvironment"]) == 0:
        raise ConfigError("No DefaultEnvironment set")
    return _CONFIG["DefaultEnvironment"]


def get_migrations_dir():
    return replace_inlines(_CONFIG['MigrationsDirectory'])


def get_rollbacks_dir():
    return replace_inlines(_CONFIG['RollbacksDirectory'])


def get_seeds_dir():
    return replace_inlines(_CONFIG['SeedsDirectory'])


def replace_inlines(s):
    s = s.replace("{SCRIPT_DIR}", _SCRIPT_DIR)
    s = s.replace("{CONFIG_DIR}", get_config_dir())
    return s


class ConfigError(Exception):
    def __init__(self, message):
        self.message = message


def confirm(msg, confirm_response):
    if _YES:
        return True
    return input(msg).lower() == confirm_response.lower()
