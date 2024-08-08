# sql-schema-versioning-tool
A simple tool for versioning and tracking SQL databases schemas inspired by Ruby on Rails schema migrations

## Note from Author
I created this tool to allow for an easier route to testing database schemas and updates as well as the ability to quickly bring up a clean test database for running tests or developing.

I would not necessarily advise using this tool in production. The ease of accidently calling a rollback, drop or clean on your database and possible security issues around having a db user that can easily do this make production use risky and the tool was not meant to be used in the same capacity as Rails database rake tasks.

Currently supports Mysql/MariaDB and Postgres

## Other Notes
General
* migration and rollback sql files require pure SQL to the corresponding database
* don't forget to fillout the rollback sql file for a migration, otherwise, a rollback will do nothing but decrement the database version
* migration files are not done as transactions, so each migration statement should have an unfailable undo statement in the rollback file(i.e. DROP TABLE IF EXISTS) if possible. This means caution is necessary with statements that can't be undone.
* initial migrations dont require a rollback file because the tool handles this rollback by running db:clean

Mysql/MariaDB
* requires MySQLdb python lib to be installed
* mysql user should have all privileges on the database you are using

Postgres
* requires requires Psycopg2 python lib installed
* postgres database should already exist and the user should be the owner of the database and the public schema, this allows the script to drop the database by dropping the public schema for the db and create by creating the public schema.  This means that extensions(i.e. uuid-ossp) need to be housed in a different schema from public


## Updates
* Updated to use Python3.8 instead of 2.7
* refactored lib/database.py
	* split out migrations into their own file and class
	* moved mysql and postgres specific code to their own adapter modules
	* changed database.py to have a class DB that calls its methods using the specified adapter
* Added support for postgres
* Added -y option to allow CI/CD integrations

## The Future
* Add SQLite support
* Write a test suite for the tools basic functionality and SQL adapters
