#!/usr/bin/env python3

import os
import re
import datetime

# import from .
from . import templates
from . import config
from . import files


class MigrationBase:
    INITIAL = "initial"

    def from_filepath(self, filepath):
        if not os.path.exists(filepath):
            raise MigrationError("Migration file not found")

        self.filepath = filepath
        self.filename = filepath.split("/")[-1]

        filename_parts = self.filename.replace(".sql", "").split("_")
        self.version = filename_parts[0]
        self.name = "_".join(filename_parts[1:])
        return self

    def run(self, db):
        db.execute_sql_file(self.filepath)

    def generate_filename(self):
        now = datetime.datetime.utcnow()
        self.version = now.strftime("%Y%m%d%H%M%S")
        self.filename = "%s_%s.sql" % (self.version, self.name)
        self.filepath = files.filepath(config.get_migrations_dir(), self.filename)

    def create_migration_file(self):
        directory = config.get_migrations_dir()
        f = self.migration_file_exists()
        if f:
            print("migration file already exists [%s]" % f)
        else:
            print("creating migration file[%s]" % self.filename)
            fileData = templates.get_template(self.TEMPLATE) % self.version
            files.create_file(directory, self.filename, fileData)

    def migration_file_exists(self):
        return files.check_sql_file_exists(config.get_migrations_dir(), self.version)


class InitialMigration(MigrationBase):
    TEMPLATE = "initial_migration"

    def new(self):
        self.name = self.INITIAL
        self.generate_filename()
        return self

    def create_files(self):
        self.create_migration_file()

    def migration_file_exists(self):
        return files.check_sql_file_exists(config.get_migrations_dir(), self.name)

    def rollback(self, db):
        print("Rollback of initial migration requested")
        db.clean()


class Migration(MigrationBase):
    TEMPLATE = "new_migration"

    def new(self):
        self.name = self.prompt_migration_name()
        self.generate_filename()
        return self

    def prompt_migration_name(self):
        name_prompt = 'Enter migration name([a-z0-9_] only): '
        name = input(name_prompt)
        name_not_exist = len(name) is 0 or self.INITIAL in name
        while name_not_exist or re.match('^[a-z0-9_]+$', name) is None:
            print("Invalid migration name")
            name = input(name_prompt)
        return name

    def create_files(self):
        self.create_migration_file()
        self.create_rollback_file()

    def rollback(self, db):
        db.execute_sql_file(self.rollback_filepath())

    def create_rollback_file(self):
        directory = config.get_rollbacks_dir()
        f = self.rollback_file_exists()
        if f:
            print("migration rollback file already exists [%s]" % f)
        else:
            rbName = self.rollback_filename()
            fileData = templates.get_template("rollback") % self.version
            files.create_file(directory, rbName, fileData)

    def rollback_filepath(self):
        return files.filepath(config.get_rollbacks_dir(), self.rollback_filename())

    def rollback_filename(self):
        return self.filename.replace('.sql', '_rollback.sql')

    def rollback_file_exists(self):
        files.check_sql_file_exists(config.get_rollbacks_dir(), self.version)


class MigrationError:
    def __init__(self, message):
        self.message = message


def create_initial_migration():
    im = InitialMigration().new()
    im.create_files()


def create_new_migration():
    if not check_for_initial_migration():
        raise MigrationError("must create initial migration first")
    m = Migration().new()
    m.create_files()


def check_for_initial_migration():
    directory = config.get_migrations_dir()
    return files.check_sql_file_exists(directory, MigrationBase.INITIAL)


def get_migrations():
    return [get_migration(f) for f in get_migrations_files()]


def get_migrated(migrated_versions):
    migrated = []
    for v in migrated_versions:
        for f in get_migrations_files():
            if v in f:
                migrated.append(get_migration(f))
                break
    return migrated


def get_migration(filepath):
    if MigrationBase.INITIAL in filepath:
        m = InitialMigration().from_filepath(filepath)
    else:
        m = Migration().from_filepath(filepath)
    return m


def get_migrations_files():
    return files.get_sql_files(config.get_migrations_dir())
