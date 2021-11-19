# -*- coding: utf-8 -*-

import datetime
import os
import threading
import time
from os import path

import mutagen
import pygame
from PyQt5 import QtSql, QtCore, QtWidgets
from PyQt5.QtCore import QPropertyAnimation, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAbstractItemView, QMenu, QToolTip, \
    QMessageBox, QAction
from mutagen.mp3 import MP3

from Pages.mainpage import Ui_MainWindow
from pagecode.about import About
from pagecode.add_playlists import AddPlayLists
from pagecode.faq import Faq


class MainPage(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.animation = QPropertyAnimation(self, b'windowOpacity')  # добавление анимации окна
        self.animation.setDuration(500)  # Продолжительность: 0.5 секунды
        self.late_n = 0

        self.do_show()  # показ анимации

        pygame.mixer.init()
        self.id_song_play = None

        self.flag_all_music_or_playlist = None
        self.horizontalSlider_2.setMinimum(0)
        self.horizontalSlider_2.setMaximum(1)
        self.horizontalSlider_2.setTickInterval(1)
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setTickInterval(1)
        self.horizontalSlider.setValue(70)
        self.flag_volume = 1
        self.timer_flag_on_off = 0
        self.timer_flag = 0
        self.name_music = None
        self.time_music()
        self.paths = None
        self.actionAdd_file.triggered.connect(self.load_file)
        self.actionAdd_Playlist.triggered.connect(self.add_playlist_to_db)
        self.actionPrevious_Track.triggered.connect(self.back_button)
        self.actionPause_Play.triggered.connect(self.pause_play)
        self.actionNext_Track.triggered.connect(self.next_button)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.about_application)
        self.actionFAQ.triggered.connect(self.faq_application)
        self.horizontalSlider_2.sliderPressed.connect(self.slider2_pressed)
        self.horizontalSlider_2.sliderReleased.connect(self.slider2_released)
        self.horizontalSlider_2.sliderMoved.connect(self.slider2_moved)
        self.horizontalSlider.sliderMoved.connect(self.slider1_moved)
        self.toolButton_2.clicked.connect(self.button_on_off)
        self.toolButton_4.clicked.connect(self.volume_on_off)
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

        self.tableView.doubleClicked.connect(self.row_tableview_double_clicked)
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
        self.tableView_2.doubleClicked.connect(self.row_tableview_2_double_clicked)
        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_3.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.context_menu_music)
        self.tableView_2.customContextMenuRequested.connect(self.context_menu_playlists_list)
        self.tableView_3.customContextMenuRequested.connect(self.context_menu_playlists_song)
        self.model2.dataChanged.connect(self.edit_close_tableview_2)
        self.model3 = QSqlTableModel()
        self.tableView_3.doubleClicked.connect(self.row_tableview3_double_clicked)

    def do_show(self):  # функция показа анимации

        self.animation.stop()
        # Диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def load_file(self):  # Загрузка аудиофайлов через диалог
        self.paths = None
        names_music = QFileDialog.getOpenFileNames(
            self, 'Take a Music', '',
            'Music (*.mp3);;Music (*.ogg);;All files (*)')[0]  # открытие диалога

        for index in names_music:

            try:
                audiofile = mutagen.File(index, easy=True)
                print(audiofile)

                if audiofile is None or audiofile.get("title") is None or audiofile.get("artist") is None:
                    if "-" in index:
                        artist, title = path.splitext(os.path.basename(index))[0].split("-", 1)
                        self.db.add_music(artists=artist, title=title,
                                          time=f"{int(MP3(index).info.length) // 60}:\
                                                {str(int(MP3(index).info.length) % 60).zfill(2)}",
                                          extension=path.splitext(os.path.basename(index))[1],
                                          path_music=index)  # добавление аудио файла в базу данных
                    else:

                        artist, title = "", path.splitext(os.path.basename(index))[0]
                        self.db.add_music(artists=artist, title=title,
                                          time=f"{int(MP3(index).info.length) // 60}:\
                                                        {str(int(MP3(index).info.length) % 60).zfill(2)}",
                                          extension=path.splitext(os.path.basename(index))[1],
                                          path_music=index)  # добавление аудио файла в базу данных
                else:
                    artist = audiofile.get("artist")
                    title = audiofile.get("title")

                    self.db.add_music(artists=artist[0], title=title[0],
                                      time=f"{int(MP3(index).info.length) // 60}:\
                                                    {str(int(MP3(index).info.length) % 60).zfill(2)}",
                                      extension=path.splitext(os.path.basename(index))[1],
                                      path_music=index)  # добавление аудио файла в базу данных
                    self.name_music = artist[0] + " - " + title[0]
            except:
                print("ERROR")
        song_info = self.db.return_songs_info(self.db.return_all_songs_info()[-1])
        print(song_info)
        if song_info[1] is None or song_info[1] == "":
            self.name_music = song_info[2]
        else:
            self.name_music = f"{song_info[1]}- {song_info[2]}"
        song = MP3(song_info[5])
        self.model1.setTable('Music')
        self.model1.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model1.select()
        self.tableView.setModel(self.model1)
        self.tableView.setColumnHidden(0, True)
        self.tableView.setColumnHidden(5, True)
        self.tableView.horizontalHeader().setSectionResizeMode(1)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.show()  # перезагрузка таблицы
        self.label.setText(self.name_music)
        self.label_2.setText(str(int(song.info.length)))

        self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
        dat_file = open('./log/playing_music_log.dat', 'a+', encoding='utf-8')
        dat_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.name_music + '\n')
        dat_file.close()  # добавление музыки в .dat файл
        self.id_song_play = self.db.return_all_songs_info()[-1]
        self.flag_all_music_or_playlist = 1
        pygame.mixer.music.load(names_music[-1])  # инициализация аудиофайла

        pygame.mixer.music.play(0)  # проигрывание аудиофайла
        self.late_n = 0
        self.toolButton_2.setChecked(True)  # смена состояния кнопки на True

    def time_music(self):
        if self.timer_flag_on_off == 0:
            self.timer = threading.Timer(0.000000001, self.time_music)  # инициализация таймера
            self.timer.start()  # Запуск таймера
            self.timer_flag_on_off = 1
        self.timer.cancel()
        if self.toolButton_2.isChecked() is True and pygame.mixer.music.get_busy() is False:
            # переход на следующую песню когда она закончилась
            time.sleep(1)
            self.next_button()
            self.late_n = 0
        if self.horizontalSlider_2.value() // 1000 % 60 > 9:
            sec = str(self.horizontalSlider_2.value() // 1000 % 60)
        else:
            sec = f"0{self.horizontalSlider_2.value() // 1000 % 60}"

        self.horizontalSlider_2.setValue(pygame.mixer.music.get_pos() + self.late_n)
        self.label_2.setText(f"{self.horizontalSlider_2.value() // 1000 // 60}:{sec}")
        self.timer.cancel()
        self.timer = threading.Timer(0.001, self.time_music)
        self.timer.start()

    def slider2_pressed(self):  # функция если слайдер нажат
        if pygame.mixer.music.get_busy():
            self.timer.cancel()

    def slider2_released(self):  # функция если слайдер отпущен

        if pygame.mixer.music.get_busy():

            pygame.mixer.music.set_pos(self.horizontalSlider_2.value() / 1000)
            self.late_n = self.horizontalSlider_2.value() - pygame.mixer.music.get_pos()

            if self.horizontalSlider_2.value() // 1000 % 60 > 9:
                sec = str(self.horizontalSlider_2.value() // 1000 % 60)
            else:
                sec = f"0{self.horizontalSlider_2.value() // 1000 % 60}"
            self.label_2.setText(f"{self.horizontalSlider_2.value() // 1000 // 60}:{sec}")
            self.timer = threading.Timer(0.001, self.time_music)
            self.timer.start()

    def slider2_moved(self):  # функция если слайдер двигают
        if self.horizontalSlider_2.value() // 1000 % 60 > 9:
            sec = str(self.horizontalSlider_2.value() // 1000 % 60)
        else:
            sec = f"0{self.horizontalSlider_2.value() // 1000 % 60}"
        self.label_2.setText(f"{self.horizontalSlider_2.value() // 1000 // 60}:{sec}")

    def slider1_moved(self):  # функция если слайдер двигают
        QToolTip.showText(QCursor.pos(), str(int(pygame.mixer.music.get_volume() * 100)))  # отображение подсказки
        if self.horizontalSlider.value() / 100 <= 0.03:

            pygame.mixer.music.set_volume(0)
            self.toolButton_4.setChecked(False)
        elif self.horizontalSlider.value() / 100 >= 0.96:
            pygame.mixer.music.set_volume(1)

        else:
            pygame.mixer.music.set_volume(self.horizontalSlider.value() / 100)  # изменение громкости
            self.toolButton_4.setChecked(True)

    def volume_on_off(self):
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
            pygame.mixer.music.unpause()  # включить аудиофайл
        else:

            pygame.mixer.music.pause()  # поставить на паузу аудиофайл

    def back_button(self):  # включить предыдущую песню
        try:
            if self.flag_all_music_or_playlist == 1:
                music_name = self.db.return_songs_info(self.db.return_all_songs_info()[
                                                           self.db.return_all_songs_info().index(
                                                               self.id_song_play) - 1])[5]
                print(music_name)
                pygame.mixer.music.load(music_name)
                self.paths = self.db.return_music_path(self.id_song_play)

                pygame.mixer.music.play(0)
                self.late_n = 0
                self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info()[
                                                                  self.db.return_all_songs_info().index(
                                                                      self.id_song_play) - 1])[0]

                self.name_music = self.db.return_songs_info(self.id_song_play)[1] + ' - ' + \
                                  self.db.return_songs_info(self.id_song_play)[2]
                song = MP3(music_name)
                self.label.setText(self.name_music)
                self.label_2.setText(str(int(song.info.length)))
                print(str(int(song.info.length)))
                self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
                dat_file = open('./log/playing_music_log.dat', 'a+', encoding='utf-8')
                dat_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.name_music + '\n')
                dat_file.close()
        except:
            pass
        if self.flag_all_music_or_playlist == 2:
            print(self.id_song_play)
            music_name = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[
                                                       self.db.return_all_songs_info_in_playlist().index(
                                                           self.id_song_play) - 1])[5]
            print(music_name)
            pygame.mixer.music.load(music_name)
            self.paths = self.db.return_music_path(self.id_song_play)

            pygame.mixer.music.play(0)
            self.late_n = 0
            self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[
                                                              self.db.return_all_songs_info_in_playlist().index(
                                                                  self.id_song_play) - 1])[0]

            self.name_music = self.db.return_songs_info(self.id_song_play)[1] + ' - ' + \
                              self.db.return_songs_info(self.id_song_play)[2]
            song = MP3(music_name)
            self.label.setText(self.name_music)
            self.label_2.setText(str(int(song.info.length)))
            print(str(int(song.info.length)))
            self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
            dat_file = open('./log/playing_music_log.dat', 'a+', encoding='utf-8')
            dat_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.name_music + '\n')
            dat_file.close()

    def next_button(self):  # включить следующую песню

        if self.flag_all_music_or_playlist == 1:

            try:

                music_name = self.db.return_songs_info(self.db.return_all_songs_info()[
                                                           self.db.return_all_songs_info().index(
                                                               self.id_song_play) + 1])[5]

                print(music_name)
                pygame.mixer.music.load(music_name)
                self.paths = self.db.return_music_path(self.id_song_play)
                self.late_n = 0
                pygame.mixer.music.play(0)
                self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info()[
                                                                  self.db.return_all_songs_info().index(
                                                                      self.id_song_play) + 1])[0]

                self.name_music = self.db.return_songs_info(self.id_song_play)[1] + ' - ' + \
                                  self.db.return_songs_info(self.id_song_play)[2]
                song = MP3(music_name)
                self.label.setText(self.name_music)
                self.label_2.setText(str(int(song.info.length)))
                print(str(int(song.info.length)))
                self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
                dat_file = open('./log/playing_music_log.dat', 'a+', encoding='utf-8')
                dat_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.name_music + '\n')
                dat_file.close()
            except:

                music_name = self.db.return_songs_info(self.db.return_all_songs_info()[0])[5]
                print(music_name)
                self.late_n = 0
                pygame.mixer.music.load(music_name)
                self.paths = self.db.return_music_path(self.id_song_play)

                pygame.mixer.music.play(0)
                self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info()[0])[0]

                self.name_music = self.db.return_songs_info(self.id_song_play)[1] + ' - ' + \
                                  self.db.return_songs_info(self.id_song_play)[2]
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
                self.paths = self.db.return_music_path(self.id_song_play)
                self.late_n = 0
                pygame.mixer.music.play(0)
                self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[
                                                                  self.db.return_all_songs_info_in_playlist().index(
                                                                      self.id_song_play) + 1])[0]

                self.name_music = self.db.return_songs_info(self.id_song_play)[1] + ' - ' + \
                                  self.db.return_songs_info(self.id_song_play)[2]
                song = MP3(music_name)
                self.label.setText(self.name_music)
                self.label_2.setText(str(int(song.info.length)))
                print(str(int(song.info.length)))
                self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
                dat_file = open('./log/playing_music_log.dat', 'a+', encoding='utf-8')
                dat_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.name_music + '\n')
                dat_file.close()
            except:
                music_name = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[0])[5]
                print(music_name)
                self.late_n = 0
                pygame.mixer.music.load(music_name)
                self.paths = self.db.return_music_path(self.id_song_play)

                pygame.mixer.music.play(0)
                self.id_song_play = self.db.return_songs_info(self.db.return_all_songs_info_in_playlist()[0])[0]

                self.name_music = self.db.return_songs_info(self.id_song_play)[1] + ' - ' + \
                                  self.db.return_songs_info(self.id_song_play)[2]
                song = MP3(music_name)
                self.label.setText(self.name_music)
                self.label_2.setText(str(int(song.info.length)))
                print(str(int(song.info.length)))
                self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
                dat_file = open('./log/playing_music_log.dat', 'a+', encoding='utf-8')
                dat_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.name_music + '\n')
                dat_file.close()

    def row_tableview_double_clicked(self):  # функция при двойном нажатии на ячейку таблицы со всеми аудиофайлами
        self.paths = None
        index = self.tableView.currentIndex()
        row = index.row()
        music_name = index.sibling(row, 5).data()

        pygame.mixer.music.load(music_name)
        self.late_n = 0
        pygame.mixer.music.play(0)
        self.id_song_play = index.sibling(row, 0).data()
        if self.db.return_songs_info(self.id_song_play)[1] is None or self.db.return_songs_info(self.id_song_play)[1] \
                == "":
            self.name_music = self.db.return_songs_info(self.id_song_play)[2]
        else:
            self.name_music = self.db.return_songs_info(self.id_song_play)[1] + ' - ' + \
                              self.db.return_songs_info(self.id_song_play)[2]
        song = MP3(music_name)
        self.label.setText(self.name_music)
        self.label_2.setText(str(int(song.info.length)))
        print(str(int(song.info.length)))
        self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
        self.flag_all_music_or_playlist = 1
        self.toolButton_2.setChecked(True)
        dat_file = open('./log/playing_music_log.dat', 'a+', encoding='utf-8')
        dat_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.name_music + '\n')
        dat_file.close()

    def add_playlist_to_db(self):  # добавить таблицу в базу данных
        dial = AddPlayLists()

        dial.exec_()
        if dial.lineEdit.text() is not None and dial.lineEdit.text().replace(' ', '') != "":
            self.db.add_playlist(dial.lineEdit.text())
            self.model2.setTable('Playlists')
            self.model2.setEditStrategy(QSqlTableModel.OnManualSubmit)
            self.model2.select()
            self.tableView_2.setModel(self.model2)
            self.tableView_2.setColumnHidden(0, True)
            self.tableView_2.horizontalHeader().setSectionResizeMode(1)
            self.tableView_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tableView_2.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tableView_2.show()

    def row_tableview_2_double_clicked(self):  # функция при двойном нажатии на ячейку таблицы с плейлистами
        index = self.tableView_2.currentIndex()
        row = index.row()
        id_playlist = index.sibling(row, 0).data()

        songs_id = self.db.return_songs_id(id_playlist)

        self.db.delete_table_result_request()
        for i in range(len(songs_id)):
            songs_info = self.db.return_songs_info(songs_id[i])
            print(songs_info)

            self.db.output_music(songs_info[0], songs_info[1], songs_info[2], songs_info[3], songs_info[4],
                                 songs_info[5])
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

    def context_menu_music(self, pos):  # создание контекстного меню
        menu1 = QMenu(self)
        add_music_to_playlist = QMenu('Add music to playlist                ')

        menu1.addMenu(add_music_to_playlist)
        play = QAction("Play now                             ")
        delete = QAction("Delete                                         Del")
        menu1.addAction(play)
        menu1.addAction(delete)

        for playlists in self.db.return_playlists():
            add_music_to_playlist.addAction(playlists)
        menu1.triggered.connect(self.action_clicked)
        play.triggered.connect(self.row_tableview_double_clicked)
        delete.triggered.connect(self.delete_music)

        menu1.exec_(self.tableView.viewport().mapToGlobal(pos))

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def action_clicked(self, action):
        try:
            id_playlist = self.db.get_id(action.text())[0]

            index = self.tableView.currentIndex()

            row = index.row()

            id_song = index.sibling(row, 0).data()
            print(id_song)
            print(self.db.duplicate_check(id_song))
            dublicate = self.db.duplicate_check(id_song)
            print(dublicate)
            if dublicate is None:
                dublicate = [0]
            print(id_playlist)
            if dublicate[0] != id_playlist:
                print("OK")
                self.db.input_id(id_song, id_playlist)

                songs_id = self.db.return_songs_id(id_playlist)
                self.db.delete_table_result_request()
                for i in range(len(songs_id)):
                    songs_info = self.db.return_songs_info(songs_id[i])

                    self.db.output_music(songs_info[0], songs_info[1], songs_info[2], songs_info[3], songs_info[4],
                                         songs_info[5])
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
            else:
                msg_box = QMessageBox()
                QMessageBox.warning(msg_box, "WARNING", "This song is already in the playlist")     # показ messagebox
        except:
            pass

    def row_tableview3_double_clicked(self):  # функция при двойном нажатии на ячейку таблицы с песнями в плейлистах
        index = self.tableView_3.currentIndex()
        row = index.row()
        music_name = index.sibling(row, 5).data()
        self.id_song_play = index.sibling(row, 0).data()
        print(self.id_song_play)
        pygame.mixer.music.load(music_name)
        self.paths = self.db.return_music_path(self.id_song_play)
        self.late_n = 0
        pygame.mixer.music.play(0)
        self.toolButton_2.setChecked(True)
        if self.db.return_songs_info(self.id_song_play)[1] is None or self.db.return_songs_info(self.id_song_play)[1] \
                == "":
            self.name_music = self.db.return_songs_info(self.id_song_play)[2]
        else:
            self.name_music = self.db.return_songs_info(self.id_song_play)[1] + ' - ' + \
                              self.db.return_songs_info(self.id_song_play)[2]
        song = MP3(music_name)
        self.label.setText(self.name_music)
        self.label_2.setText(str(int(song.info.length)))
        print(str(int(song.info.length)))
        self.horizontalSlider_2.setMaximum(int(song.info.length * 1000))
        self.flag_all_music_or_playlist = 2
        dat_file = open('./log/playing_music_log.dat', 'a+', encoding='utf-8')
        dat_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + self.name_music + '\n')
        dat_file.close()

    def closeEvent(self, event):  # переопределение closeEvent

        event.accept()
        self.timer.cancel()

    def pause_play(self):
        if self.toolButton_2.isChecked():

            pygame.mixer.music.pause()
            self.toolButton_2.setChecked(False)

        else:

            pygame.mixer.music.unpause()
            self.toolButton_2.setChecked(True)

    def keyPressEvent(self, event):  # создание горячих клавиш

        if int(event.modifiers()) == Qt.CTRL:
            if event.key() == Qt.Key_P:
                self.pause_play()
        if int(event.modifiers()) == Qt.CTRL:
            if event.key() == Qt.Key_B:
                self.back_button()
        if int(event.modifiers()) == Qt.CTRL:
            if event.key() == Qt.Key_N:
                self.next_button()
        if event.key() == Qt.Key_Delete:
            self.delete_music()

    def about_application(self):  # отображение окна about
        wid = About()
        wid.exec_()

    def delete_music(self):  # далить аудиофайл
        index = self.tableView.currentIndex()

        row = index.row()

        id_song = index.sibling(row, 0).data()
        self.db.delete_music(id_song)
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

    def context_menu_playlists_list(self, pos):  # конктекстное меню в таблице с плейлистами
        menu1 = QMenu(self)
        add_playlist = QAction('New playlist      ')
        rename = QAction("Rename")

        delete = QAction("Delete                               ")

        menu1.addAction(delete)
        menu1.addAction(rename)
        menu1.addSeparator()
        menu1.addAction(add_playlist)
        add_playlist.triggered.connect(self.add_playlist_to_db)
        delete.triggered.connect(self.delete_playlist)
        rename.triggered.connect(self.update_playlist)
        menu1.exec_(self.tableView_2.viewport().mapToGlobal(pos))

    def update_playlist(self):  # изменить название плейлиста
        index = self.tableView_2.currentIndex()
        self.tableView_2.edit(index)

    def edit_close_tableview_2(self):  # закрытие редактирования
        index = self.tableView_2.currentIndex()

        row = index.row()

        id_pl = index.sibling(row, 0).data()
        name = index.sibling(row, 1).data()
        self.db.update_name_playlist(name, id_pl)

    def delete_playlist(self):  # удалить плейлист
        index = self.tableView_2.currentIndex()

        row = index.row()
        print(row)
        if row > 0:
            row_now = row - 1
        else:
            row_now = row + 1
        id_pl = index.sibling(row, 0).data()
        id_pl_now = index.sibling(row_now, 0).data()
        print(id_pl)
        self.db.delete_playlist_music(id_pl)
        self.db.delete_playlist(id_pl)
        self.model2.setTable('Playlists')
        self.model2.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model2.select()
        self.tableView_2.setModel(self.model2)
        self.tableView_2.setColumnHidden(0, True)
        self.tableView_2.horizontalHeader().setSectionResizeMode(1)
        self.tableView_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView_2.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_2.show()

        songs_id = self.db.return_songs_id(id_pl_now)
        self.db.delete_table_result_request()
        for i in range(len(songs_id)):
            songs_info = self.db.return_songs_info(songs_id[i])
            print(songs_info)

            self.db.output_music(songs_info[0], songs_info[1], songs_info[2], songs_info[3], songs_info[4],
                                 songs_info[5])
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

    def context_menu_playlists_song(self, pos):
        menu1 = QMenu(self)

        play = QAction("Play now")
        delete = QAction("Delete            ")
        menu1.addAction(play)
        menu1.addAction(delete)
        menu1.triggered.connect(self.action_clicked)
        play.triggered.connect(self.row_tableview_double_clicked)
        delete.triggered.connect(self.delete_playlist_songs)

        menu1.exec_(self.tableView_3.viewport().mapToGlobal(pos))

    def delete_playlist_songs(self):  # удалить песню из плейлиста
        index = self.tableView_3.currentIndex()
        row = index.row()
        id_song = index.sibling(row, 0).data()
        self.db.delete_music_from_playlist(id_song)

        index = self.tableView_2.currentIndex()
        row = index.row()
        id_playlist = index.sibling(row, 0).data()
        songs_id = self.db.return_songs_id(id_playlist)
        self.db.delete_table_result_request()
        for i in range(len(songs_id)):
            songs_info = self.db.return_songs_info(songs_id[i])
            print(songs_info)
            self.db.output_music(songs_info[0], songs_info[1], songs_info[2], songs_info[3], songs_info[4],
                                 songs_info[5])
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

    def faq_application(self):  # отображение окна faq

        wid = Faq()

        wid.exec_()
