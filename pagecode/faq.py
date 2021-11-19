from PyQt5 import uic

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt


class Faq(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("./Pages/faq.ui", self)
        self.pushButton.clicked.connect(self.close)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)  # фиксированный размер окна
