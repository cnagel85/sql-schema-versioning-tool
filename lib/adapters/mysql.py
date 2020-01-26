
import MySQLdb
import re


class MysqlAdapter:
    dbConn = None

    def __init__(self, sqlCfg):
        self.driver = sqlCfg["Driver"]
        self.host = sqlCfg["Host"]
        self.port = sqlCfg["Port"]
        self.user = sqlCfg["User"]
        self.password = sqlCfg["Password"]
        self.database = sqlCfg["Database"]

    def get_db_connection(self):
        if not self.dbConn:
            self.dbConn = MySQLdb.connect(host=self.host, port=self.port,
                                          user=self.user, passwd=self.password,
                                          db=self.database)
            self.dbConn.autocommit(True)
        return self.dbConn

    def get_mysql_connection(self):
        return MySQLdb.connect(host=self.host, port=self.port,
                               user=self.user, passwd=self.password)

    def create_database(self):
        db = self.get_mysql_connection()
        try:
            db.cursor().execute("CREATE DATABASE %s;" % self.database)
            db.close()
        except MySQLdb.Error as e:
            db.close()
            if e.args[0] == 1007:
                print("database already exists")
            else:
                raise

    def drop_database(self):
        db = self.get_mysql_connection()
        print("Dropping database " + self.database)

        try:
            db.cursor().execute("DROP DATABASE %s;" % self.database)
            db.close()
        except MySQLdb.Error as e:
            db.close()
            if e.args[0] != 1008:
                raise
            else:
                print("database does not exist")

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
            raise MysqlAdapterError("invalid query row limit")
        return results

    def get_migrated_versions(self):
        versions = []
        try:
            rows = self.query("SELECT version FROM schema_migrations")
            for row in rows:
                versions.append(row[0])
        except MySQLdb.Error as e:
            if e.args[0] != 1146:
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
                    except MySQLdb.Error:
                        db.rollback()
                        raise
                    statement = ""

            db.commit()
        except MySQLdb.Error:
            db.rollback()
            raise
        print("[INFO] Finished Excuting SQL file")


class MysqlAdapterError(Exception):
    def __init__(self, message):
        self.message = message


def new_adapter(sqlCfg):
    return MysqlAdapter(sqlCfg)
