from asyncio import sleep

from PyQt5 import uic, QtSql, QtCore, QtWidgets
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtGui import QCursor
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHeaderView, QAbstractItemView, QMenu, QAction, QToolTip
import pygame
import os
from os import path
import threading
from mutagen.mp3 import MP3

from pagecode.add_playlists import AddPlayLists
from sql.db import DataBase
import requests

db = DataBase()

data = {
    'api_token': 'fd24256bddd932d2ff3ea89b26c5b77a',
    'accurate_offsets': 'true',
    'skip': '100',
    'every': '1',
}


class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("./Pages/mainpage.ui", self)  # Загружаем дизайн
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(500)  # Продолжительность: 1 секунда

        # Выполните постепенное увеличение
        self.doShow()
        pygame.mixer.init()
        self.id_song_play = None
        self.db = db
        self.flag_all_music_or_playlist = None
        self.horizontalSlider_2.setMinimum(0)
        self.horizontalSlider_2.setMaximum(1)
        self.horizontalSlider_2.setTickInterval(1)
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setTickInterval(1)
        self.horizontalSlider.setValue(70)
        self.flag_volume = 1
        self.name_music = None
        self.Time_Music()
        self.paths = None
        self.actionAdd_file.triggered.connect(self.load_file)
        self.actionAdd_Playlist.triggered.connect(self.add_playlist_to_db)
        self.horizontalSlider_2.sliderPressed.connect(self.Slider2_Pressed)
        self.horizontalSlider_2.sliderReleased.connect(self.Slider2_Released)
        self.horizontalSlider_2.sliderMoved.connect(self.Slider2_Moved)
        self.horizontalSlider.sliderMoved.connect(self.Slider1_Moved)
        self.toolButton_2.clicked.connect(self.button_on_off)
        self.toolButton_4.clicked.connect(self.Volume_on_off)
        self.toolButton.clicked.connect(self.back_button)
        self.toolButton_3.clicked.connect(self.next_button)
        db_connect = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        db_connect.setDatabaseName("sql/CatMusic.db")
        db_connect.open()

        self.model1 = QSqlTableModel()
        self.model1.setTable('Music')
        self.model1.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model1.select()
        self.tableView.setModel(self.model1)
        self.tableView.setColumnHidden(0, True)
        self.tableView.setColumnHidden(5, True)

        self.tableView.horizontalHeader().setSectionResizeMode(1)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.show()
        self.tableView.doubleClicked.connect(self.row_tableview_doubleClicked)
        self.model2 = QSqlTableModel()
        self.model2.setTable('Playlists')
        self.model2.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model2.select()
        self.tableView_2.setModel(self.model2)
        self.tableView_2.setColumnHidden(0, True)
        self.tableView_2.horizontalHeader().setSectionResizeMode(1)
        self.tableView_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView_2.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_2.show()
        self.tableView_2.doubleClicked.connect(self.row_tableview_2_doubleClicked)
        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.context_menu_music)
        self.model3 = QSqlTableModel()
        self.tableView_3.doubleClicked.connect(self.row_tableview3_doubleClicked)

    def doShow(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        # Диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def load_file(self):
        self.paths = None
        fname = QFileDialog.getOpenFileNames(
            self, 'Take a Music', '',
            'Music (*.mp3);;Music (*.wav);;All files (*)')[0]

        print(fname)

        self.name_music = path.splitext(os.path.basename(fname[-1]))[0]
        song = MP3(fname[-1])


        for index in fname:
            files = {
                'file': open(index, 'rb'),
            }
            result = requests.post('https://enterprise.audd.io/', data=data, files=files)

            if result.json()["status"] != "success":
                if "-" in index:
                    Artist, Title = path.splitext(os.path.basename(index))[0].split("-", 1)
                    self.db.add_music(Artists=Artist, Title=Title,
                                      Time=f"{int(MP3(index).info.length) // 60}:{str(int(MP3(index).info.length) % 60).zfill(2)}",
                                      Extension=path.splitext(os.path.basename(index))[1], Path_Music=index)
                else:

                    Artist, Title = "", path.splitext(os.path.basename(index))[0]
                    self.db.add_music(Artists=Artist, Title=Title,
                                      Time=f"{int(MP3(index).info.length) // 60}:{str(int(MP3(index).info.length) % 60).zfill(2)}",
                                      Extension=path.splitext(os.path.basename(index))[1], Path_Music=index)
            else:
                Artist = result.json()["result"][0]["songs"][0]["artist"]
                Title = result.json()["result"][0]["songs"][0]["title"]

                self.db.add_music(Artists=Artist, Title=Title,
                                  Time=f"{int(MP3(index).info.length) // 60}:{str(int(MP3(index).info.length) % 60).zfill(2)}",
                                  Extension=path.splitext(os.path.basename(index))[1], Path_Music=index)
                self.name_music = Artist + " - " + Title

        self.model1.setTable('Music')
        self.model1.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model1.select()
        self.tableView.setModel(self.model1)
        self.tableView.setColumnHidden(0, True)
        self.tableView.setColumnHidden(5, True)
        self.tableView.horizontalHeader().setSectionResizeMode(1)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.show()
        self.label.setText(self.name_music)
        self.label_2.setText(str(int(song.info.length)))
        print(str(int(song.info.length)))
        self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))

        self.id_song_play = self.db.return_all_songs_info()[-1]
        self.flag_all_music_or_playlist = 1
        pygame.mixer.music.load(fname[-1])

        pygame.mixer.music.play(0)
        self.toolButton_2.setChecked(True)

    def Time_Music(self):

        if self.horizontalSlider_2.value() // 1000 % 60 > 9:
            sec = str(self.horizontalSlider_2.value() // 1000 % 60)
        else:
            sec = f"0{self.horizontalSlider_2.value() // 1000 % 60}"

        self.horizontalSlider_2.setValue(pygame.mixer.music.get_pos())
        self.label_2.setText(f"{self.horizontalSlider_2.value() // 1000 // 60}:{sec}")
        self.timer = threading.Timer(0.001, self.Time_Music)
        self.timer.start()

    def Slider2_Pressed(self):

        self.timer.cancel()

    def Slider2_Released(self):

        pygame.mixer.music.set_pos(self.horizontalSlider_2.value() // 1000)
        self.horizontalSlider_2.setValue(pygame.mixer.music.get_pos())
        if self.horizontalSlider_2.value() // 1000 % 60 > 9:
            sec = str(self.horizontalSlider_2.value() // 1000 % 60)
        else:
            sec = f"0{self.horizontalSlider_2.value() // 1000 % 60}"
        self.label_2.setText(f"{self.horizontalSlider_2.value() // 1000 // 60}:{sec}")
        self.timer = threading.Timer(0.001, self.Time_Music)
        self.timer.start()

    def Slider2_Moved(self):

        if self.horizontalSlider_2.value() // 1000 % 60 > 9:
            sec = str(self.horizontalSlider_2.value() // 1000 % 60)
        else:
            sec = f"0{self.horizontalSlider_2.value() // 1000 % 60}"
        self.label_2.setText(f"{self.horizontalSlider_2.value() // 1000 // 60}:{sec}")

    def Slider1_Moved(self):
        QToolTip.showText(QCursor.pos(), str(int(pygame.mixer.music.get_volume() * 100)))
        if self.horizontalSlider.value() / 100 <= 0.03:

            pygame.mixer.music.set_volume(0)
            self.toolButton_4.setChecked(False)
        elif self.horizontalSlider.value() / 100 >= 0.96:
            pygame.mixer.music.set_volume(1)

        else:
            pygame.mixer.music.set_volume(self.horizontalSlider.value() / 100)
            self.toolButton_4.setChecked(True)

    def Volume_on_off(self):
        if self.flag_volume:
            pygame.mixer.music.set_volume(0)
            self.flag_volume = 0
            self.horizontalSlider.setValue(0)

        else:
            pygame.mixer.music.set_volume(1)
            self.flag_volume = 1
            self.horizontalSlider.setValue(100)

    def button_on_off(self):
        if self.toolButton_2.isChecked():
            pygame.mixer.music.unpause()


        else:

            pygame.mixer.music.pause()

    def back_button(self):
        print('hello')
        print(self.flag_all_music_or_playlist)

        if self.flag_all_music_or_playlist == 1:
            print(self.id_song_play)
            music_name = self.db.return_songs_info(self.id_song_play - 1)[5]
            print(music_name)
            pygame.mixer.music.load(music_name)
            self.paths = db.return_music_path(self.id_song_play)

            pygame.mixer.music.play(0)
            self.id_song_play -= 1

            self.name_music = path.splitext(os.path.basename(music_name))[0]
            song = MP3(music_name)
            self.label.setText(self.name_music)
            self.label_2.setText(str(int(song.info.length)))
            print(str(int(song.info.length)))
            self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
        if self.flag_all_music_or_playlist == 2:
            print(self.id_song_play)
            music_name = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[
                                                       self.db.return_all_songs_info_in_playlist().index(
                                                           self.id_song_play) - 1])[5]
            print(music_name)
            pygame.mixer.music.load(music_name)
            self.paths = db.return_music_path(self.id_song_play)

            pygame.mixer.music.play(0)
            self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[
                                                              self.db.return_all_songs_info_in_playlist().index(
                                                                  self.id_song_play) - 1])[0]

            self.name_music = path.splitext(os.path.basename(music_name))[0]
            song = MP3(music_name)
            self.label.setText(self.name_music)
            self.label_2.setText(str(int(song.info.length)))
            print(str(int(song.info.length)))
            self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))

    def next_button(self):
        print('hello')
        print(self.flag_all_music_or_playlist)

        if self.flag_all_music_or_playlist == 1:
            print(self.id_song_play)
            music_name = self.db.return_songs_info(self.id_song_play + 1)[5]
            print(music_name)
            pygame.mixer.music.load(music_name)
            self.paths = db.return_music_path(self.id_song_play)

            pygame.mixer.music.play(0)
            self.id_song_play += 1

            self.name_music = path.splitext(os.path.basename(music_name))[0]
            song = MP3(music_name)
            self.label.setText(self.name_music)
            self.label_2.setText(str(int(song.info.length)))
            print(str(int(song.info.length)))
            self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
        if self.flag_all_music_or_playlist == 2:
            print(self.id_song_play)
            try:
                music_name = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[
                                                           self.db.return_all_songs_info_in_playlist().index(
                                                               self.id_song_play) + 1])[5]
                print(music_name)
                pygame.mixer.music.load(music_name)
                self.paths = db.return_music_path(self.id_song_play)

                pygame.mixer.music.play(0)
                self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[
                                                                  self.db.return_all_songs_info_in_playlist().index(
                                                                      self.id_song_play) + 1])[0]

                self.name_music = path.splitext(os.path.basename(music_name))[0]
                song = MP3(music_name)
                self.label.setText(self.name_music)
                self.label_2.setText(str(int(song.info.length)))
                print(str(int(song.info.length)))
                self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
            except:
                music_name = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[0])[5]
                print(music_name)
                pygame.mixer.music.load(music_name)
                self.paths = db.return_music_path(self.id_song_play)

                pygame.mixer.music.play(0)
                self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[0])[0]

                self.name_music = path.splitext(os.path.basename(music_name))[0]
                song = MP3(music_name)
                self.label.setText(self.name_music)
                self.label_2.setText(str(int(song.info.length)))
                print(str(int(song.info.length)))
                self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))

    def row_tableview_doubleClicked(self):
        self.paths = None
        index = self.tableView.currentIndex()
        row = index.row()
        music_name = index.sibling(row, 5).data()

        pygame.mixer.music.load(music_name)

        pygame.mixer.music.play(0)
        self.id_song_play = index.sibling(row, 0).data()
        self.name_music = path.splitext(os.path.basename(music_name))[0]
        song = MP3(music_name)
        self.label.setText(self.name_music)
        self.label_2.setText(str(int(song.info.length)))
        print(str(int(song.info.length)))
        self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
        self.flag_all_music_or_playlist = 1
        self.toolButton_2.setChecked(True)

    def add_playlist_to_db(self):
        dial = AddPlayLists()

        dial.exec_()
        if dial.lineEdit.text() is not None and dial.lineEdit.text().replace(' ', '') != "":
            db.add_playlist(dial.lineEdit.text())
            self.model2.setTable('Playlists')
            self.model2.setEditStrategy(QSqlTableModel.OnManualSubmit)
            self.model2.select()
            self.tableView_2.setModel(self.model2)
            self.tableView_2.setColumnHidden(0, True)
            self.tableView_2.horizontalHeader().setSectionResizeMode(1)
            self.tableView_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tableView_2.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tableView_2.show()

    def row_tableview_2_doubleClicked(self):
        index = self.tableView_2.currentIndex()
        row = index.row()
        id_playlist = index.sibling(row, 0).data()
        print(id_playlist)
        songs_id = db.return_songsID(id_playlist)
        db.delete_table_result_request()
        for i in range(len(songs_id)):
            songs_info = db.return_songs_info(songs_id[i])
            print(songs_info)

            db.output_music(songs_info[0], songs_info[1], songs_info[2], songs_info[3], songs_info[4], songs_info[5])
        self.model3.setTable('ResultRequest')
        self.model3.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model3.select()
        self.tableView_3.setModel(self.model3)
        self.tableView_3.setColumnHidden(0, True)
        self.tableView_3.setColumnHidden(5, True)
        self.tableView_3.horizontalHeader().setSectionResizeMode(1)
        self.tableView_3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView_3.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_3.show()

    def context_menu_music(self, pos):
        menu1 = QMenu(self)
        add_music_to_playlist = QMenu('Add music to playlist...')

        menu1.addMenu(add_music_to_playlist)
        # menu1.addAction("Play")
        # menu1.addAction("Pause")
        for playlists in db.return_playlists():
            add_music_to_playlist.addAction(playlists)
        menu1.triggered.connect(self.actionClicked)

        menu1.exec_(self.tableView.viewport().mapToGlobal(pos))

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def actionClicked(self, action):
        id_playlist = db.get_id(action.text())[0]

        index = self.tableView.currentIndex()
        row = index.row()
        id_song = index.sibling(row, 0).data()

        db.input_id(id_song, id_playlist)
        songs_id = db.return_songsID(id_playlist)
        db.delete_table_result_request()
        for i in range(len(songs_id)):
            songs_info = db.return_songs_info(songs_id[i])
            print(songs_info)

            db.output_music(songs_info[0], songs_info[1], songs_info[2], songs_info[3], songs_info[4], songs_info[5])
        self.model3.setTable('ResultRequest')
        self.model3.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model3.select()
        self.tableView_3.setModel(self.model3)
        self.tableView_3.setColumnHidden(0, True)
        self.tableView_3.setColumnHidden(5, True)
        self.tableView_3.horizontalHeader().setSectionResizeMode(1)
        self.tableView_3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView_3.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_3.show()

    def row_tableview3_doubleClicked(self):
        index = self.tableView_3.currentIndex()
        row = index.row()
        music_name = index.sibling(row, 5).data()
        self.id_song_play = index.sibling(row, 0).data()
        print(self.id_song_play)
        pygame.mixer.music.load(music_name)
        self.paths = db.return_music_path(self.id_song_play)

        pygame.mixer.music.play(0)
        self.toolButton_2.setChecked(True)
        self.name_music = path.splitext(os.path.basename(music_name))[0]
        song = MP3(music_name)
        self.label.setText(self.name_music)
        self.label_2.setText(str(int(song.info.length)))
        print(str(int(song.info.length)))
        self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
        self.flag_all_music_or_playlist = 2
        # self.t = threading.Thread(self.wait_music())
        # self.t.start()

    # def wait_music(self):

    # n_music = 0
    # while pygame.mixer.music.get_busy():
    # sleep(1)
    # try:
    # self.paths[n_music]
    # pygame.mixer.music.play(0)
    # self.name_music = path.splitext(os.path.basename(self.paths[n_music]))[0]
    # song = MP3(self.paths[n_music])
    # self.label.setText(self.name_music)
    # self.label_2.setText(str(int(song.info.length)))
    # print(str(int(song.info.length)))
    # self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))

    # except:
    # pass
