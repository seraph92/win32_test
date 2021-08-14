import sys
from dbm import HistoryMgr
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QDataWidgetMapper,
    QDesktopWidget,
    QHeaderView,
    QLineEdit,
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

class LogsModel(list):

    def __init__(self, l=[]):
        super().__init__()

        #self.PAGE_SIZE = 20
        self.PAGE_SIZE = 15
        self.current_page = 1

        self.item_data = {}
        self.item_data["current_page"] = 1

        self.model = QStandardItemModel()
        self.model.setColumnCount(7)
        self.aggregation_model = QStandardItemModel()
        self.query_page()

        '''
        mgr = HistoryMgr()
        self.total_page = mgr.query_total_page(self.PAGE_SIZE)
        self.item_data["total_page"] = self.total_page

        #print(f"self.item_data=[{self.item_data}]")
        #print(f"total_page = [{self.item_data['total_page']}]")

        sql = f"SELECT dtm, name, temper, dtm2, reg_dtm, send_dtm \n"
        sql += f"FROM inout_history \n"
        sql += f"WHERE \n"
        sql += f"name like '%%'"
        sql += f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}"

        self.data = mgr.query(sql)

        print(f"data = [{self.data}]")

        self.model = QStandardItemModel()
        self.model.setColumnCount(7)
        self.aggregation_model = QStandardItemModel()

        self.applyModel()
        '''

    def query_page(self):

        mgr = HistoryMgr()
        self.total_page = mgr.query_total_page(self.PAGE_SIZE)
        self.item_data['current_page'] = self.current_page
        self.item_data["total_page"] = self.total_page

        sql = f"SELECT dtm, name, temper, dtm2, reg_dtm, send_dtm \n"
        sql += f"FROM inout_history \n"
        sql += f"WHERE \n"
        sql += f"name like '%%'\n"
        sql += f"ORDER BY dtm desc\n"
        sql += f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}"

        print(f"sql = [{sql}]")

        self.data = mgr.query(sql)

        print(f"data = [{self.data}]")

        #self.model = QStandardItemModel()
        #self.aggregation_model = QStandardItemModel()
        self.model.clear()
        self.model.setColumnCount(7)
        self.aggregation_model.clear()

        self.applyModel()


    def before_page(self):
        self.current_page -=1
        if self.current_page < 1:
            self.current_page = 1

        print(f"before current_page=[{self.current_page}]")
        #self.model.clear()
        #self.aggregation_model.clear()
        self.query_page()

    def next_page(self):
        self.current_page +=1
        if self.current_page > self.total_page:
            self.current_page = self.total_page

        print(f"next current_page=[{self.current_page}]")
        #self.model.clear()
        #self.aggregation_model.clear()
        self.query_page()

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
        self.aggregation_model.clear()
        self.applyModel()

        return temp

    def applyModel(self):

        print(f"Page: {self.item_data['current_page']} / {self.item_data['total_page']}")

        self.aggregation_model.appendRow(
            [
                #QStandardItem(f"{self.item_data['current_page']} / {self.item_data['total_page']}"),
                QStandardItem(f"{self.current_page} / {self.item_data['total_page']}"),
            ]
        )

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

class LogViewModel:
    def __init__(self, view, model):
        self.view = view["table_view"]
        self.item_view = view["item_view"]
        self.view = view["table_view"]

        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(model.aggregation_model)

        self.model = model
        self.dataInit()

        # event 할당
        self.view.clicked.connect(self.removeConfirm)
        self.view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        view["before_button"].clicked.connect(self.before_page)
        view["before_button2"].clicked.connect(self.before_page)
        view["next_button"].clicked.connect(self.next_page)
        view["next_button2"].clicked.connect(self.next_page)

        #self.view
        # self.model.onDataChange.connect(self.adjustColumnSize)

        # self.view.resizeColumnsToContents()
        # self.view.setColumnWidth(2, 50)

    def dataInit(self):
        self.view.setModel(self.model.model)
        self.mapper.addMapping(self.item_view, 0)
        self.mapper.toFirst()

    def before_page(self):
        self.model.before_page()
        self.mapper.toFirst()

    def next_page(self):
        self.model.next_page()
        self.mapper.toFirst()

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

        self.views = {}
        self.views["table_view"] = self.logTableView
        self.views["item_view"] = self.pageEdit
        self.views["before_button"] = self.beforeBtn
        self.views["before_button2"] = self.beforeBtn2
        self.views["next_button"] = self.nextBtn
        self.views["next_button2"] = self.nextBtn2

        self.logsModel = LogsModel()
        #self.logViewModel = LogViewModel(self.logTableView, self.logsModel)
        self.logViewModel = LogViewModel(self.views, self.logsModel)

        #QDataWidgetMapper

        self.adjustColumnSize()

        # self.setGeometry(300, 300, 1280, 768)
        self.setGeometry(300, 300, 1024, 768)
        self.center()
        self.show()

        # edit = QLineEdit()
        # edit.

    @pyqtSlot()
    def adjustColumnSize(self):
        header = self.logTableView.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        # self.logTableView.setColumnWidth(5, 50)
        header.setSectionResizeMode(header.count() - 1, QtWidgets.QHeaderView.Stretch)

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
