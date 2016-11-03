#!/usr/bin/env python
import os
import sys
import glob
import re
import datetime
import MySQLdb
import psycopg2
from . import config, templates


def get_db_connection():
    sqlCfg = config.get_env_sql_cfg()

    if sqlCfg["Driver"] == "mysql":
        dbConn = MySQLdb.connect(host=sqlCfg['Host'], port=sqlCfg['Port'],
                                 user=sqlCfg['User'], passwd=sqlCfg[
                                     'Password'],
                                 db=sqlCfg['Database'])
        dbConn.autocommit(False)
    elif sqlCfg["Driver"] == "postgres":
        dbConn = psycopg2.connect(host=sqlCfg['Host'], port=sqlCfg['Port'],
                                  user=sqlCfg['User'], password=sqlCfg[
                                      'Password'],
                                  database=sqlCfg['Database'])

    return dbConn


def create_database():
    sqlCfg = config.get_env_sql_cfg()

    database = sqlCfg['Database']
    if sqlCfg["Driver"] == "mysql":
        print "Creating database", database

        dbConn = MySQLdb.connect(host=sqlCfg['Host'], port=sqlCfg['Port'],
                                 user=sqlCfg['User'],
                                 passwd=sqlCfg['Password'])
        try:
            dbConn.cursor().execute("CREATE DATABASE %s;" % database)
            dbConn.close()
        except MySQLdb.Error as e:
            dbConn.close()
            if e[0] == 1007:
                print "database already exists"
            else:
                raise

    elif sqlCfg["Driver"] == "postgres":
        dbConn = psycopg2.connect(host=sqlCfg['Host'], port=sqlCfg['Port'],
                                  user=sqlCfg['User'],
                                  password=sqlCfg['Password'],
                                  database=database)
        dbConn.set_isolation_level(0)

        print "Creating database", database, "public schema"
        try:
            dbConn.cursor().execute("CREATE SCHEMA public;")
            dbConn.cursor().execute("GRANT ALL ON SCHEMA public TO postgres;")
            dbConn.cursor().execute("GRANT ALL ON SCHEMA public TO %s;" %
                                    sqlCfg['User'])
            dbConn.close()
        except psycopg2.Error as e:
            dbConn.close()
            if e.pgcode == "42P06":
                print "database(public schema) already exists"
            else:
                print e.pgcode, e.pgerror
                raise


def drop_database():
    env = config.get_env()
    sqlCfg = config.get_env_sql_cfg()

    database = sqlCfg['Database']
    if env["Name"] != "test":
        msg = "[WARNING] Are you sure you want to drop[all data will \
        be lost] database with name %s [yes/No]? "
        if not config.confirm(msg % database, 'yes'):
            print "Exiting without dropping database"
            sys.exit(0)

    if sqlCfg["Driver"] == "mysql":
        print "Dropping database " + database
        dbConn = MySQLdb.connect(host=sqlCfg['Host'], port=sqlCfg[
                                 'Port'], user=sqlCfg['User'],
                                 passwd=sqlCfg['Password'])
        try:
            dbConn.cursor().execute("DROP DATABASE %s;" % database)
            dbConn.close()
        except MySQLdb.Error as e:
            dbConn.close()
            if e[0] != 1008:
                raise
            else:
                print "database does not exist"
    elif sqlCfg["Driver"] == "postgres":
        print "Dropping database", database, "public schema"
        dbConn = psycopg2.connect(host=sqlCfg['Host'], port=sqlCfg['Port'],
                                  user=sqlCfg['User'],
                                  password=sqlCfg['Password'],
                                  database=database)
        dbConn.set_isolation_level(0)
        try:
            dbConn.cursor().execute("DROP SCHEMA public CASCADE;")
            dbConn.close()
        except psycopg2.Error as e:
            dbConn.close()
            print e.pgcode, e.pgerror
            raise


def clean_database():
    print "Attempting to drop database"
    drop_database()
    print "Attempting to recreate clean database"
    create_database()


def create_initial_migration():
    if check_for_initial_migration():
        print "initial migration already exists"
        sys.exit(1)

    # Create initial migration file
    create_migration_file(generate_filename('initial'),
                          templates.initial_migration())


def create_new_migration():
    if not check_for_initial_migration():
        print "must create initial igration first"
        sys.exit(1)

    # Create New Migration File
    filename = generate_filename("")
    create_migration_file(filename, templates.new_migration())
    create_rollback_file(filename)


def create_migration_file(filename, filetext):
    print "Creating SQL Migration file: ", filename
    migration_dir = config.get_migrations_dir()
    # Create Migration Directory if it doesnt exist
    if not os.path.exists(migration_dir):
        os.makedirs(migration_dir)

    # Create Migration file
    with open(migration_dir + "/" + filename, "w+") as f:
        f.write(filetext % filename.split('_')[0])


def create_rollback_file(migration_filename):
    filename = migration_filename.replace('.sql', '_rollback.sql')
    print "Creating SQL Rollback Migration file: ", filename

    rollbacks_dir = config.get_rollbacks_dir()
    # Create Rollback Migrations Directory if it doesnt exist
    if not os.path.exists(rollbacks_dir):
        os.makedirs(rollbacks_dir)

    # Create Rollback Migration file
    with open(rollbacks_dir + "/" + filename, "w+") as f:
        f.write(templates.rollback() % filename.split('_')[0])


def check_for_initial_migration():
    try:
        for file in glob.glob(config.get_migrations_dir() + "/*.sql"):
            if 'initial' in file:
                return True
    except IOError:
        print "failed migration files check"
        sys.exit(1)
    return False


def generate_filename(name):
    if len(name) == 0:
        name = prompt_migration_name()
    now = datetime.datetime.utcnow()
    return "%s_%s.sql" % (now.strftime("%Y%m%d%H%M%S"), name)


def prompt_migration_name():
    name_prompt = 'Enter migration name([a-z0-9_] only): '
    name = raw_input(name_prompt)
    name_not_exist = len(name) is 0 or name is "initial"
    while name_not_exist or re.match('^[a-z0-9_]+$', name) is None:
        print "Invalid migration name"
        name = raw_input(name_prompt)
    return name


def run_migration():
    db = get_db_connection()

    migrated = get_current_migrated_versions(db)
    # print migrated
    for file in get_migrations_files():
        if extract_migration_version(file) not in migrated:
            execute_sql_file(db, file)


def run_rollback(version=''):
    db = get_db_connection()

    migrated = get_current_migrated_versions(db)
    if len(migrated) == 0:
        print "no migrations to rollback"
        return
    migrated.reverse()

    # confirm rollback version exists
    if version == '':
        version = migrated[0]
    elif version not in migrated:
        print "Cannot find migration %s in migrated" % version
        raise DBError("Migration Not Found")

    # get migrations to rollback
    toRollback = []
    for m in migrated:
        toRollback.append(m)
        if m == version:
            break

    # rollback each migration in descending order
    for rVersion in toRollback:
        if rVersion != migrated[-1]:
            for file in get_rollback_files():
                if rVersion in file:
                    execute_sql_file(db, file)
                    break
        else:
            print "Rollback of initial migration requested"
            clean_database()
            sys.exit(0)


def get_version():
    db = get_db_connection()
    migrated = get_current_migrated_versions(db)
    if len(migrated) > 0:
        print "Current migration version: " + migrated[-1]
    else:
        print "No version data in database"


def get_current_migrated_versions(db):
    versions = []
    try:
        query = "SELECT version FROM schema_migrations"
        # print "[DEBUG] Executing SQL statement:\n\t%s" % query
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        for row in cursor.fetchall():
            versions.append(row[0])
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] != 1146:
            raise
    except psycopg2.Error as e:
        db.rollback()
        if e.pgcode != "42P01":
            raise

    versions = sorted(versions)
    print "Found migration versions: %s" % versions
    return versions


def get_migrations_files():
    try:
        return sorted(glob.glob(config.get_migrations_dir() + "/*.sql"))
    except IOError:
        print "no migration files found"
        sys.exit(1)


def get_rollback_files():
    try:
        files = sorted(glob.glob(config.get_rollbacks_dir() + "/*.sql"))
        files.reverse()
        return files
    except IOError:
        print "no migration files found"
        sys.exit(1)


def extract_migration_version(filename):
    return filename.split("/")[-1].split("_")[0]


def execute_sql_file(db, filename):
    print "[INFO] Executing SQL file: '%s'" % (filename)
    print "[INFO] Executing SQL statements:\t"
    statement = ""
    try:
        cursor = db.cursor()
        for line in open(filename, 'r'):
            # line = line.strip()
            if re.match('BEGIN TRANSACTION;', line):
                continue
            if re.match('COMMIT;', line):
                continue
            if (re.match(r'--', line) or len(line) == 0):
                continue
            if not re.search(r'[^-;]+;', line):
                statement += line  # + " "
            else:
                statement += line
                # print "\n\n[DEBUG] Executing SQL statement:\n\t%s" %
                # statement
                print "\t" + statement
                try:
                    cursor.execute(statement)
                except MySQLdb.Error:
                    db.rollback()
                    raise
                statement = ""

        db.commit()
    except MySQLdb.Error:
        db.rollback()
        raise
    print "[INFO] Finished Excuting SQL file"


class DBError(Exception):
    def __init__(self, message):
        self.message = message
