import os
from psycopg2 import connect, DatabaseError

class DB():

    def __init__(self):

        self.__host = os.getenv("DATABASE_HOST")
        self.__port = os.getenv("DATABASE_PORT")
        self.__username = os.getenv("DATABASE_USER")
        self.__password = os.getenv("DATABASE_PASSWORD")
        self.__database = os.getenv("DATABASE_NAME")

        
        # connecting to the PostgreSQL server
        try:
            self.__config: dict = {
                "host": self.__host,
                "database": self.__database,
                "port": self.__port,
                "user": self.__username,
                "password": self.__password
            }
            with connect(**self.__config) as self.__conn:
                self._cursor = self.__conn.cursor()
        
        except (DatabaseError, Exception) as error:
            print(error)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    @ property
    def connection(self):
        return self.__conn

    @ property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def executemany(self, sql, params=None):
        self.cursor.executemany(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()