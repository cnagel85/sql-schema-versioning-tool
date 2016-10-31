#!/usr/bin/env python

import sys, getopt, os
from lib import config, database

DOC = """\
NAME
	SQL Schema Migration Tool

SYNOPSYS
	A tool for tracking and updating database schema versions inspired by
	Ruby on Rails database migrations.

DESCRIPTION


NOTICE
	Currently supports mysql and mariadb only
	requires yaml and MySQLdb python libraries

OPTIONS
	-h help
		show this help documentation

	-c config
		specifies the path to a YAML config file default is migration_config.yml
		in the same directory as this script

	-e environment
		specifies which environment from the config file to use

	-v version
		specifies a migration to rollback to for db:rollback

COMMANDS
	initial
		creates a migrations folder in the location specified by the config
		and creates an initial migration sql file
	new
		creates a new migration sql file in the migrations directory and a
		corresponding rollback sql file

	db:[command]
		the following db commands are run using the database specified in the
		config file

		create
			creates an empty database if none exists

		drop
			drops the database

		clean
			drops the current database and creates a new empty database

		version
			lists teh migration version of the database in the config file

		migrate
			runs all database migrations in order

		rollback
			runs the rollback sql file of the most recent migration or can rollback
			to a specific version if -v is passed

FILES
	migration_config.yml
		YAML config file conforming to migration_config.yml.example
		Can be overridden with -c or --config=

AUTHOR
	Corey Nagel <coreyelliotnagel@gmail.com>

EXAMPLE
	python migration.py -e test db:create
"""

def usage():
	print DOC

if __name__ == '__main__':
	try:
		long_args = ["help", "config=", "environment=", "version="]
		opts, args = getopt.getopt(sys.argv[1:], "hc:e:v:", long_args)
	except getopt.GetoptError:
		print "Opt Err : " + getopt.GetoptError
		sys.exit(1)

	version = ''
	env = ''
	for opt, arg in opts:
		if opt in ('-h','--help'):
			usage()
			sys.exit(0)
		if opt in ('-c','--config'):
			config.set_filepath(arg)
		if opt in ('-e', '--environment'):
			env = arg
		if opt in ('-v', '--version'):
			version = arg

	# load config and environment data
	config.set_script_directory(os.path.dirname(os.path.realpath(__file__)))
	config.load_config()
	config.set_env(env)

	# parse command
	for cmd in args:
		if cmd in ("initial"):
			database.create_initial_migration()
			sys.exit(0)
		if cmd in ("new"):
			database.create_new_migration()
			sys.exit(0)
		if cmd in ("db:version"):
			database.get_version()
			sys.exit(0)
		if cmd in ("db:create"):
			database.create_database()
			sys.exit(0)
		if cmd in ("db:drop"):
			database.drop_database()
			sys.exit(0)
		if cmd in ("db:clean"):
			database.clean_database()
			sys.exit(0)
		if cmd in ("db:migrate"):
			database.run_migration()
			sys.exit(0)
		if cmd in ("db:rollback"):
			database.run_rollback(version)
			sys.exit(0)

