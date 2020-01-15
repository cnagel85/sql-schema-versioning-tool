
import psycopg2
import re
import subprocess
import platform


class PGAdapterError(Exception):
    def __init__(self, message):
        self.message = message


class PGAdapter:
    dbConn = None

    def __init__(self, sqlCfg):
        self.driver = sqlCfg["Driver"]
        self.host = sqlCfg["Host"]
        self.port = sqlCfg["Port"]
        self.user = sqlCfg["User"]
        self.password = sqlCfg["Password"]
        self.database = sqlCfg["Database"]

    def get_db_connection(self):
        if not self.dbConn or self.dbConn:
            self.dbConn = psycopg2.connect(host=self.host, port=self.port,
                                           user=self.user,
                                           password=self.password,
                                           database=self.database)
            self.dbConn.autocommit = True
        return self.dbConn

    def create_database(self):
        db = self.get_db_connection()
        print("Creating database", self.database, "public schema")
        try:
            db.cursor().execute("CREATE SCHEMA public;")
            db.cursor().execute("GRANT ALL ON SCHEMA public TO postgres;")
            db.cursor().execute("GRANT ALL ON SCHEMA public TO %s;" %
                                self.user)
            # db.close()
        except psycopg2.Error as e:
            # db.close()
            if e.pgcode == "42P06":
                print("database(public schema) already exists")
            else:
                print(e.pgcode, e.pgerror)
                raise

    def drop_database(self):
        db = self.get_db_connection()
        print("Dropping database", self.database, "public schema")
        try:
            db.cursor().execute("DROP SCHEMA public CASCADE;")
            # db.close()
        except psycopg2.Error as e:
            # db.close()
            print(e.pgcode, e.pgerror)
            raise

    def query(self, query, limit=-1):
        db = self.get_db_connection()
        # print "[DEBUG] Executing SQL statement:\n\t%s" % query
        cursor = db.cursor()
        cursor.execute(query)
        if limit < 0:
            results = cursor.fetchall()
        elif limit == 1:
            results = cursor.fetchone()
        elif limit > 1:
            cursor.fetchmany(limit)
        else:
            raise PGAdapterError("invalid query row limit")
        return results

    def get_migrated_versions(self):
        versions = []
        try:
            rows = self.query("SELECT version FROM schema_migrations")
            for row in rows:
                versions.append(row[0])
        except psycopg2.Error as e:
            if e.pgcode != "42P01":
                raise
        return sorted(versions)

    def execute_sql_file(self, filepath):
        db = self.get_db_connection()
        print("[INFO] Executing SQL file: '%s'" % (filepath))
        print("[INFO] Executing SQL statements:\t")
        statement = ""
        try:
            cursor = db.cursor()
            for line in open(filepath, 'r'):
                # line = line.strip()
                if (re.match(r'--', line) or len(line) == 0):
                    continue
                if not re.search(r'[^-;]+;', line):
                    statement += line  # + " "
                else:
                    statement += line
                    # print "\n\n[DEBUG] Executing SQL statement:\n\t%s" %
                    # statement
                    print("\t" + statement)
                    try:
                        cursor.execute(statement)
                    except psycopg2.Error:
                        db.rollback()
                        raise
                    statement = ""

            db.commit()
        except psycopg2.Error:
            db.rollback()
            raise
        print("[INFO] Finished Excuting SQL file")

    def create_table_dump(self, filepath):
        if platform.system() != "Linux":
            print("Table dump only implemented for linux environments.")
            return
        try:
            process = subprocess.Popen(
                ['pg_dump',
                 '--dbname=postgresql://{}:{}@{}:{}/{}'.format(self.user, self.password, self.host, self.port, self.database),
                 '-n', "public",
                 '-f', filepath,
                 '-s',
                 '-O',
                 '-x']
            )
            process.communicate()[0]
            if process.returncode != 0:
                print('Command failed. Return code : {}'.format(process.returncode))
        except Exception as e:
            print(e)


def new_adapter(sqlCfg):
    return PGAdapter(sqlCfg)
