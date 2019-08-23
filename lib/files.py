#!/usr/bin/env python

import os
import glob


def filepath(dirPath, filename):
    return "%s/%s" % (dirPath, filename)


def create_file(directory, filename, file_data):
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Create file
    filepath = directory + "/" + filename
    with open(filepath, "w+") as f:
        f.write(file_data)


def check_sql_file_exists(directory, identifier):
    return check_file_with_id_exists(directory, identifier, "sql")


def check_file_with_id_exists(directory, identifier, extension):
    print "checking for file with identifier[%s] and extension[%s]" % (identifier, extension),
    print "in dir[%s]" % directory
    for filename in glob.glob("%s/*.%s" % (directory, extension)):
        if identifier in filename:
            return filename
    return False


def get_sql_files(directory):
    return sorted(glob.glob(directory + "/*.sql"))
