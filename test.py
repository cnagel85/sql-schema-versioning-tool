#!/usr/bin/env python

from lib import test_helpers

_MYSQL_CONFIG_PATH = "./test/mysql/mysql_test_config.yml"
_POSTGRES_CONFIG_PATH = "./test/postgres/postgres_test_Config.yml"


def run_tests(tests=[]):
    test_helpers.hello()


if __name__ == '__main__':
    run_tests()
