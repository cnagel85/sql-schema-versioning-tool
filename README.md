# sql-schema-versioning-tool
A simple tool for versioning and tracking SQL databases schemas inspired by Ruby on Rails schema migrations

Currently supports Mysql/MariaDB and Postgres

# Notes
Mysql/MariaDB requires MySQLdb python lib to be installed
Postgres requires requires Psycopg2 python lib installed


## Updates
* refactored lib/database.py
	* split out migrations into their own file and class
	* moved mysql and postgres specific code to their own adapter modules
	* changed database.py to have a class DB that calls its methods using the specified adapter
* Added support for postgres
