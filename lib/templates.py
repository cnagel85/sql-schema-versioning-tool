#!/usr/bin/env python

_INITIAL_MIGRATION_TEXT = """BEGIN TRANSACTION;
CREATE TABLE schema_migrations (version varchar(255) NOT NULL, PRIMARY KEY (version));
-- DO NOT CHANGE ABOVE THIS LINE
-- Place Migration statements below



-- DO NOT CHANGE BELOW THIS LINE
INSERT INTO schema_migrations VALUES('%s');
COMMIT;
"""

_NEW_MIGRATION_TEXT = """BEGIN TRANSACTION;
INSERT INTO schema_migrations VALUES('%s');
-- DO NOT CHANGE ABOVE THIS LINE
-- Place Migration statements below



-- DO NOT CHANGE BELOW THIS LINE
COMMIT;
"""

_ROLLBACK_TEXT = """BEGIN TRANSACTION;
-- DO NOT CHANGE ABOVE THIS LINE
-- Place Rollback Migration statements below



-- DO NOT CHANGE BELOW THIS LINE
DELETE FROM schema_migrations WHERE version='%s';
COMMIT;
"""

def initial_migration():
	return _INITIAL_MIGRATION_TEXT

def new_migration():
	return _NEW_MIGRATION_TEXT

def rollback():
	return _ROLLBACK_TEXT
