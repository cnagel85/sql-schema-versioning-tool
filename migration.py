#!/usr/bin/env python
import os, shlex, subprocess, getopt, sys, json, yaml, re, datetime, glob


MIGRATIONs_DIR = './migrations'
ROLLBACKS_DIR = MIGRATIONs_DIR + '/rollbacks'
MIGRATION_NAME_PROMPT = 'Enter migration name([a-z0-9_] only): '
INITIAL_MIGRATION_TEXT = """BEGIN TRANSACTION;
CREATE TABLE "schema_migrations" ("version" varchar(255) NOT NULL PRIMARY KEY);
INSERT INTO "schema_migrations" VALUES('%s');
-- Place Migration statements below



-- DO NOT CHANGE BELOW THIS LINE
COMMIT;
"""
NEW_MIGRATION_TEXT = """BEGIN TRANSACTION;
INSERT INTO "schema_migrations" VALUES('%s');
-- Place Migration statements below



-- DO NOT CHANGE BELOW THIS LINE
COMMIT;
"""

ROLLBACK_TEXT = """BEGIN TRANSACTION;
-- Place Rollback Migration statements below



-- DO NOT CHANGE BELOW THIS LINE
DELETE FROM "schema_migrations" WHERE version='%s');
COMMIT;
"""

def CreateInitialMigration():
	if checkForInitialMigration():
		print "initial migration already exists"
		sys.exit(2)

	# Create initial migration file
	createMigrationFile(generateFileName('initial'), INITIAL_MIGRATION_TEXT)

def CreateNewMigration():
	if not checkForInitialMigration():
		print "must create initial igration first"
		sys.exit(2)

	# Create New Migration File
	filename = generateFileName("")
	createMigrationFile(filename, NEW_MIGRATION_TEXT)
	createRollbackFile(filename)

def createMigrationFile(filename, filetext):
	print "Creating SQL Migration file: ", filename

	# Create Migration Directory if it doesnt exist
	if not os.path.exists(MIGRATIONs_DIR):
		os.makedirs(MIGRATIONs_DIR)

	# Create Migration file
	with open(MIGRATIONs_DIR+"/"+filename, "w+") as f:
		f.write(filetext % filename.split('_')[0])

def createRollbackFile(migration_filename):
	filename = migration_filename.replace('.sql','_rollback.sql')
	print "Creating SQL Rollback Migration file: ", filename

	# Create Rollback Migrations Directory if it doesnt exist
	if not os.path.exists(ROLLBACKS_DIR):
		os.makedirs(ROLLBACKS_DIR)

	# Create Rollback Migration file
	with open(ROLLBACKS_DIR+"/"+filename, "w+") as f:
		f.write(ROLLBACK_TEXT % filename.split('_')[0])


def checkForInitialMigration():
    try:
    	for file in glob.glob(MIGRATIONs_DIR+"/*.sql"):
    		if 'initial' in file:
    			return True
    except IOError as e:
    	print "failed migration files check"
    	sys.exit(2)
    return False


def generateFileName(name):
	if len(name) == 0:
		name = promptMigrationName()
	now = datetime.datetime.utcnow()
	return "%s_%s.sql" % (now.strftime("%Y%m%d%H%M%S"), name)


def promptMigrationName():
	name = raw_input(MIGRATION_NAME_PROMPT)
	while (len(name) == 0 or name == "initial" or re.match('^[a-z0-9_]+$', name) == None):
		print "Invalid migration name"
		name = raw_input(MIGRATION_NAME_PROMPT)
	return name


if __name__ == '__main__':
	try:
		long_args = ["help", "initial", "new"]
		opts, args = getopt.getopt(sys.argv[1:], "h", long_args)
	except getopt.GetoptError:
		print "Opt Err : " + getopt.GetoptError
		sys.exit(2)

	for cmd in args:
		if cmd in ("initial"):
			CreateInitialMigration()
		if cmd in ("new"):
			CreateNewMigration()
