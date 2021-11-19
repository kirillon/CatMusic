from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt


class AddPlayLists(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("./Pages/add_playlist.ui", self)
        self.pushButton.clicked.connect(self.clicked_save)
        self.pushButton_2.clicked.connect(self.close)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)  # фиксированный размер окна

    def clicked_save(self):  # событие при нажатии на кнопку save
        self.close()
        return str(self.lineEdit.text())
