import sys
from dbm import HistoryMgr
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QHeaderView,
    QMainWindow,
    QApplication,
    QMessageBox,
    QTableView,
)
from PyQt5 import QtCore
from PyQt5 import uic

# signal processing importing
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from BKLOG import *

ui_form = uic.loadUiType("ui/auto_log_program.ui")[0]

# 데이터가 변경되었을때 컬럼의 크기를 변경하기 위해 새로운 Signal 정의
# 아직 사용되지 않음
class DataChangeEventHandler(QObject):
    onDataChange = pyqtSignal()

    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view

    def run(self):
        self.onDataChange.emit()


class LogsModel(list):
    # class LogsModel(QObject):
    # onDataChange = DataChangeSignal()
    # onDataChange = pyqtSignal()

    def __init__(self, l=[]):
        super().__init__()

        sql = "SELECT dtm, name, temper, dtm2, reg_dtm, send_dtm \n"
        sql += "FROM inout_history \n"
        sql += "WHERE \n"
        sql += "name like '%%'"

        mgr = HistoryMgr()

        self.data = mgr.query(sql)

        print(f"data = [{self.data}]")

        """
        self.data = [
            {
                "dtm": "2021-08-09 18:59:53",
                "name": "이수미",
                "temper": "36.6.",
                "dtm2": "2021-08-09T18:58:06",
                "reg_dtm": "2021-08-11 18:02:39.928",
                "send_dtm": "",
            }
        ]
        """

        self.model = QStandardItemModel()

        self.applyModel()

    def remove(self, idx):
        DEBUG(f"remove index= [{idx}]")
        temp = self.data[idx]
        del self.data[idx]
        # last_idx = len(self.data) - 1
        # DEBUG(f"remove last_Index [{last_idx}]")

        # self.data[idx] = self.data[last_idx]
        # self.data[last_idx] = temp
        # self.data.pop()

        self.model.clear()
        self.applyModel()

        return temp

    def applyModel(self):
        self.model.setHorizontalHeaderLabels(
            ["출입일시", "이름", "온도", "일시2", "등록일시", "전송일자", "전송버튼"]
        )
        for data in self.data:
            self.model.appendRow(
                [
                    QStandardItem(data["dtm"]),
                    QStandardItem(data["name"]),
                    QStandardItem(data["temper"]),
                    QStandardItem(data["dtm2"]),
                    QStandardItem(data["reg_dtm"]),
                    QStandardItem(data["send_dtm"]),
                    QStandardItem(""),
                ]
            )
        # self.onDataChange.emit()
        # self.signal.run()


class LogViewModel:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.dataInit()

        # event 할당
        self.view.clicked.connect(self.removeConfirm)
        self.view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # self.model.onDataChange.connect(self.adjustColumnSize)

        # self.view.resizeColumnsToContents()
        # self.view.setColumnWidth(2, 50)

    def dataInit(self):
        self.view.setModel(self.model.model)

    def removeConfirm(self):
        data = self.view.selectedIndexes()
        idx = data[0].row()

        msg = "[%s]에 발생한 [%s]님의 출입로그를 삭제하시겠습니까?" % (
            self.model.data[idx]["dtm"],
            self.model.data[idx]["name"],
        )

        rst = QMessageBox.question(
            None, "삭제하시겠습니까?", msg, QMessageBox.Yes | QMessageBox.No
        )

        if rst == QMessageBox.Yes:
            self.model.remove(idx)


class MainWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.logsModel = LogsModel()
        self.logViewModel = LogViewModel(self.logTableView, self.logsModel)

        self.adjustColumnSize()

        self.setGeometry(300, 300, 1280, 768)
        self.center()
        self.show()

    @pyqtSlot()
    def adjustColumnSize(self):
        header = self.logTableView.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.setWindowTitle("Log Monitor")
    # myWindow.show()
    app.exec_()
