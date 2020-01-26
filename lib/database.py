#!/usr/bin/env python3

import importlib

# import from .
from . import config
from . import migrations
from . import seeds


class DBError(Exception):
    def __init__(self, message):
        self.message = message


class DB():
    def __init__(self, envCfg):
        self.env = envCfg["Name"]
        self.sqlCfg = envCfg["SQLConfig"]
        self.driver = self.sqlCfg["Driver"]
        self.database = self.sqlCfg["Database"]
        self.init_db_adapter()

    def init_db_adapter(self):
        adapterLib = importlib.import_module(
            ".adapters.%s" % self.driver, "lib")
        self.adapter = adapterLib.new_adapter(self.sqlCfg)

    def create(self):
        self.adapter.create_database()

    def drop(self):
        if self.env != "test":
            msg = "[WARNING] Are you sure you want to drop[all data will \
                   be lost] database with name %s [yes/No]? "
            if not config.confirm(msg % self.database, 'yes'):
                print("Exiting without dropping database")
                return
        self.adapter.drop_database()

    def clean(self):
        print("Attempting to drop database")
        self.drop()
        print("Attempting to recreate clean database")
        self.create()

    def version(self):
        migrated = self.adapter.get_migrated_versions()
        print("Found migration versions: %s" % migrated)
        if len(migrated) > 0:
            print("Current migration version: " + migrated[-1])
        else:
            print("No version data in database")

    def execute_sql_file(self, filepath):
        self.adapter.execute_sql_file(filepath)

    def migrate(self):
        migrated = self.adapter.get_migrated_versions()
        for m in migrations.get_migrations():
            if m.version not in migrated:
                m.run(self)

    def rollback(self, version):
        migratedVersions = self.adapter.get_migrated_versions()
        if len(migratedVersions) == 0:
            print("no migrations to rollback")
            return
        migratedVersions.reverse()

        # confirm rollback version exists
        if version == '':
            version = migratedVersions[0]
        elif version not in migratedVersions:
            print("Cannot find migration %s in migrated" % version)
            raise DBError("Migration Not Found")

        # get migrations to rollback
        rollbackVersions = []
        for m in migratedVersions:
            rollbackVersions.append(m)
            if m == version:
                break

        # rollback each migration in descending order
        rollbacks = migrations.get_migrated(rollbackVersions)
        for migration in rollbacks:
            migration.rollback(self)

    def seed(self):
        for s in seeds.get_seeds():
            s.run(self)
