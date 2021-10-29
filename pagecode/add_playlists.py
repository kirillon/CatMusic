from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt


class AddPlayLists(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("./Pages/add_playlist.ui", self)
        self.pushButton.clicked.connect(self.clicked_save)
        self.pushButton_2.clicked.connect(self.clicked_close)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint);

    def return_lineEdit(self):
        line = str(self.lineEdit.text())
        return line
    def clicked_save(self):

        self.close()
        return str(self.lineEdit.text())

    def clicked_close(self):
        self.close()


