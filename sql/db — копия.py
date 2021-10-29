import sqlite3 as sq


class DataBase:
    def __init__(self, path_to_db='sql\CatMusic.db'):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sq.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(sql, parameters)
        data = None
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()

        return data

    def create_table_music(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Music(
        Id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Artists TEXT,
        Title TEXT,
        Time TEXT,
        Extension TEXT);
        
        """
        self.execute(sql, commit=True)
        print(1)

    def add_music(self, Artists: str, Title: str, Time: str,Extension: str):
        sql = """
        INSERT INTO Music (Artists, Title,Time, Extension) VALUES(?,?,?,?)
        
        """
        parameteres = (Artists, Title,Time, Extension)

        self.execute(sql, parameters=parameteres, commit=True)
