import sqlite3 as sq


class DataBase:
    def __init__(self, path_to_db='sql/CatMusic.db'):
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
        cash = []
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()



            for i in range(len(data)):
                cash.append(data[i][0])

            data = cash


        connection.close()

        return data

    def create_table_music(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Music(
        Id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        Artists TEXT,
        Title TEXT,
        Time TEXT,
        Extension TEXT,
        Path_Music TEXT);

        """
        self.execute(sql, commit=True)

    def add_music(self, Artists: str, Title: str, Time: str, Extension: str, Path_Music: str):
        sql = """
        INSERT INTO Music (Artists, Title,Time, Extension, Path_Music) VALUES(?,?,?,?,?)

        """
        parameteres = (Artists, Title, Time, Extension, Path_Music)

        self.execute(sql, parameters=parameteres, commit=True)

    def create_table_playlists(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Playlists(
        Id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        PlayLists TEXT);

        """
        self.execute(sql, commit=True)

    def create_table_playlistsSongs(self):
        sql = """
        CREATE TABLE IF NOT EXISTS PlaylistsSongs(
        IdSong INT,
        IdPlayLists INT);

        """
        self.execute(sql, commit=True)

    def create_table_result_request(self):
        sql = """
        CREATE TABLE IF NOT EXISTS ResultRequest(
        Id  INTEGER PRIMARY KEY NOT NULL,
        Artists TEXT,
        Title TEXT,
        Time TEXT,
        Extension TEXT,
        Path_Music TEXT);

        """
        self.execute(sql, commit=True)

    def delete_table_result_request(self):
        sql = """DELETE FROM ResultRequest"""
        self.execute(sql, commit=True)

    def add_playlist(self, playlist: str):
        sql = """
        INSERT INTO Playlists (PlayLists) VALUES(?)

        """
        parameteres = (playlist,)
        self.execute(sql, parameters=parameteres, commit=True)

    def output_music(self, Id:int,Artists: str, Title: str, Time: str, Extension: str, Path_Music: str):
        sql = """
                INSERT INTO ResultRequest (Id,Artists, Title,Time, Extension, Path_Music) VALUES(?,?,?,?,?,?)

                """
        parameteres = (Id,Artists, Title, Time, Extension, Path_Music)

        self.execute(sql, parameters=parameteres, commit=True)

    def return_playlists(self):
        sql = """
                        SELECT PlayLists from Playlists

                        """
        return self.execute(sql, fetchall=True)

    def get_id(self, playlist):
        sql = """
                        SELECT Id from Playlists WHERE PlayLists = ?

                        """
        parameteres = (playlist,)
        return self.execute(sql, fetchone=True, parameters=parameteres)

    def input_id(self, song_id, playlist_id):
        sql = """
                        INSERT INTO PlaylistsSongs (IdSong,IdPlaylists) VALUES(?,?)

                        """
        parameteres = (song_id, playlist_id)

        self.execute(sql, parameters=parameteres, commit=True)

    def return_songsID(self, IdPlaylists):
        sql = """
                        SELECT IdSong from PlaylistsSongs WHERE IdPlaylists = ?

                        """
        parameteres = (IdPlaylists,)
        return self.execute(sql, fetchall=True, parameters=parameteres)

    def return_songs_info(self, song_id):
        sql = """
                        SELECT * from Music WHERE Id = ?

                        """
        parameteres = (song_id,)
        return self.execute(sql, fetchone=True, parameters=parameteres)

    def return_music_path(self, song_id):
        sql = """
                                SELECT Path_Music from ResultRequest WHERE Id >= ?

                                """
        parameteres = (song_id,)
        return self.execute(sql, fetchall=True, parameters=parameteres)

    def return_play_song_id(self, path):
        sql = """
                                        SELECT Id from Music WHERE Path_Music = ?

                                        """
        parameteres = (*path,)

        return self.execute(sql, fetchone=True, parameters=parameteres)

    def return_all_songs_info(self):
        sql = """
                        SELECT * from Music 

                        """

        return self.execute(sql, fetchall=True)

    def return_all_songs_info_in_playlist(self):
        sql = """
                        SELECT * from ResultRequest 

                        """

        return self.execute(sql, fetchall=True)
