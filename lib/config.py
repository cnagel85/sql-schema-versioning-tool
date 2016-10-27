#!/usr/bin/env python

import os, yaml

_DIR = os.path.dirname(os.path.realpath(__file__))
_CONFIG_FILE_PATH = "%s/migration_config.yml" % _DIR
_CONFIG = {}
_ENVIRONMENT = "dev"
_ENV_DATA = None


def get_filepath():
	return _CONFIG_FILE_PATH


def get():
	return _CONFIG


def set_filepath(filepath):
	print "overriding config filepath with [%s]" % filepath
	global _CONFIG_FILE_PATH
	_CONFIG_FILE_PATH = filepath


def load_config():
	global _CONFIG
	print "Loading YAML config file [%s]..." % _CONFIG_FILE_PATH
	with open(_CONFIG_FILE_PATH, 'r') as f:
		_CONFIG = yaml.load(f)


def get_env():
	global _ENV_DATA
	if _ENV_DATA == None:
		_ENV_DATA = next(e for e in _CONFIG["Environments"] if e["Name"] == _ENVIRONMENT)
	return _ENV_DATA


def set_env(env):
	global _ENVIRONMENT
	_ENVIRONMENT = validate_environment(env)


def validate_environment(env):
	if len(env) == 0:
		env = default_env()
		print "Running in default environment [%s]" % env
	else:
		envs = [str(e["Name"]) for e in _CONFIG["Environments"]]
		if env not in envs:
			print "Not a valid environment, environment must be in %s" % envs
			sys.exit(2)
		if env not in ("test", "dev"):
			msg = "Are you sure you want to use the '%s' environment [yes/No]?" % env
			resp = raw_input(msg)
			if resp.lower() not in ('yes'):
				print "Non-Dev Environment not confirmed"
				sys.exit(2)
		print "Running in environment [%s]" % env

	return env


def get_env_sql_cfg():
	env = get_env()
	return env["SQLConfig"]


def default_env():
	try:
		if len(_CONFIG["DefaultEnvironment"]) > 0:
			return _CONFIG["DefaultEnvironment"]

	except:
		raise ConfigError("No DefaultEnvironment set")


def get_migrations_dir():
	return _CONFIG['MigrationsDirectory'].replace("{{SCRIPT_DIRECTORY}}", _DIR)


def get_rollbacks_dir():
	return _CONFIG['RollbacksDirectory'].replace("{{SCRIPT_DIRECTORY}}", _DIR)


class ConfigError(Exception):
	def __init__(self, message):
		self.message = message
