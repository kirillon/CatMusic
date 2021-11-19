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

    def create_table_music(self):  # создание таблицы Music
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

    def add_music(self, artists: str, title: str, time: str, extension: str, path_music: str):
        sql = """
        INSERT INTO Music (Artists, Title,Time, Extension, Path_Music) VALUES(?,?,?,?,?)

        """
        parameters = (artists, title, time, extension, path_music)

        self.execute(sql, parameters=parameters, commit=True)

    def create_table_playlists(self):  # создание таблицы Playlists
        sql = """
        CREATE TABLE IF NOT EXISTS Playlists(
        Id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        PlayLists TEXT);

        """
        self.execute(sql, commit=True)

    def create_table_playlists_songs(self):  # создание таблицы  PlaylistsSongs
        sql = """
        CREATE TABLE IF NOT EXISTS PlaylistsSongs(
        IdSong INT,
        IdPlayLists INT);

        """
        self.execute(sql, commit=True)

    def create_table_result_request(self):  # создание таблицы  ResultRequest
        sql = """
        CREATE TABLE IF NOT EXISTS ResultRequest(
        Id  INTEGER  NOT NULL,
        Artists TEXT,
        Title TEXT,
        Time TEXT,
        Extension TEXT,
        Path_Music TEXT);

        """
        self.execute(sql, commit=True)

    def delete_table_result_request(self):  # запрос на удаление таблицы
        sql = """DELETE FROM ResultRequest"""
        self.execute(sql, commit=True)

    def add_playlist(self, playlist: str):  # запрос на добавление таблицы
        sql = """
        INSERT INTO Playlists (PlayLists) VALUES(?)

        """
        parameters = (playlist,)
        self.execute(sql, parameters=parameters, commit=True)

    def output_music(self, id_output: int, artists: str, title: str, time: str, extension: str, path_music: str):
        # запрос на отображение плейлиста
        sql = """
                INSERT INTO ResultRequest (Id,Artists, Title,Time, Extension, Path_Music) VALUES(?,?,?,?,?,?)

                """
        parameters = (id_output, artists, title, time, extension, path_music)

        self.execute(sql, parameters=parameters, commit=True)

    def return_playlists(self):  # запрос на возращение название всех плейлистов
        sql = """
                        SELECT PlayLists from Playlists

                        """
        return self.execute(sql, fetchall=True)

    def get_id(self, playlist):  # запрос на возращение id плейлистов
        sql = """
                        SELECT Id from Playlists WHERE PlayLists = ?

                        """
        parameters = (playlist,)
        return self.execute(sql, fetchone=True, parameters=parameters)

    def input_id(self, song_id, playlist_id):  # запрос на добавление песни в плейлист
        sql = """
                        INSERT INTO PlaylistsSongs (IdSong,IdPlaylists) VALUES(?,?)

                        """
        parameters = (song_id, playlist_id)

        self.execute(sql, parameters=parameters, commit=True)

    def return_songs_id(self, id_playlists):  # запрос на возращение id песен в плейлистах
        sql = """
                        SELECT IdSong from PlaylistsSongs WHERE IdPlaylists = ?

                        """
        parameters = (id_playlists,)
        return self.execute(sql, fetchall=True, parameters=parameters)

    def return_songs_info(self, song_id):  # запрос возвращение на всей информации из Music
        sql = """
                        SELECT * from Music WHERE Id = ?

                        """
        parameters = (song_id,)

        return self.execute(sql, fetchone=True, parameters=parameters)

    def return_music_path(self, song_id):  # запрос возвращение пути аудиофайла
        sql = """
                                SELECT Path_Music from ResultRequest WHERE Id >= ?

                                """
        parameters = (song_id,)
        return self.execute(sql, fetchall=True, parameters=parameters)

    def return_play_song_id(self, path):  # запрос возвращение id из Music
        sql = """
                                        SELECT Id from Music WHERE Path_Music = ?

                                        """
        parameters = (*path,)

        return self.execute(sql, fetchone=True, parameters=parameters)

    def return_all_songs_info(self):  # запрос возвращение на всей информации из Music
        sql = """
                        SELECT * from Music 

                        """

        return self.execute(sql, fetchall=True)

    def return_all_songs_info_in_playlist(self):  # запрос возвращение на всей информации из ResultRequest
        sql = """
                        SELECT * from ResultRequest 

                        """

        return self.execute(sql, fetchall=True)

    def duplicate_check(self, id_song):  # проверка на дубликат
        sql = """
                           SELECT IdPlayLists from PlaylistsSongs WHERE IdSong = ?

                           """
        parameters = (id_song,)
        return self.execute(sql, fetchone=True, parameters=parameters)

    def delete_music(self, song_id):  # запрос на удаление музыки
        sql = """
                                DELETE from Music WHERE Id = ?

                                """
        parameters = (song_id,)
        self.execute(sql, parameters=parameters, commit=True)

    def update_name_playlist(self, playlist, id_pl):  # запрос на изменение названия плейлиста
        sql = """
                        UPDATE Playlists SET Playlists = ? WHERE Id = ?

                        """
        parameters = (playlist, id_pl,)
        return self.execute(sql, parameters=parameters, commit=True)

    def delete_playlist_music(self, playlist_id):  # запрос на удаление всей музыки из плейлиста при удалении плейлиста
        sql = """
                                DELETE from PlaylistsSongs WHERE IdPlayLists = ?

                                """
        parameters = (playlist_id,)
        self.execute(sql, parameters=parameters, commit=True)

    def delete_playlist(self, playlist_id):  # запрос на удаление плейлиста
        sql = """
                                       DELETE from Playlists WHERE Id = ?

                                       """
        parameters = (playlist_id,)
        self.execute(sql, parameters=parameters, commit=True)

    def delete_music_from_playlist(self, song_id):  # запрос на удаление музыки из плейлиста
        sql = """
                                DELETE from PlaylistsSongs WHERE IdSong = ?

                                """
        parameters = (song_id,)
        self.execute(sql, parameters=parameters, commit=True)
