import sys

from PyQt5.QtWidgets import QApplication

from pagecode.mainpage import MainPage
from Pages.mainpage import db


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainPage()
    # создание таблиц
    db.create_table_music()
    db.create_table_playlists()
    db.create_table_playlists_songs()
    db.create_table_result_request()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
