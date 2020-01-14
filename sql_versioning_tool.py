#!/usr/bin/env python3

import os
import sys
import getopt
from lib import config, database, migrations, seeds

DOC = """\
NAME
    SQL Schema Versioning Tool

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
        specifies the path to a YAML config file default is
        versioning_config.yml in the same directory as this script

    -e environment
        specifies which environment from the config file to use defaults to
        the DefaultEnvironment in config

    -v version
        specifies a migration to rollback for db:rollback, will roll back in
        order of most recent version back to and including the specifed version

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
            runs all unmigrated database migrations in order

        rollback
            runs the rollback sql file of the most recent migration or can
            rollback to a specific version number by passing it with -v

FILES
    ./versioning_config.yml
        YAML config file conforming to versioning_config.yml.example
        Can be overridden with -c or --config=

AUTHOR
    Corey Nagel <coreyelliotnagel@gmail.com>

EXAMPLE
    python sql_versioning_tool.py -e test db:create
"""


def usage():
    print(DOC)


if __name__ == '__main__':
    try:
        long_args = ["help", "config=", "environment=", "version="]
        opts, args = getopt.getopt(sys.argv[1:], "hc:e:v:", long_args)
    except getopt.GetoptError as err:
        print("Opt Err :", str(err))
        usage()
        sys.exit(1)

    version = ''
    env = ''
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        if opt in ('-c', '--config'):
            config.set_filepath(arg)
        if opt in ('-e', '--environment'):
            env = arg
        if opt in ('-v', '--version'):
            version = arg

    # load config and environment data
    config.set_script_directory(os.path.dirname(os.path.realpath(__file__)))
    config.load_config()
    config.set_env(env)

    db = database.DB(config.get_env())
    # parse command
    for cmd in args:
        if cmd in ("initial_migration"):
            migrations.create_initial_migration()
            break
        elif cmd in ("new_migration"):
            migrations.create_new_migration()
            break
        elif cmd in ("new_seed"):
            seeds.create_seed()
            break
        elif cmd in ("db:create"):
            db.create()
            break
        elif cmd in ("db:drop"):
            db.drop()
            break
        elif cmd in ("db:clean"):
            db.clean()
            break
        elif cmd in ("db:version"):
            db.version()
            break
        elif cmd in ("db:migrate"):
            db.migrate()
            break
        elif cmd in ("db:seed"):
            db.seed()
            break
        elif cmd in ("db:rollback"):
            db.rollback(version)
            break
