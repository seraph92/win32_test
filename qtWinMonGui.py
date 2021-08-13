import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtCore
from PyQt5 import uic

ui_form = uic.loadUiType("ui/auto_log_program.ui")[0]


class LogViewModel(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = LogViewModel()
    myWindow.setWindowTitle("Log Monitor")
    myWindow.show()
    app.exec_()
