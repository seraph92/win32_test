from PyQt5 import QtGui
from PyQt5 import QtCore
from pandas.core.frame import DataFrame
import numpy as np
from ChannelMsgAuto import ChannelMessageSending
import os
import sys
import threading

# import win32com.shell.shell as shell

from DBM import DBMgr
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QDataWidgetMapper,
    QDesktopWidget,
    QDialog,
    QFileDialog,
    QFrame,
    QHeaderView,
    QLineEdit,
    QListView,
    QMainWindow,
    QApplication,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableView,
    QTextEdit,
)
from PyQt5 import uic

# signal processing importing
from PyQt5.QtCore import (
    QModelIndex,
    QThread,
    QTimer,
    pyqtSlot,
)

from typing import Literal
import sqlite3
import pandas as pd

from LogCapture import LogCaptureWin32Worker
from Config import CONFIG
from BKLOG import *

ui_form = uic.loadUiType("ui/auto_log_program.ui")[0]
UserDetailDialog = uic.loadUiType("ui/user_detail.ui")[0]


class MsgsModel(list):
    def __init__(self, l=[]):
        super().__init__()

        self.data: list[dict] = []
        self.model: QStandardItemModel = QStandardItemModel()

    def applyModel(self) -> None:
        self.model.clear()
        for data in self.data:
            self.model.appendRow(
                [
                    QStandardItem(f"{data['user']}({data['inout']})"),
                    QStandardItem(data["message"]),
                ]
            )

    def del_msg(self, idx: int) -> None:
        self.setRestoreReady(self.data[idx])
        del self.data[idx]
        self.applyModel()

    def deque_msg(self) -> dict:
        try:
            data = self.data[0]
            del self.data[0]
            self.applyModel()
        except IndexError as ie:
            DEBUG(f"index참조 오류: [{ie}]")
            data = None
        return data

    def add_reserve_msg(self, d: dict) -> bool:
        # [ㅌㅌㅌ] 학생의 수업이 [ 2020.09.01(수) 13시 ]에 예약 되어 있습니다. 전일 오후 6시 전까지 취소를 하셔야 합니다.
        # enter_exit: Literal["등원", "하원"] = "등원" if d["rnk"] % 2 else "하원"
        enter_exit = "예약"

        if enter_exit == "등원":
            enter_exit_msg = "도착했습니다.\n-READ101-"
        elif enter_exit == "하원":
            enter_exit_msg = "수업이 끝났습니다.(출발)\n-READ101-"
        else:
            enter_exit_msg = "출입 체크 되었습니다.\n-READ101-"

        reserve_msg = f"예약 변경 및 취소는 하루 전 오후9시까지 가능합니다.\n-READ101-"

        # 9/6(월) 7시 노아,수아 예약되어 있습니다.

        INFO(f"d['date'] = [{d['date']}], d['time'] = [{d['time']}]")
        tdate = datetime.datetime.strptime(str(d["date"]), "%Y%m%d").date()
        if len(str(d["time"])) == 8:
            ttime = datetime.datetime.strptime(str(d["time"]), "%H:%M:%S").time()
        else:
            ttime = datetime.datetime.strptime(str(d["time"]), "%H:%M").time()

        INFO(f"tdate = [{tdate}]")
        w = ["월", "화", "수", "목", "금", "토", "일"]
        kw = w[tdate.weekday()]
        date_str = f"{tdate.strftime('%Y.%m.%d')}({kw})"
        INFO(f"date_str = [{date_str}]")
        time_str = ttime.strftime("%H:%M")

        msg: dict = {
            "user": d["user"],
            "inout": enter_exit,
            "message": f"[{d['user']}]학생의 수업이 [{date_str} {time_str}]에 에약 되어 있습니다.  { reserve_msg }",
            "dtm": "",
        }

        INFO(f"msg = [{msg}]")

        # 기 발송 검증
        # if d["send_dtm"]:
        #    return False

        # 중복 검증
        # {k: v for k, v in my_dict.items() if int(v) > 2000}
        # INFO(f"data = [{self.data}]")
        # names = (data["user"] for data in self.data)
        names = (f"{data['user']}({data['inout']})" for data in self.data)
        # INFO(f"names = [{names}]")
        if f"{d['user']}({enter_exit})" in names:
            return False

        self.data.append(msg)
        # self.setReadyToSend(msg)
        self.applyModel()

        return True

    def add_msg(self, d: dict) -> bool:
        enter_exit: Literal["등원", "하원"] = "등원" if d["rnk"] % 2 else "하원"
        DEBUG(f"rank = {d['rnk']} = {enter_exit}")

        if enter_exit == "등원":
            enter_exit_msg = "도착했습니다.\n-READ101-"
        elif enter_exit == "하원":
            enter_exit_msg = "수업이 끝났습니다.(출발)\n-READ101-"
        else:
            enter_exit_msg = "출입 체크 되었습니다.\n-READ101-"

        msg: dict = {
            "user": d["name"],
            "inout": enter_exit,
            "message": f"[{d['dtm']}] {d['name']}학생 { enter_exit_msg }",
            "dtm": d["dtm"],
        }

        INFO(f"msg = [{msg}]")

        # 기 발송 검증
        # if d["send_dtm"]:
        #    return False

        # 중복 검증
        # {k: v for k, v in my_dict.items() if int(v) > 2000}
        # INFO(f"data = [{self.data}]")
        # names = (data["user"] for data in self.data)
        names = (f"{data['user']}({data['inout']})" for data in self.data)
        # INFO(f"names = [{names}]")
        if f"{d['name']}({enter_exit})" in names:
            return False

        self.data.append(msg)
        self.setReadyToSend(msg)
        self.applyModel()

        return True

    def setReadyToSend(self, msg: dict) -> None:
        dbm = DBMgr.instance()
        sql = " \n".join(
            (
                f"UPDATE inout_history",
                f"SET send_dtm = '-'",
                f"where dtm = '{msg['dtm']}'",
            )
        )

        INFO(f"sql = [{sql}]")
        with dbm as conn:
            try:
                dbm.execute(sql)
                conn.commit()
            except:
                conn.rollback()
                raise sqlite3.Error("변경실패")

    def setRestoreReady(self, msg: dict) -> None:
        dbm = DBMgr.instance()
        sql = " \n".join(
            (
                f"UPDATE inout_history",
                f"SET send_dtm = ''",
                f"where dtm = '{msg['dtm']}'",
                f"and send_dtm = '-'",
            )
        )
        INFO(f"sql = [{sql}]")
        with dbm as conn:
            try:
                dbm.execute(sql)
                conn.commit()
            except:
                conn.rollback()
                raise sqlite3.Error("변경실패")


class UserModel(list):
    # def __init__(self, l=[]):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel(1, 3)
        # self.user_name_model = QStandardItemModel()
        # self.chat_room_model = QStandardItemModel()
        # self.reg_dtm_model = QStandardItemModel()

    def query_one(self, user_name: str) -> None:
        dbm = DBMgr.instance()

        sql = " \n".join(
            (
                f"SELECT user_name, chat_room, reg_dtm",
                f"FROM user",
                f"WHERE",
                f"user_name like '{user_name}'",
                f"ORDER BY user_name",
                # f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}"
            )
        )

        INFO(f"sql = [{sql}]")
        # INFO(f"sql = [{sql}]")

        with dbm as conn:
            datas: list[dict] = dbm.query(sql)

        INFO(f"datas = [{datas}]")

        self.data = datas[0]

        DEBUG(f"data = [{self.data}]")
        # INFO(f"data = [{self.data}]")

        self.applyModel()

    def regist_user(self, user: dict) -> None:
        # user_name = self.model.item(0, 1).accessibleText()
        # chat_room = self.model.item(0, 2).accessibleText()
        user_name: str = user["user_name"]
        chat_room: str = user["chat_room"]

        dbm = DBMgr.instance()

        sql = " \n".join(
            (
                f"INSERT INTO user(user_name, chat_room, reg_dtm)",
                f"VALUES ( '{user_name}', '{chat_room}', strftime('%Y-%m-%d %H:%M:%f','now', 'localtime'))",
            )
        )

        with dbm as conn:
            try:
                dbm.execute(sql)
                conn.commit()
            except:
                conn.rollback()
                raise sqlite3.IntegrityError("등록실패")

    def update_user(self, user: dict) -> None:
        user_name: str = user["user_name"]
        chat_room: str = user["chat_room"]

        dbm = DBMgr.instance()

        sql = " \n".join(
            (
                f"UPDATE user",
                f"SET reg_dtm = strftime('%Y-%m-%d %H:%M:%f','now', 'localtime')",
                f"  , chat_room = '{chat_room}'",
                f"where user_name = '{user_name}'",
            )
        )
        INFO(f"sql = [{sql}]")

        with dbm as conn:
            try:
                dbm.execute(sql)
                conn.commit()
            except:
                conn.rollback()
                raise sqlite3.Error("변경실패")

    # data를 model에 적용
    def applyModel(self) -> None:
        self.model.clear()

        self.model.setItem(0, 0, QStandardItem(f"{self.data['user_name']}"))
        self.model.setItem(0, 1, QStandardItem(f"{self.data['chat_room']}"))
        self.model.setItem(0, 2, QStandardItem(f"{self.data['reg_dtm']}"))


class WeeklyModel(list):
    def __init__(self):
        super().__init__()

        self.head_data = {}
        self.data = {}

        self.head_model = {}  # QStandardItemModel()
        self.model = {}  # QStandardItemModel()

        week_abbr = (
            "mon",
            "tue",
            "wed",
            "thir",
            "fri",
            "sat",
        )
        for wabbr in week_abbr:
            self.head_model[wabbr] = QStandardItemModel(1, 2)
            self.model[wabbr] = QStandardItemModel()
        # self.model.setColumnCount(18)

    # 현재 Page 조회
    def query_page(self) -> None:
        # self.data = dbm.query(sql)

        self.applyModel()

    # def findRowIndex(self, key: str, find_text: str) -> int:
    #     for index, item in enumerate(self.data):
    #         if item[key] == find_text:
    #             return index
    #     return None

    # def getRows(self, idx: int) -> dict:
    #     return self.data[idx]

    # data를 model에 적용
    def applyModel(self):
        week_abbr = (
            "mon",
            "tue",
            "wed",
            "thir",
            "fri",
            "sat",
        )
        for wabbr in week_abbr:
            self.head_model[wabbr].clear()
            for i, head in enumerate(self.head_data[wabbr]):
                INFO(f"head({wabbr}) = [{head}]")
                self.head_model[wabbr].setItem(0, i, QStandardItem(str(head)))

            self.model[wabbr].clear()
            self.model[wabbr].setColumnCount(3)
            # Header Setting
            self.model[wabbr].setHorizontalHeaderLabels(["Time", "User", "send_dtm"])

            INFO(f"self.data[{wabbr}] = [{self.data[wabbr]}]")

            for idx, row in self.data[wabbr].iterrows():
                INFO(f"row = [{row}]")
                self.model[wabbr].appendRow(
                    [
                        QStandardItem(str(row["time"])),
                        QStandardItem(str(row["user"])),
                        QStandardItem(str(row["send_dtm"])),
                    ]
                )


class UsersModel(list):
    # def __init__(self, l=[]):
    def __init__(self):
        super().__init__()

        self.data: list[dict] = []

        self.model = QStandardItemModel()
        self.model.setColumnCount(3)
        self.query_page()

    # 현재 Page 조회
    def query_page(self) -> None:
        dbm = DBMgr.instance()

        sql = " \n".join(
            (
                f"SELECT user_name, chat_room, reg_dtm",
                f"FROM user",
                f"WHERE",
                f"user_name like '%%'",
                f"ORDER BY user_name",
                # f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}",
            )
        )
        DEBUG(f"sql = [{sql}]")

        with dbm as conn:
            self.data = dbm.query(sql)
            DEBUG(f"data = [{self.data}]")

        self.applyModel()

    def findRowIndex(self, key: str, find_text: str) -> int:
        for index, item in enumerate(self.data):
            if item[key] == find_text:
                return index
        return None

    def getRows(self, idx: int) -> dict:
        return self.data[idx]

    # remove Button 클릭시 호출됨 (하지만 현재 사용하지 않음)
    def remove(self, idx: int) -> dict:
        DEBUG(f"remove index= [{idx}]")
        temp = self.data[idx]
        del self.data[idx]
        self.applyModel()

        return temp

    def load_user(self, datas):
        dbm = DBMgr.instance()

        sql = " \n".join(
            (
                f"DELETE",
                f"FROM user",
            )
        )

        with dbm as conn:
            try:
                dbm.execute(sql)

                for data in datas:
                    sql = " \n".join(
                        (
                            f"INSERT INTO user(user_name, chat_room, reg_dtm)",
                            f"VALUES ( '{data['user_name']}', '{data['chat_room']}', strftime('%Y-%m-%d %H:%M:%f','now', 'localtime'))",
                        )
                    )
                    dbm.execute(sql)
                conn.commit()
            except:
                conn.rollback()
                raise sqlite3.IntegrityError("등록실패")

            self.query_page()

    # data를 model에 적용
    def applyModel(self):
        self.model.clear()
        self.model.setColumnCount(3)

        self.model.setHorizontalHeaderLabels(["이름", "채팅방", "등록일시"])
        for data in self.data:
            self.model.appendRow(
                [
                    QStandardItem(data["user_name"]),
                    QStandardItem(data["chat_room"]),
                    QStandardItem(data["reg_dtm"]),
                ]
            )


class LogsModel(list):
    # def __init__(self, l=[]):
    def __init__(self):
        super().__init__()

        now = datetime.datetime.now()
        self.today: str = now.strftime("%Y%m%d")
        # self.PAGE_SIZE = 20
        self.PAGE_SIZE = 15
        self.current_page = 1

        self.data: list[dict] = []

        self.item_data = {}
        self.item_data["current_page"] = 1

        self.model = QStandardItemModel()
        self.model.setColumnCount(7)
        self.aggregation_model = QStandardItemModel()
        self.today_model = QStandardItemModel()
        self.query_page()

    # Total Page 조회
    def query_total_page(self) -> int:
        page = self.PAGE_SIZE
        today = f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:8]}"
        dbm = DBMgr.instance()

        sql = " \n".join(
            (
                f"select count(*) / {page} + case count(*) % {page} when 0 then 0 else 1 END as total_page",
                f"from inout_history",
                f"where date(dtm) = date('{today}')",
                f"and (del_yn is NULL or del_yn = 'N')",
            )
        )

        with dbm as conn:
            rslt = dbm.query(sql)
            return rslt[0]["total_page"]

    # 현재 Page 조회
    def query_page(self) -> None:
        dbm = DBMgr.instance()

        # self.total_page = mgr.query_total_page(self.PAGE_SIZE)
        self.total_page = self.query_total_page()
        self.item_data["current_page"] = self.current_page
        self.item_data["total_page"] = self.total_page
        today = f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:8]}"
        DEBUG(f"self.today = {self.today}")
        DEBUG(f"today = {today}")
        # 20210809

        sql = " \n".join(
            (
                f"SELECT dtm, name, temper, dtm2, reg_dtm, rank() over (PARTITION BY name ORDER by dtm) as rnk, send_dtm",
                f"FROM inout_history",
                f"WHERE",
                f"name like '%%'",
                f"and date(dtm) = date('{today}')",
                f"and (del_yn is NULL or del_yn = 'N')",
                f"ORDER BY dtm desc",
                f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}",
            )
        )
        DEBUG(f"sql = [{sql}]")

        with dbm as conn:
            self.data = dbm.query(sql)
            DEBUG(f"data = [{self.data}]")

        self.applyModel()

    def findNextKey(self, key) -> str:
        dbm = DBMgr.instance()

        sql = " \n".join(
            (
                f"SELECT dtm, name",
                f"FROM inout_history",
                f"WHERE",
                f"dtm >= '{key}'",
                f"order by dtm",
                f"limit 2",
            )
        )

        DEBUG(f"sql = [{sql}]")

        with dbm as conn:
            datas = dbm.query(sql)

        if len(datas) < 2:
            return None
        else:
            return datas[1]["dtm"]

    def findRowIndex(self, key: str, find_text: str) -> int:
        for index, item in enumerate(self.data):
            if item[key] == find_text:
                return index
        return None

    def getLastRowKey(self) -> str:
        return self.data[len(self.data) - 1]["dtm"]

    # def findNotSentRowIndex(self):
    #     item_count = len(self.data)
    #     #INFO(f"item_count = [{item_count}]")
    #     for index in reversed(range(item_count)):
    #         item = self.data[index]
    #         #INFO(f"item_count = [{item['send_dtm']}]")
    #         if item["send_dtm"] == None or item["send_dtm"] == "":
    #             return index
    #     return None

    def getRows(self, idx) -> dict:
        return self.data[idx]

    # before Button 클릭시 호출됨
    def before_page(self) -> None:
        self.current_page -= 1
        if self.current_page < 1:
            self.current_page = 1

        DEBUG(f"before current_page=[{self.current_page}]")
        self.query_page()

    # next Button 클릭시 호출됨
    def next_page(self) -> None:
        self.current_page += 1
        if self.current_page > self.total_page:
            self.current_page = self.total_page

        DEBUG(f"next current_page=[{self.current_page}]")
        self.query_page()

    # remove Button 클릭시 호출됨 (하지만 현재 사용하지 않음)
    def remove(self, idx: int) -> dict:
        DEBUG(f"remove index= [{idx}]")
        temp = self.data[idx]
        del self.data[idx]

        self.applyModel()

        return temp

    def update_sent_dtm(self, user_msg):
        dbm = DBMgr.instance()

        sql = f"UPDATE inout_history\n"
        sql += f"SET send_dtm = strftime('%Y-%m-%d %H:%M:%f','now', 'localtime')\n"
        sql += f"where dtm = '{user_msg['dtm']}'\n"

        with dbm as conn:
            rslt = dbm.execute(sql)
            conn.commit()

        self.query_page()
        self.applyModel()

    # data를 model에 적용
    def applyModel(self):
        self.model.clear()
        self.model.setColumnCount(7)
        self.aggregation_model.clear()

        DEBUG(
            f"Page: {self.item_data['current_page']} / {self.item_data['total_page']}"
        )

        self.today_model.appendRow(
            [
                QStandardItem(f"{self.today}"),
            ]
        )

        self.aggregation_model.appendRow(
            [
                # QStandardItem(f"{self.item_data['current_page']} / {self.item_data['total_page']}"),
                QStandardItem(f"{self.current_page} / {self.item_data['total_page']}"),
            ]
        )

        self.model.setHorizontalHeaderLabels(
            ["출입일시", "이름", "온도", "일시2", "등록일시", "등하원", "전송일시"]
        )
        for data in self.data:
            self.model.appendRow(
                [
                    QStandardItem(data["dtm"]),
                    QStandardItem(data["name"]),
                    QStandardItem(data["temper"]),
                    QStandardItem(data["dtm2"]),
                    QStandardItem(data["reg_dtm"]),
                    QStandardItem("등원" if data["rnk"] % 2 else "하원"),
                    QStandardItem(data["send_dtm"]),
                ]
            )


class LogViewModel:
    def __init__(self, parent, views, models):
        self.parent = parent
        now = datetime.datetime.now()
        self.real_today = now.strftime("%Y%m%d")
        self.log_capture_loop = None
        self.auto_flag = False
        self.views = views

        # Log Tab
        self.view: QTableView = views["table_view"]
        self.model: LogsModel = models["log_model"]

        self.paging_mapper = QDataWidgetMapper()
        self.paging_mapper.setModel(models["log_model"].aggregation_model)

        self.today_mapper = QDataWidgetMapper()
        self.today_mapper.setModel(models["log_model"].today_model)

        self.page_edit: QLineEdit = views["page_edit"]

        # User Tab
        self.user_view: QTableView = views["user_table_view"]
        self.user_model: UsersModel = models["user_model"]

        # Weekly Tab
        # self.weekly_view: QTableView = views["weekly_table_view"]
        self.weekly_views = views["weekly_reserve"]
        self.weekly_model: WeeklyModel = models["weekly_model"]

        # Left Top
        self.msg_view: QListView = views["msg_view"]
        self.msg_model: MsgsModel = models["msg_model"]
        # Right Bottom
        self.scrap_log_edit: QTextEdit = views["scrap_log_edit"]
        # Left Bottom

        self.dataInit()

        self.view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # event 할당
        # Log View
        views["before_button"].clicked.connect(self.before_page)
        views["before_button2"].clicked.connect(self.before_page)
        views["next_button"].clicked.connect(self.next_page)
        views["next_button2"].clicked.connect(self.next_page)
        views["today_button"].clicked.connect(self.set_today)
        views["today_edit"].editingFinished.connect(self.date_change)
        views["keyword_edit"].editingFinished.connect(self.keyword_change)
        views["keyword_edit"].hide()
        views["auto_button"].clicked.connect(self.set_auto_process)
        self.view.doubleClicked.connect(self.log_view_double_click_handler)
        # self.view.doubleClicked.connect(self.add_msg)

        # User View
        views["regist_user_button"].clicked.connect(self.show_regist_dialog)
        views["regist_user_button2"].clicked.connect(self.show_regist_dialog)
        self.user_view.doubleClicked.connect(self.show_detail_dialog)
        views["save_button"].clicked.connect(self.save_user)
        views["load_button"].clicked.connect(self.load_user)

        # Weekly View
        # self.weekly_view.doubleClicked.connect(self.weekly_view_double_click_handler)
        week_abbr = (
            "mon",
            "tue",
            "wed",
            "thir",
            "fri",
            "sat",
        )
        self.weekly_mapper = {}
        for wabbr in week_abbr:
            self.weekly_mapper[wabbr] = QDataWidgetMapper()
            head_model = models["weekly_model"].head_model[wabbr]
            self.weekly_mapper[wabbr].setModel(head_model)
            thead: QLineEdit = self.weekly_views[wabbr]["date"]
            tweek: QLineEdit = self.weekly_views[wabbr]["week"]
            tview: QTableView = self.weekly_views[wabbr]["view"]
            self.weekly_mapper[wabbr].addMapping(thead, 0)
            self.weekly_mapper[wabbr].addMapping(tweek, 1)
            tview.setModel(models["weekly_model"].model[wabbr])
            tview.doubleClicked.connect(
                self.get_weekly_view_double_click_handler(wabbr)
            )

        views["save_weekly_button"].clicked.connect(self.save_weekly_plan)
        views["load_weekly_button"].clicked.connect(self.load_weekly_plan)

        # msg List
        self.msg_view.doubleClicked.connect(self.del_msg)

        ## Thread Setup
        # self.setup_log_capture_thread()
        self.setup_send_msg_thread()

        ## Auto Processing
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.auto_log_process)
        self.timer.start()

    def get_weekly_view_double_click_handler(self, wabbr):
        this = self
        # def weekly_view_double_click_handler(self, model: QModelIndex):
        def weekly_view_double_click_handler(self):
            INFO(f"double_clicked = [{wabbr}]")
            this.add_reserve_msg(wabbr)

        return weekly_view_double_click_handler

    def load_weekly_plan(self):
        # 파일 브라우저를 통해서 저장위치 결정
        fname = QFileDialog.getOpenFileName(
            self.parent, "Open file", "./", "Excel File(*.xlsx *.xls);; All File(*)"
        )
        DEBUG(f"선택파일: [{fname[0]}]")
        try:
            df = pd.read_excel(fname[0], header=None)
            INFO(f"df = [\n{df}]")
            INFO(f"df.index = [\n{df.index}]")
            INFO(f"df.columns = [\n{df.columns}]")
            INFO(f"df.iloc[0] = [\n{df.iloc[0]}]")
            week_abbr = (
                "mon",
                "tue",
                "wed",
                "thir",
                "fri",
                "sat",
            )
            for i, wabbr in enumerate(week_abbr):
                heads = []
                date = df.iloc[0, i * 3]
                heads.append(date)
                week = df.iloc[1, i * 3]
                heads.append(week)
                self.weekly_model.head_data[wabbr] = heads
                # index를 새로 부여하기 위해 vaules를 이용하여 df를 다시 만듬
                _slice = DataFrame(df.iloc[3:, i * 3 : i * 3 + 3].values)
                _slice.columns = ["time", "user", "send_dtm"]
                _slice.drop_duplicates(["time", "user"], inplace=True)
                _slice.fillna({"send_dtm": ""}, inplace=True)
                # 각 아이템에 날짜 정보를 부여하기 위해 Series를 만들어서 붙임
                date_array = np.full((len(_slice.values)), str(date))
                date_series = pd.Series(date_array, name="date")
                INFO(f"date_series({wabbr}) = [{date_series}]")
                _slice = pd.concat([_slice, date_series], axis=1)
                # _slice.fillna({'date':date}, inplace=True)
                _slice.dropna(inplace=True)
                INFO(f"_slice({wabbr}) = [{_slice}]")
                slice = _slice.sort_values(by=["time", "user"], axis=0)
                INFO(f"slice({wabbr}) = [{slice}]")
                self.weekly_model.data[wabbr] = slice

            self.weekly_model.query_page()
            self.adjust_weekly_view_column()
        except FileNotFoundError as fnfe:
            pass

    def save_weekly_plan(self):
        # 파일 브라우저를 통해서 저장위치 결정
        # xls 확장자, Default Name 적용(x)
        fname = QFileDialog.getSaveFileName(
            self.parent, "Open file", "./", "Excel File(*.xlsx *.xls);; All File(*)"
        )
        DEBUG(f"선택파일: [{fname[0]}]")
        week_abbr = (
            "mon",
            "tue",
            "wed",
            "thir",
            "fri",
            "sat",
        )

        df = pd.DataFrame()
        for i, wabbr in enumerate(week_abbr):
            df_week = pd.DataFrame()
            df_week.colunms = ["time", "user", "send_dtm"]
            date = self.weekly_model.head_data[wabbr][0]
            df_week = df_week.append(pd.Series([date, "", ""]), ignore_index=True)
            week = self.weekly_model.head_data[wabbr][1]
            df_week = df_week.append(pd.Series([week, "", ""]), ignore_index=True)
            df_week = df_week.append(
                pd.Series(["time", "user", "send_dtm"]), ignore_index=True
            )
            INFO(
                f"self.weekly_model.data[{wabbr}] = [\n{self.weekly_model.data[wabbr].iloc[0:,0:2]}\n]"
            )
            data = DataFrame(self.weekly_model.data[wabbr].iloc[0:, 0:2].values)
            INFO(f"data({wabbr}) = [\n{data}\n]")
            # df_week = df_week.append(data, ignore_index=True)
            df_week = pd.concat([df_week, data], ignore_index=True)

            # for idx, row in self.weekly_model.data[wabbr].iterrows():
            #     df.iloc[3 + idx, i*3] = row['time']
            #     df.iloc[3 + idx, i*3+1] = row['user']
            #     df.iloc[3 + idx, i*3+2] = row['send_dtm']
            INFO(f"df_week = [\n{df_week}\n]")
            df = pd.concat([df, df_week], axis=1, ignore_index=True)

        INFO(f"df = [\n{df}\n]")
        try:
            df.to_excel(fname[0], index=False, header=False)
        except ValueError as ve:
            pass
        except PermissionError as pe:
            pass

    def load_user(self):
        # 파일 브라우저를 통해서 저장위치 결정
        fname = QFileDialog.getOpenFileName(
            self.parent, "Open file", "./", "Excel File(*.xlsx *.xls);; All File(*)"
        )
        DEBUG(f"선택파일: [{fname[0]}]")
        try:
            df = pd.read_excel(fname[0])
            DEBUG(f"df = [\n{df}]")
            DEBUG(f"df.index = [\n{df.index}]")
            DEBUG(f"df.columns = [\n{df.columns}]")
            DEBUG(f"df.iloc[0] = [\n{df.iloc[0]}]")
            DEBUG(f"df.iloc[0][user_name] = [\n{df.iloc[0]['user_name']}]")
            temp = self.user_model.data
            self.user_model.data = []
            for line in df.iloc:
                self.user_model.data.append(
                    {
                        "user_name": line["user_name"],
                        "chat_room": line["chat_room"],
                        "reg_dtm": line["reg_dtm"],
                    }
                )
            del temp
            self.user_model.load_user(df.iloc)
            self.adjust_user_view_column()
        except FileNotFoundError as fnfe:
            pass

    def save_user(self):
        # 파일 브라우저를 통해서 저장위치 결정
        # xls 확장자, Default Name 적용(x)
        fname = QFileDialog.getSaveFileName(
            self.parent, "Open file", "./", "Excel File(*.xlsx *.xls);; All File(*)"
        )
        DEBUG(f"선택파일: [{fname[0]}]")
        df = pd.DataFrame(self.user_model.data)
        DEBUG(f"df = [\n{df}]")
        DEBUG(f"df.index = [\n{df.index}]")
        DEBUG(f"df.columns = [\n{df.columns}]")
        DEBUG(f"df.iloc[0] = [\n{df.iloc[0]}]")
        try:
            df.to_excel(fname[0], index=False)
        except ValueError as ve:
            pass

    def close(self, e):
        INFO(f"ViewModel Closing!")
        if hasattr(self, "worker"):
            self.worker.stop()
        if hasattr(self, "msg_worker"):
            self.msg_worker.stop()
        try:
            if hasattr(self, "thread"):
                self.thread.quit()
        except RuntimeError as re:
            ERROR(f"error = [{re}]")

        try:
            if hasattr(self, "msg_thread"):
                self.msg_thread.quit()
        except RuntimeError as re:
            ERROR(f"error = [{re}]")

        if hasattr(self, "thread"):
            self.thread.wait()
        if hasattr(self, "msg_thread"):
            self.msg_thread.wait()

    def set_auto_process(self):
        if self.real_today == self.model.today or CONFIG["RUN_MODE"] != "REAL":
            self.auto_flag = not self.auto_flag
            self.apply_auto_Btn()
        else:
            self.auto_flag = False

    def apply_auto_Btn(self):
        autoBtn: QPushButton = self.views["auto_button"]

        if self.auto_flag:
            try:
                self.auto_current_key = self.model.getLastRowKey()
                autoBtn.setText("자동 처리 중")
                autoBtn.setStyleSheet("background-color: red;")
                # index = self.model.findRowIndex("dtm", self.auto_current_key)
                # if index:
                #     self.view.selectRow(index)
                # self.add_msg(None)
            except IndexError as ie:
                self.auto_flag = False
        else:
            autoBtn.setText("자동처리")
            autoBtn.setStyleSheet("")

    def auto_log_process(self):
        now = datetime.datetime.now()
        self.real_today = now.strftime("%Y%m%d")

        if self.real_today != self.model.today and CONFIG["RUN_MODE"] == "REAL":
            self.auto_flag = False

        # 현재 페이지를 상대로 처리되지 않은 항목들에 대해 메시지를 발송한다.
        if self.auto_flag:
            DEBUG(f"self.auto_current_key = [{self.auto_current_key}]")
            index = self.model.findRowIndex("dtm", self.auto_current_key)
            DEBUG(f"index = [{index}]")
            if index != None:
                self.view.selectRow(index)
                self.add_msg(None)

            next_key = self.model.findNextKey(self.auto_current_key)
            DEBUG(f"self.next_key = [{next_key}]")

            if next_key:
                self.auto_current_key = next_key

            # index = self.model.findRowIndex("dtm", self.auto_current_key)
            # if index:
            #     self.view.selectRow(index)
            # self.add_msg(None)

    def show_detail_dialog(self):
        # 상세정보 창
        row = self.user_view.currentIndex().row()
        rows = self.user_model.getRows(row)
        DEBUG(f"rows = [{rows}]")
        dlg = UserDetailDlg(self.parent, rows["user_name"])
        dlg.accepted.connect(self.regist_dialog_accept)
        dlg.rejected.connect(self.regist_dialog_reject)
        dlg.exec()
        index = self.user_model.findRowIndex("user_name", rows["user_name"])
        if index:
            self.user_view.selectRow(index)

    def show_regist_dialog(self):
        # self.views["user_detail_dialog"].exec()
        # 신규등록 창
        dlg = UserDetailDlg(self.parent)
        dlg.accepted.connect(self.regist_dialog_accept)
        dlg.rejected.connect(self.regist_dialog_reject)
        # dlg.finished.connect(self.regist_dialog_finished)
        dlg.exec()
        # self.user_model.

    def regist_dialog_finished(self):
        DEBUG(f"다이얼로그 끝났어!!")
        self.user_model.query_page()
        self.adjust_user_view_column()

    def regist_dialog_accept(self):
        DEBUG(f"OK버튼 눌렀지?")
        self.user_model.query_page()
        # self.user_model.applyModel()
        self.adjust_user_view_column()

    def regist_dialog_reject(self):
        DEBUG(f"Cancel버튼 눌렀지?")

    def adjust_weekly_view_column(self):
        week_abbr = (
            "mon",
            "tue",
            "wed",
            "thir",
            "fri",
            "sat",
        )
        for i, wabbr in enumerate(week_abbr):
            self.weekly_mapper[wabbr].toFirst()
            header = self.weekly_views[wabbr]["view"].horizontalHeader()
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(
                header.count() - 1, QtWidgets.QHeaderView.Stretch
            )

    def adjust_user_view_column(self):
        header = self.user_view.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(header.count() - 1, QtWidgets.QHeaderView.Stretch)

    def adjust_log_view_column(self):
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(header.count() - 1, QtWidgets.QHeaderView.Stretch)

    def setup_send_msg_thread(self):
        # Log Capture Thread 설정
        self.msg_thread = QThread(self.parent)
        self.msg_worker = ChannelMessageSending()
        self.msg_worker.moveToThread(self.msg_thread)

        self.msg_thread.started.connect(self.msg_worker.run)
        self.msg_worker.running.connect(self.change_msg_running_bg)
        self.msg_worker.finished.connect(self.msg_thread.quit)
        self.msg_worker.finished.connect(self.change_msg_stop_bg)
        self.msg_worker.finished.connect(self.msg_worker.deleteLater)
        self.msg_thread.finished.connect(self.msg_thread.deleteLater)

        # Step 6: Start the thread
        self.msg_thread.start()

        # 중복 로그는 남기지 않음
        self.msg_worker.need_msg.connect(self.send_msg)
        self.msg_worker.one_processed.connect(self.log_sending)
        # self.msg_worker.inserted.connect(self.inserted_handle)

    def setup_log_capture_thread(self):
        # Log Capture Thread 설정
        self.thread = QThread()
        self.worker = LogCaptureWin32Worker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.running.connect(self.change_log_running_bg)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.change_log_stop_bg)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.reportProgress)

        # Step 6: Start the thread
        self.thread.start()

        # 중복 로그는 남기지 않음
        # self.worker.dupped.connect(self.dup_handle)
        self.worker.inserted.connect(self.inserted_handle)

    def change_log_stop_bg(self):
        edit: QTextEdit = self.views["log_edit"]
        edit.setStyleSheet("background-color: #f5d6c1;")

    def change_log_running_bg(self):
        edit: QTextEdit = self.views["log_edit"]
        edit.setStyleSheet("background-color: #bec5f7;")

    def change_msg_stop_bg(self):
        view: QListView = self.views["msg_view"]
        view.setStyleSheet("background-color: #f5d6c1;")

    def change_msg_running_bg(self):
        edit: QTextEdit = self.views["msg_view"]
        edit.setStyleSheet("background-color: #bec5f7;")

    def __del__(self):
        # self.logCapture.loop_flag = False
        DEBUG(f"LogViewModel destroyed!!")

    def log_sending(self, user_msg):
        INFO(f"{user_msg}")
        self.model.update_sent_dtm(user_msg)
        self.adjust_log_view_column()

    def send_msg(self):
        # 첫번째 데이터를 꺼내서 msg_worker로 전송
        data = self.msg_model.deque_msg()
        if data:
            self.msg_worker.user_msgs.append(data)

    def keyword_change(self):
        keyword = self.views["keyword_edit"].text()
        INFO(f"keyword changed = [{keyword}]")

    def set_today(self):
        edit: QLineEdit = self.views["today_edit"]
        edit.setText(self.real_today)
        self.date_change()

    def date_change(self):
        self.model.today = self.views["today_edit"].text()
        INFO(f"date changed = [{self.model.today}]")
        self.model.current_page = 1
        self.refresh_log_view()
        # self.model.query_total_page()
        # self.model.query_page()
        # self.paging_mapper.toFirst()
        # self.adjust_log_view_column()
        self.auto_flag = False
        self.apply_auto_Btn()

    def del_msg(self, model):
        row = self.msg_view.currentIndex().row()
        # column = self.view.currentIndex().column()
        self.msg_model.del_msg(row)

        # log view update
        self.refresh_log_view()
        # self.model.query_total_page()
        # self.model.query_page()
        # self.paging_mapper.toFirst()
        # self.adjust_log_view_column()

        DEBUG(f"delete row = [{row}]")

    def log_view_double_click_handler(self, model: QModelIndex):
        if self.real_today == self.model.today or CONFIG["RUN_MODE"] != "REAL":
            self.add_msg(model)

    def add_reserve_msg(self, week):
        row = self.weekly_views[week]["view"].currentIndex().row()
        # column = self.view.currentIndex().column()
        rows = self.weekly_model.data[week].iloc[row]
        DEBUG(f"rows = [{rows}]")

        if not rows["send_dtm"]:
            if self.msg_model.add_reserve_msg(rows):
                rows["send_dtm"] = "-"
                self.weekly_model.applyModel()
        elif rows["send_dtm"] == "-":
            msg = "메시지 발송을 시도 했지만, 처리되지 않았습니다. 다시 시도 할까요?"
            rst = QMessageBox.question(
                None, "메시지 재 발송", msg, QMessageBox.Yes | QMessageBox.No
            )
            if rst == QMessageBox.Yes:
                if self.msg_model.add_reserve_msg(rows):
                    rows["send_dtm"] = "-"
                    self.weekly_model.applyModel()

        self.adjust_weekly_view_column()

    def add_msg(self, model):
        row = self.view.currentIndex().row()
        # column = self.view.currentIndex().column()
        rows = self.model.getRows(row)
        DEBUG(f"rows = [{rows}]")

        if not rows["send_dtm"]:
            if self.msg_model.add_msg(rows):
                rows["send_dtm"] = "-"
                self.model.applyModel()
        elif rows["send_dtm"] == "-":
            if not self.auto_flag:
                msg = "메시지 발송을 시도 했지만, 처리되지 않았습니다. 다시 시도 할까요?"
                rst = QMessageBox.question(
                    None, "메시지 재 발송", msg, QMessageBox.Yes | QMessageBox.No
                )
                if rst == QMessageBox.Yes:
                    if self.msg_model.add_msg(rows):
                        rows["send_dtm"] = "-"
                        self.model.applyModel()

        self.adjust_log_view_column()

    # scrap시 dup발생시 호출되는 함수
    def dup_handle(self, strlog, error):
        # self.scrap_log_edit.append(f"[{strlog}]-[{error}]")
        self.views["log_edit"].append(f"[{strlog}]-[{error}]")
        self.views["log_edit"].verticalScrollBar().setValue(
            self.views["log_edit"].verticalScrollBar().maximum()
        )

    # scrap시 insert발생시 호출되는 함수
    def inserted_handle(self, strlog):
        self.refresh_log_view()
        self.views["log_edit"].append(f"[{strlog}]")
        self.views["log_edit"].verticalScrollBar().setValue(
            self.views["log_edit"].verticalScrollBar().maximum()
        )

    def refresh_log_view(self):
        # self.model.query_total_page()
        self.model.query_page()
        self.paging_mapper.toFirst()
        self.adjust_log_view_column()

    def dataInit(self):
        # Log Tab
        self.view.setModel(self.model.model)
        self.paging_mapper.addMapping(self.page_edit, 0)
        self.paging_mapper.toFirst()
        self.today_mapper.addMapping(self.views["today_edit"], 0)
        self.today_mapper.toFirst()
        self.adjust_log_view_column()

        # User Tab
        self.user_view.setModel(self.user_model.model)
        self.adjust_user_view_column()

        # Left Top (List)
        self.msg_view.setModel(self.msg_model.model)

    def before_page(self):
        self.model.before_page()
        self.paging_mapper.toFirst()
        self.adjust_log_view_column()
        self.auto_flag = False
        self.apply_auto_Btn()

    def next_page(self):
        self.model.next_page()
        self.paging_mapper.toFirst()
        self.adjust_log_view_column()
        self.auto_flag = False
        self.apply_auto_Btn()

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


class UserDetailDlg(QDialog, UserDetailDialog):
    """User Detail Dialog."""

    def __init__(self, parent=None, user_name=None):
        super().__init__(parent)
        self.setupUi(self)

        # self.user_name이 있고 없고에 따라, 등록과 수정을 구분
        self.user_name = user_name

        if self.user_name:
            INFO(f"사용자 정보 수정 [{self.user_name}]")
            self.setWindowTitle("사용자 정보 수정")
            # w : QLineEdit = QLineEdit()
            # w.setStyleSheet('background-color: transparent;')
            self.user_name_edit.setReadOnly(True)
            self.user_name_edit.setStyleSheet("background-color: transparent;")
            # background-color: transparent;
        else:
            self.setWindowTitle("사용자 정보 등록")

        # 작은 MVVM처럼 세팅
        self.views = {}
        self.models = {}

        # 작은 view들 세팅
        self.views["user_name_edit"] = self.user_name_edit
        self.views["chat_room_edit"] = self.chat_room_edit
        self.views["reg_dtm_edit"] = self.reg_dtm_edit
        self.views["button_box"] = self.buttonBox

        # 작은 model들 세팅
        self.models["user_model"] = UserModel()

        self.dataInit()
        # event 할당
        # self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)

        # 이지만 할게 없네

        if self.user_name:
            self.models["user_model"].query_one(self.user_name)
            self.mapper.toFirst()

            # self.name_mapper.toFirst()
            # self.chat_mapper.toFirst()
            # self.reg_dtm_mapper.toFirst()

    def accept(self) -> None:
        DEBUG(f"accept 내부에서 처리 [self.user_name]")
        if self.user_name:
            # 수정
            user = {
                "user_name": self.views["user_name_edit"].text(),
                "chat_room": self.views["chat_room_edit"].text(),
            }
            try:
                self.models["user_model"].update_user(user)
            except sqlite3.Error as e:
                ERROR(f"사용자정보 수정에 실패하였습니다. {e}]")
                QMessageBox.about(self, "정보 변경 오류", "사용자정보 수정에 실패하였습니다.")
        else:
            # 등록
            # w = QLineEdit()
            # w.text()
            user = {
                "user_name": self.views["user_name_edit"].text(),
                "chat_room": self.views["chat_room_edit"].text(),
            }
            try:
                self.models["user_model"].regist_user(user)
            except sqlite3.IntegrityError as ie:
                ERROR(f"사용자등록에 실패하였습니다. 중복이 발생하였습니다.[{ie}]")
                QMessageBox.about(self, "사용자 추가 오류", "사용자 추가하는데 실패하였습니다.(중복)")
        return super().accept()

    def reject(self) -> None:
        DEBUG(f"reject 내부에서 처리")
        return super().reject()

    def dataInit(self):
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.models["user_model"].model)

        # self.name_mapper = QDataWidgetMapper()
        # self.name_mapper.setModel(self.models["user_model"].user_name_model)
        # self.chat_mapper = QDataWidgetMapper()
        # self.chat_mapper.setModel(self.models["user_model"].chat_room_model)
        # self.reg_dtm_mapper = QDataWidgetMapper()
        # self.reg_dtm_mapper.setModel(self.models["user_model"].reg_dtm_model)

        # Log Tab
        self.mapper.addMapping(self.views["user_name_edit"], 0)
        self.mapper.addMapping(self.views["chat_room_edit"], 1)
        self.mapper.addMapping(self.views["reg_dtm_edit"], 2)
        self.mapper.toFirst()

        # self.name_mapper.addMapping(self.views["user_name_edit"], 0)
        # self.name_mapper.toFirst()
        # self.chat_mapper.addMapping(self.views["chat_room_edit"], 0)
        # self.chat_mapper.toFirst()
        # self.reg_dtm_mapper.addMapping(self.views["reg_dtm_edit"], 0)
        # self.reg_dtm_mapper.toFirst()


class MainWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.views = {}
        ## Log Tab
        self.views["table_view"] = self.logTableView
        self.views["page_edit"] = self.pageEdit
        self.views["today_edit"] = self.todayEdit
        self.views["today_button"] = self.todayBtn
        self.views["keyword_edit"] = self.keywordEdit
        self.views["before_button"] = self.beforeBtn
        self.views["before_button2"] = self.beforeBtn2
        self.views["next_button"] = self.nextBtn
        self.views["next_button2"] = self.nextBtn2
        self.views["auto_button"] = self.autoBtn

        ## User Tab
        self.views["user_table_view"] = self.userTableView
        self.views["regist_user_button"] = self.registUserBtn
        self.views["regist_user_button2"] = self.registUserBtn2
        self.views["save_button"] = self.saveBtn
        self.views["load_button"] = self.loadBtn

        ## Weekly Tab
        # self.views["weekly_table_view"] = self.weeklyTableView
        self.views["save_weekly_button"] = self.saveWeeklyBtn
        self.views["load_weekly_button"] = self.loadWeeklyBtn

        week_abbr = (
            "mon",
            "tue",
            "wed",
            "thir",
            "fri",
            "sat",
        )

        weekly_columns = {}

        for wabbr in week_abbr:
            weekly_columns[wabbr] = {
                "date": getattr(self, f"dateHeaderLineEdit_{wabbr}"),
                "week": getattr(self, f"weekHeaderLineEdit_{wabbr}"),
                "view": getattr(self, f"reserveView_{wabbr}"),
            }
            dateLineEdit: QLineEdit = weekly_columns[wabbr]["date"]
            dateLineEdit.setStyleSheet("background-color: #EBF1DE;")
            weekLineEdit: QLineEdit = weekly_columns[wabbr]["week"]
            weekLineEdit.setStyleSheet("background-color: #FDE9D9;")

        # weekly_columns = {
        #     "mon": {
        #         "date": self.dateHeaderLineEdit_mon,
        #         "week": self.weekHeaderLineEdit_mon,
        #         "view": self.reserveView_mon,
        #     },
        #     "tue": {
        #         "date": self.dateHeaderLineEdit_tue,
        #         "week": self.weekHeaderLineEdit_tue,
        #         "view": self.reserveView_tue,
        #     },
        #     "wed": {
        #         "date": self.dateHeaderLineEdit_wed,
        #         "week": self.weekHeaderLineEdit_wed,
        #         "view": self.reserveView_wed,
        #     },
        #     "thir": {
        #         "date": self.dateHeaderLineEdit_thir,
        #         "week": self.weekHeaderLineEdit_thir,
        #         "view": self.reserveView_thir,
        #     },
        #     "fri": {
        #         "date": self.dateHeaderLineEdit_fri,
        #         "week": self.weekHeaderLineEdit_fri,
        #         "view": self.reserveView_fri,
        #     },
        #     "sat": {
        #         "date": self.dateHeaderLineEdit_sat,
        #         "week": self.weekHeaderLineEdit_sat,
        #         "view": self.reserveView_sat,
        #     },
        # }

        # viewAttrs(self)

        self.views["weekly_reserve"] = weekly_columns
        INFO(f"weekly_columns = [{weekly_columns}]")
        INFO(f"self.views['weekly_reserve'] = [{self.views['weekly_reserve']}]")

        ## Left Bottom List
        self.views["scrap_log_edit"] = self.scrapLogEdit
        ## Right Bottom List
        self.views["log_edit"] = self.logEdit
        ## Left Top List
        self.views["msg_view"] = self.msgListView

        ## Dialog
        # self.views["user_detail_dialog"] = UserDetailDlg(self)

        self.models = {}
        ## table_view의 모델
        self.models["log_model"] = LogsModel()
        ## msg_view의 모델
        self.models["msg_model"] = MsgsModel()
        ## user_table_view의 모델
        self.models["user_model"] = UsersModel()
        ## weekly_table_view의 모델
        self.models["weekly_model"] = WeeklyModel()

        self.logViewModel = LogViewModel(self, self.views, self.models)

        self.adjustColumnSize()

        # self.setGeometry(300, 300, 1280, 768)
        self.setGeometry(300, 300, 1024, 768)
        self.center()
        self.show()

        frame: QFrame = self.frame_2

        self.scrollArea.setWidget(frame)
        frame.setFixedWidth(2048)
        self.resizeWeeklyFrame()
        # frame.setFixedHeight(500)

    def resizeEvent(self, resizeEvent: QtGui.QResizeEvent) -> None:
        self.frame.setFixedSize(resizeEvent.size())
        self.resizeWeeklyFrame()

    def resizeWeeklyFrame(self):
        scrollArea: QScrollArea = self.scrollArea
        weekly_frame: QFrame = self.frame_2
        margin = scrollArea.getContentsMargins()  # contentsMargins()
        DEBUG(f"margin = [{margin}]")
        rect = scrollArea.geometry()
        DEBUG(f"rect = [{rect}]")
        weekly_frame.setFixedHeight(rect.height() - (rect.y() * 2 + margin[1] * 2))

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

    def closeEvent(self, e):
        self.logViewModel.close(e)
        # self.hide()
        # self.thread.stop()


def uac_require():
    asadmin = "asadmin"
    # try:
    if sys.argv[-1] != asadmin:
        script = os.path.abspath(sys.argv[0])
        params = " ".join([script] + sys.argv[1:] + [asadmin])
        shell.ShellExecuteEx(lpVerb="runas", lpFile=sys.executable, lpParameters=params)
        sys.exit(0)
    return True
    # except:
    #    return False


def viewAttrs(obj):
    for ar in dir(obj):
        if callable(getattr(obj, ar)):
            print("Callable >> %s : %s\n\n" % (ar, getattr(obj, ar).__doc__))
        else:
            print("Property >> %s : %s\n\n" % (ar, getattr(obj, ar).__doc__))


if __name__ == "__main__":
    # if uac_require():
    #    INFO("continue")
    # else:
    #    ERROR("error message")

    # mt = MemTrace()

    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.setWindowTitle(f"Log Monitor [{CONFIG['RUN_MODE']}]")
    # myWindow.show()
    # 이벤트 큐 루프에 들어가기전 log capture thread와 channel message sending thread 가동
    INFO(f"current thread id :[{threading.get_ident()}]")
    app.exec_()

    # mt.end_print()
