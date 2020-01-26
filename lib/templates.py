#!/usr/bin/env python3

_INITIAL_MIGRATION_TEXT = """\
CREATE TABLE schema_migrations (
    version varchar(255) NOT NULL,
    PRIMARY KEY (version)
);
-- DO NOT CHANGE ABOVE THIS LINE --
-- Place Migration statements below



-- DO NOT CHANGE BELOW THIS LINE --
INSERT INTO schema_migrations VALUES('%s');
"""

_NEW_MIGRATION_TEXT = """\
INSERT INTO schema_migrations VALUES('%s');
-- DO NOT CHANGE ABOVE THIS LINE --
-- Place Migration statements below



-- DO NOT CHANGE BELOW THIS LINE --
"""

_ROLLBACK_TEXT = """\
-- DO NOT CHANGE ABOVE THIS LINE --
-- Place Rollback Migration statements below



-- DO NOT CHANGE BELOW THIS LINE --
DELETE FROM schema_migrations WHERE version='%s';
"""

_NEW_SEED_TEXT = """\
-- DO NOT CHANGE ABOVE THIS LINE --
-- Place Seed statements below



-- DO NOT CHANGE BELOW THIS LINE --
"""


def initial_migration():
    return _INITIAL_MIGRATION_TEXT


def new_migration():
    return _NEW_MIGRATION_TEXT


def rollback():
    return _ROLLBACK_TEXT


def new_seed():
    return _NEW_SEED_TEXT


def get_template(name):
    if name is "initial_migration":
        return initial_migration()
    elif name is "new_migration":
        return new_migration()
    elif name is "rollback":
        return rollback()
    elif name is "new_seedfile":
        return new_seed()
    else:
        raise TemplateError("template not found")


class TemplateError:
    def __init__(self, message):
        self.message = message
