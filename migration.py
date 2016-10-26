#!/usr/bin/env python
import os, shlex, subprocess, getopt, sys, json, yaml, re, datetime, glob
# import mysql.connector as mariadb
import MySQLdb

_DIR = os.path.dirname(os.path.realpath(__file__))

_CONFIG_FILE_PATH = "%s/migration_config.yml" % _DIR
_ENVIRONMENT = "dev" # default is dev
_ENV_DATA = {}
_CONFIG = {}
_DB = 0 # placeholder value for db connection global

# MIGRATIONs_DIR = './migrations'
# ROLLBACKS_DIR = MIGRATIONs_DIR + '/rollbacks'
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
DELETE FROM schema_migrations WHERE version='%s');
COMMIT;
"""

DOC = """\
NAME
	SQL Schema Migration Tool

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
		specifies the path to a YAML config file default is migration_config.yml
		in the same directory as this script

	-e environment
		specifies which environment from the config file to use

	-v version
		specifies a migration to rollback to for db:rollback

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
			runs all database migrations in order

		rollback
			runs the rollback sql file of the most recent migration or can rollback
			to a specific version if -v is passed

FILES
	migration_config.yml
		YAML config file conforming to migration_config.yml.example
		Can be overridden with -c or --config=

AUTHOR
	Corey Nagel <coreyelliotnagel@gmail.com>

EXAMPLE
	python migration.py -e test db:create
"""

def usage():
	print DOC

def set_config_file_path(filepath):
	print "overriding config filepath with [%s]" % filepath
	global _CONFIG_FILE_PATH
	_CONFIG_FILE_PATH = filepath

def load_config(filename):
	print "Loading YAML config file [%s]..." % filename
	print filename
	with open(filename, 'r') as f:
		return yaml.load(f)

def get_env_config(env):
	return next(e for e in _CONFIG["Environments"] if e["Name"] == env)

def validate_environment(env):
	if len(env) == 0:
		env = _CONFIG["DefaultEnvironment"]
		print "Running in default environment [%s]" % env
	else:
		envs = [str(e["Name"]) for e in _CONFIG["Environments"]]
		if env not in envs:
			print "Not a valid environment, environment must be in %s" % envs
			sys.exit(2)
		if env not in ("test", "dev"):
			msg = "Are you sure you want to use the '%s' environment [yes/No]?" % env
			resp = raw_input(msg)
			if resp.lower() not in ('yes'):
				print "Non-Dev Environment not confirmed"
				sys.exit(2)
		print "Running in environment [%s]" % env

	return env

def create_initial_migration():
	if check_for_initial_migration():
		print "initial migration already exists"
		sys.exit(1)

	# Create initial migration file
	create_migration_file(generate_filename('initial'), _INITIAL_MIGRATION_TEXT)

def create_new_migration():
	if not check_for_initial_migration():
		print "must create initial igration first"
		sys.exit(1)

	# Create New Migration File
	filename = generate_filename("")
	create_migration_file(filename, _NEW_MIGRATION_TEXT)
	create_rollback_file(filename)

def create_migration_file(filename, filetext):
	print "Creating SQL Migration file: ", filename
	migration_dir = get_migrations_dir()
	# Create Migration Directory if it doesnt exist
	if not os.path.exists(migration_dir):
		os.makedirs(migration_dir)

	# Create Migration file
	with open(migration_dir+"/"+filename, "w+") as f:
		f.write(filetext % filename.split('_')[0])

def create_rollback_file(migration_filename):
	filename = migration_filename.replace('.sql','_rollback.sql')
	print "Creating SQL Rollback Migration file: ", filename

	rollbacks_dir = get_rollbacks_dir()
	# Create Rollback Migrations Directory if it doesnt exist
	if not os.path.exists(rollbacks_dir):
		os.makedirs(rollbacks_dir)

	# Create Rollback Migration file
	with open(rollbacks_dir+"/"+filename, "w+") as f:
		f.write(_ROLLBACK_TEXT % filename.split('_')[0])


def check_for_initial_migration():
    try:
    	for file in glob.glob(get_migrations_dir()+"/*.sql"):
    		if 'initial' in file:
    			return True
    except IOError as e:
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
	while (len(name) == 0 or name == "initial" or re.match('^[a-z0-9_]+$', name) == None):
		print "Invalid migration name"
		name = raw_input(name_prompt)
	return name

def get_db_connection():
	sql_config = _ENV_DATA['SQLConfig']
	dbConn = MySQLdb.connect(host=sql_config['Host'], port=sql_config['Port'], user=sql_config['User'], passwd=sql_config['Password'], db=sql_config['Database'])
	dbConn.autocommit(False)
	return dbConn

def run_migration():
	migrated = get_current_migrated_versions()
	# print migrated
	for file in get_migrations():
		if extract_migration_version(file) not in migrated:
			execute_sql_file(file)

def run_rollback(version=''):
	migrated = get_current_migrated_versions()
	migrated.reverse()
	if (len(migrated) < 2 or migrated[-1] == version):
		print "Rollback of initial migration requested"
		clean_database()
		sys.exit(0)

	toRollback = []
	if version == '':
		toRollback.append(migrated[0])
	else:
		if version not in migrated:
			print "[ERROR] Cannot find migration %s in migrated" % version
			sys.exit(1)
		for m in migrated:
			toRollback.append(m)
			if m == version:
				break
	for rVersion in toRollback:
		if rVersion != migrated[-1]:
			for file in get_rollbacks():
				if rVersion in file:
					execute_sql_file(file)
					break
		else:
			print "Rollback of initial migration requested"
			clean_database()
			sys.exit(0)

def get_version():
	migrated = get_current_migrated_versions(get_db_connection())
	if len(migrated) > 0 :
		print "Current migration version: "+ migrated[-1]
	else:
		print "No version data in database"

def get_current_migrated_versions(db=None):
	if db == None:
		db = _DB
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
		if e[0]!= 1146:
			raise

	versions = sorted(versions)
	print "Found migration versions: %s" % versions
	return versions

def get_migrations_dir():
	return _CONFIG['MigrationsDirectory'].replace("{{SCRIPT_DIRECTORY}}", _DIR)

def get_migrations():
    try:
    	return sorted(glob.glob(get_migrations_dir()+"/*.sql"))
    except IOError as e:
    	print "no migration files found"
    	sys.exit(1)

def get_rollbacks_dir():
	return _CONFIG['RollbacksDirectory'].replace("{{SCRIPT_DIRECTORY}}", _DIR)

def get_rollbacks():
    try:
    	files = sorted(glob.glob(get_rollbacks_dir()+"/*.sql"))
    	files.reverse()
    	return files
    except IOError as e:
    	print "no migration files found"
    	sys.exit(1)

def extract_migration_version(filename):
	return filename.split("/")[-1].split("_")[0]

def execute_sql_file(filename):
	print "[INFO] Executing SQL file: '%s'" % (filename)
	print "[INFO] Executing SQL statements:\t"
	statement = ""
	try:
		cursor = _DB.cursor()
		for line in open(filename, 'r'):
			# line = line.strip()
			if re.match('BEGIN TRANSACTION;', line):
				continue
			if re.match('COMMIT;', line):
				continue
			if (re.match(r'--', line) or len(line) == 0):
				continue
			if not re.search(r'[^-;]+;', line):
				statement += line #+ " "
			else:
				statement += line
				# print "\n\n[DEBUG] Executing SQL statement:\n\t%s" % statement
				print "\t"+statement
				try:
					cursor.execute(statement)
				except MySQLdb.Error as e:
					_DB.rollback()
					raise
				statement = ""

		_DB.commit()
	except MySQLdb.Error as e:
		_DB.rollback()
		raise
	print "[INFO] Finished Excuting SQL file"

def create_database():
	sql_config = _ENV_DATA['SQLConfig']
	database = sql_config['Database']
	dbConn = MySQLdb.connect(host=sql_config['Host'], port=sql_config['Port'], user=sql_config['User'], passwd=sql_config['Password'])

	print "Creating database "+database
	try:
		dbConn.cursor().execute("CREATE DATABASE %s;" % database)
		dbConn.close()
	except MySQLdb.Error as e:
		dbConn.close()
		if e[0] != 1007:
			raise
		else:
			print "database already exists"

def drop_database():
	sql_config = _ENV_DATA['SQLConfig']
	database = sql_config['Database']
	if _ENVIRONMENT != "test":
		if raw_input("[WARNING] Are you sure you want to drop database with name %s? " % database) != 'yes':
			print "Exiting without dropping database"
			sys.exit(0)

	dbConn = MySQLdb.connect(host=sql_config['Host'], port=sql_config['Port'], user=sql_config['User'], passwd=sql_config['Password'])
	print "Dropping database "+database
	try:
		dbConn.cursor().execute("DROP DATABASE %s;" % database)
		dbConn.close()
	except MySQLdb.Error as e:
		dbConn.close()
		if e[0] != 1008:
			raise
		else:
			print "database does not exist"

def clean_database():
	print "Attempting to drop database"
	drop_database()
	print "Attempting to recreate clean database"
	create_database()

if __name__ == '__main__':
	try:
		long_args = ["help", "config=", "environment=", "version="]
		opts, args = getopt.getopt(sys.argv[1:], "hc:e:v:", long_args)
	except getopt.GetoptError:
		print "Opt Err : " + getopt.GetoptError
		sys.exit(1)

	version = ''
	env = ''
	for opt, arg in opts:
		if opt in ('-h','--help'):
			usage()
			sys.exit(0)
		if opt in ('-c','--config'):
			set_config_file_path(arg)
		if opt in ('-e', '--environment'):
			env = arg
		if opt in ('-v', '--version'):
			version = arg

	# load config and environment data
	print _CONFIG_FILE_PATH
	_CONFIG = load_config(_CONFIG_FILE_PATH)
	_ENVIRONMENT = validate_environment(env)
	_ENV_DATA = get_env_config(_ENVIRONMENT)

	# parse commands
	migrate, rollback = False, False
	for cmd in args:
		if cmd in ("initial"):
			create_initial_migration()
			sys.exit(0)
		if cmd in ("new"):
			create_new_migration()
			sys.exit(0)
		if cmd in ("db:version"):
			get_version()
			sys.exit(0)
		if cmd in ("db:create"):
			create_database()
			sys.exit(0)
		if cmd in ("db:drop"):
			drop_database()
			sys.exit(0)
		if cmd in ("db:clean"):
			clean_database()
			sys.exit(0)
		if cmd in ("db:migrate"):
			migrate = True
		if cmd in ("db:rollback"):
			rollback = True

	# run command
	_DB = get_db_connection()
	if migrate:
		run_migration()
		sys.exit(0)
	if rollback:
		run_rollback(version)
		sys.exit(0)




