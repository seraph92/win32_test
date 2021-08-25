import ctypes
from PyQt5.QtCore import QObject, pyqtSignal
import six
import win32gui
import win32con

import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

#from pywinauto.application import Application

# import pywinauto
import time
import re

import sqlite3

from dbm import HistoryMgr
from BKLOG import *

GLOBAL_WIN = "AGENT"
#GLOBAL_WIN = "EDIT"

class WindowsObject:
    def __init__(self, r_text=None):
        self.win_objs = []
        self.pattern = re.compile(r_text)
        win32gui.EnumWindows(self.__EnumWindowsHandler, None)
        if len(self.win_objs) < 1:
            raise ValueError("Windows Object를 발견하지 못하였습니다.")
        self.obj = self.win_objs[0]

    def getFirstObj(self):
        if len(self.win_objs) < 1:
            return None
        else:
            return self.win_objs[0]

    def __EnumWindowsHandler(self, hwnd, find_text):
        wintext = win32gui.GetWindowText(hwnd)
        if self.pattern.match(wintext):
            obj = {}
            obj["handle"] = hwnd
            obj["text"] = wintext
            self.win_objs.append(obj)

class ChildObject:
    def __init__(self, parent_hwnd=None, match_class=None):
        self.parent_hwnd = parent_hwnd
        self.match_class = match_class
        self.pattern = re.compile(self.match_class)
        self.win_objs = []
        win32gui.EnumChildWindows(parent_hwnd, self.__EnumChildWindowsHandler, None)
        if len(self.win_objs) < 1:
            raise ValueError("Windows Object를 발견하지 못하였습니다.")
        self.obj = self.win_objs[0]

    def getFirstObj(self):
        if len(self.win_objs) < 1:
            return None
        else:
            return self.win_objs[0]

    def __EnumChildWindowsHandler(self, hwnd, extra):
        ctrl_id = win32gui.GetDlgCtrlID(hwnd)
        win_text = win32gui.GetWindowText(hwnd)
        wnd_clas = win32gui.GetClassName(hwnd)

        if self.match_class:
            if self.pattern.match(wnd_clas):
                obj = {}
                obj["handle"] = hwnd
                obj["control_id"] = ctrl_id
                obj["class_name"] = wnd_clas
                obj["text"] = win_text
                self.win_objs.append(obj)

    def line_count(self):
        control_hwnd = self.obj['handle']
        linecnt = win32gui.SendMessage(control_hwnd, win32con.EM_GETLINECOUNT, 0, 0)
        return linecnt

    def line_length(self, line_index):
        control_hwnd = self.obj['handle']
        char_index = win32gui.SendMessage(control_hwnd, win32con.EM_LINEINDEX, line_index, 0)
        line_length = win32gui.SendMessage(control_hwnd, win32con.EM_LINELENGTH, char_index, 0)
        return line_length

    def get_line(self, line_index):
        control_hwnd = self.obj['handle']
        text_len = self.line_length(line_index)
        # create a buffer and set the length at the start of the buffer
        text = ctypes.create_unicode_buffer(text_len+3)
        text[0] = six.unichr(text_len)

        result = win32gui.SendMessage(control_hwnd, win32con.EM_GETLINE, line_index, text)
        return text.value

class LogCaptureWin32Worker(QObject):
    started = pyqtSignal()
    running = pyqtSignal()
    finished = pyqtSignal()
    inserted = pyqtSignal(str)
    dupped = pyqtSignal(str, str)
    in_processing = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.loop_flag = True

        try:
            if GLOBAL_WIN == "AGENT":
                # self.w = WindowsObject("KRC-EC100 에이전트 v1.2.5.0 학원번호 : test - [  ]")
                self.w = WindowsObject(
                    r"KRC-EC100 에이전트 v[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ 학원번호 : .* - \[.*\]"
                )
            else:
                self.w = WindowsObject(r"sample.txt - Windows 메모장")

            DEBUG(f"w={self.w.win_objs}")
            DEBUG(
                "w.handle,text=[%08X][%s]" % (self.w.obj["handle"], self.w.obj["text"])
            )

            self.hwnd = self.w.obj["handle"]
            if GLOBAL_WIN == "AGENT":
                self.logwin = ChildObject(self.hwnd, CONFIG["class_name"])
            else:
                self.logwin = ChildObject(self.hwnd, r"Edit")

            """
            self.hwnd = self.w.obj["handle"]
            self.app = Application(backend="win32").connect(handle=self.hwnd)

            self.dig = self.app.window(handle=self.hwnd)
            # dig.print_control_identifiers()

            if GLOBAL_WIN == "AGENT":
                self.logwin = self.dig.child_window(
                    #class_name="WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1"
                    #class_name="WindowsForms10.RichEdit20W."
                    class_name=CONFIG["class_name"]
                )
            else:
                self.logwin = self.dig.child_window(class_name="Edit")
            """

        except ValueError as ve:
            self.loop_flag = False
            ERROR(f"Log Capture 생성 오류 [{ve}]")

    def stop(self):
        self.loop_flag = False

    def run(self):
        self.running.emit()
        processing_pattern = re.compile(
            r"\[(?P<dtm>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] 출입 확인 \(이름: (?P<name>.*), 체온: (?P<temper>[0-9.]{3,5}) 출입시간 : (?P<dtm2>.{19})\)"
        )

        if self.loop_flag:
            edit_control = self.logwin

        while self.loop_flag:
            line_cnt = edit_control.line_count()
            INFO(f"line_cnt:[{line_cnt}]")

            for i in range(0, line_cnt):
                line = edit_control.get_line(i)
                self.log_processing(processing_pattern, line)
            DEBUG("")
            self.in_processing.emit(line_cnt)
            time.sleep(3)

        self.finished.emit()

    def log_processing(self, compiled_pattern, strLog):
        history_mgr = HistoryMgr()
        DEBUG(f"strLog=[{strLog}]")
        # 외부로 이동
        # p = re.compile(r"\[(?P<dtm>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] 출입 확인 \(이름: (?P<name>.*), 체온: (?P<temper>[0-9.]{5}) 출입시간 : (?P<dtm2>.{19})\)")
        p = compiled_pattern
        m = p.match(strLog)

        try:
            DEBUG(f"m.group(dtm)    = [{m.group('dtm')}]")
            DEBUG(f"m.group(name)   = [{m.group('name')}]")
            DEBUG(f"m.group(temper) = [{m.group('temper')}]")
            DEBUG(f"m.group(dtm2)   = [{m.group('dtm2')}]")
        except AttributeError as ae:
            # 파싱 오류
            DEBUG(f"파싱 오류 무시 DB처리 하지 않음 [{ae}]")
            return

        # DB처리 (Cache 검증 및 insert)
        # 등록하려는 정보의 앞뒤 1기간 가량안에 동일 사용자의 로그가 있다면 등록하지 않고 무시
        sql = f"SELECT count(*) cnt \n"
        sql += f"FROM inout_history a \n"
        sql += f"WHERE \n"
        sql += f"name = '{m.group('name')}' \n"
        sql += f"and datetime(a.dtm) BETWEEN datetime('{m.group('dtm')}', '-1 hours') and datetime('{m.group('dtm')}', '+1 hours') \n"

        datas = history_mgr.query(sql)

        dup_cnt = datas[0]["cnt"]

        if dup_cnt:
            DEBUG(f"sql = [{sql}]")
            DEBUG(f"datas = [{datas}]")
            DEBUG(f"dup_cnt = [{dup_cnt}][{type(dup_cnt)}]")

        if not dup_cnt:
            try:
                history_mgr.execute_param(
                    history_mgr.INSERT_HISTORY,
                    (
                        m.group("dtm"),
                        m.group("name"),
                        m.group("temper"),
                        m.group("dtm2"),
                    ),
                )
            except sqlite3.IntegrityError as si:
                # Insert 무결성은 무시
                self.dupped.emit(strLog, str(si))
                history_mgr.rollback()
                DEBUG(f"INSERT 무결성은 무시 [{si}]")
            else:
                history_mgr.commit()
                self.inserted.emit(strLog)
                INFO(f"로그등록:[{strLog}]")


def uac_require():
    asadmin = "asadmin"
    try:
        if sys.argv[-1] != asadmin:
            script = os.path.abspath(sys.argv[0])
            params = " ".join([script] + sys.argv[1:] + [asadmin])
            shell.ShellExecuteEx(
                lpVerb="runas", lpFile=sys.executable, lpParameters=params
            )
            sys.exit()
        return True
    except:
        return False


if __name__ == "__main__":
    import win32com.shell.shell as shell
    import os, sys

    if uac_require():
        INFO("continue")
    else:
        ERROR("error message")
    logCapture = LogCaptureWin32Worker()
    logCapture.run()
    # log_capture_main()
