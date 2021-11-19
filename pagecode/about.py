from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt


class About(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("./Pages/about.ui", self)
        self.pushButton.clicked.connect(self.close)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)  # фиксированный размер окна
        self.label_5.setPixmap(QIcon("./img/channels4_profile.jpg").pixmap(64, 64))  # добавление логотипа
