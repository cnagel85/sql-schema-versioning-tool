#!/usr/bin/env python

import os
import re
import datetime

# import from .
import templates
import config
import files


class SeedError:
    def __init__(self, message):
        self.message = message


class Seed:
    TEMPLATE = "new_seedfile"

    def from_filepath(self, filepath):
        if not os.path.exists(filepath):
            raise SeedError("seed file not found")

        self.filepath = filepath
        self.filename = filepath.split("/")[-1]

        filename_parts = self.filename.replace(".sql", "").split("_")
        self.version = filename_parts[0]
        self.name = "_".join(filename_parts[1:])
        return self

    def new(self):
        self.name = self.prompt_seed_name()
        self.generate_filename()
        return self

    def prompt_seed_name(self):
        name_prompt = 'Enter seed name([a-z0-9_] only): '
        name = raw_input(name_prompt)
        name_not_exist = len(name) is 0
        while name_not_exist or re.match('^[a-z0-9_]+$', name) is None:
            print "Invalid seed name"
            name = raw_input(name_prompt)
        return name

    def run(self, db):
        db.execute_sql_file(self.filepath)

    def generate_filename(self):
        now = datetime.datetime.utcnow()
        self.version = now.strftime("%Y%m%d%H%M%S")
        self.filename = "%s_%s.sql" % (self.version, self.name)
        self.filepath = files.filepath(config.get_seeds_dir(), self.filename)

    def create_seed_file(self):
        directory = config.get_seeds_dir()
        f = files.check_sql_file_exists(config.get_seeds_dir(), self.name)
        if f:
            print "seed file already exists [%s]" % f
        else:
            filename = self.name + ".sql"
            print "creating seed file[%s]" % filename
            fileData = templates.get_template(self.TEMPLATE)
            files.create_file(directory, self.filename, fileData)


def create_seed():
    s = Seed().new()
    s.create_seed_file()


def get_seeds():
    return [get_seed(f) for f in get_seed_files()]


def get_seed(filepath):
    return Seed().from_filepath(filepath)


def get_seed_files():
    return files.get_sql_files(config.get_seeds_dir())
