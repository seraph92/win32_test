import win32gui
from pywinauto.application import Application
#import pywinauto
import time

import sqlite3

from BKLOG import *

class HistoryMgr:
    def __init__(self, dbconn):
        self.dbconn = dbconn
        self.dbconn = sqlite3.connect("data/log.db")
        self.cur = self.dbconn.cursor()

    def execute(self, exec_str):
        result=self.dbconn.execute(exec_str)
        DEBUG(f"exec result=[{result}]")
        return result

    def query(self, exec_str):
        cur=self.cur.execute(exec_str)
        DEBUG(f"query result(cur)=[{cur}]")
        rows = cur.fetchall()
        return rows

    def commit(self):
        self.dbconn.commit()

    def rollback(self):
        self.dbconn.rollback()

    def __del__(self):
        self.dbconn.close()
        DEBUG(f"db Connection Closed!!")


class WindowsObject:
    def __init__(self, text=None, parent_hwnd=None):
        self.win_objs = []
        win32gui.EnumWindows(self.__EnumWindowsHandler, text)
        if len(self.win_objs) < 1:
            raise ValueError('Windows Object를 발견하지 못하였습니다.')
        self.obj = self.win_objs[0]
 
    def getFirstObj(self):
        if len(self.win_objs) < 1:
            return None
        else:
            return self.win_objs[0]
 
    def __EnumWindowsHandler(self, hwnd, find_text):
        wintext = win32gui.GetWindowText(hwnd)
        if find_text:
            if wintext.find(find_text) != -1:
                obj = {}
                obj['handle'] = hwnd
                obj['text'] = wintext
                self.win_objs.append(obj)
        else:
            obj = {}
            obj['handle'] = hwnd
            obj['text'] = wintext
            self.win_objs.append(obj)
        #print ("%08X: %s" % (hwnd, wintext))

def monitoring(edit_control):
    loop_flag = True

    while loop_flag:
        try:
            line_cnt = edit_control.line_count()
            INFO(f"line_cnt:[{line_cnt}]")

            for i in range(0, line_cnt):
                INFO(f"Line[{i}]:[{edit_control.get_line(i)}]")
            INFO("")
            time.sleep(3)
        except:
            loop_flag=False

    return loop_flag

def main():
    w = WindowsObject("KRC-EC100 에이전트 v1.2.5.0 학원번호 : test - [  ]")

    DEBUG(f"w={w.win_objs}")
    DEBUG("w.handle,text=[%08X][%s]"%(w.obj['handle'], w.obj['text']))

    #app = Application(backend="uia").start('notepad.exe') # process 실행
    #app = Application(backend="uia").connect(handle=0x000808B4)
    #app = Application(backend="win32").start('notepad.exe') # process 실행
    #app = Application(backend="win32").start(r'C:\Program Files (x86)\드림시큐리티\KRC-EC100 에이전트\ACT Agent.exe') # process 실행
    #app = Application(backend="win32").start(r'C:\Program Files (x86)\드림시큐리티\KRC-EC100 에이전트\ACT Agent.exe') # process 실행
    #app = Application(backend="win32").connect(handle=0x000B0916)
    #app = Application().connect(title_re=".*Notepad", class_name="Notepad")
    #app = Application(backend="win32").connect(path=r"C:\Program Files (x86)\드림시큐리티\KRC-EC100 에이전트\ACT Agent.exe")
    hwnd = w.obj['handle']
    app = Application(backend="win32").connect(handle=hwnd)

    #dig = app.window(title='KRC-EC100 에이전트 v1.2.5.0 학원번호 : test - [  ]')
    dig = app.window(handle=hwnd)
    #dig.print_control_identifiers()

    # WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1
    logwin = dig.child_window(class_name="WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1")


    result = monitoring(logwin)

    #print(f"메모장내용:[{logwin.text_block()}]")
    #print(f"메모장내용:[{logwin.window_text()}]")


def uac_require():
    asadmin = 'asadmin'
    try:
        if sys.argv[-1] != asadmin:
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:] + [asadmin])
            shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
            sys.exit()
        return True
    except:
        return False

if __name__ == '__main__':
    import win32com.shell.shell as shell
    import os, sys
    if uac_require():
        INFO('continue')
    else:
        ERROR('error message')

    main()