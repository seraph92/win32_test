from Config import CONFIG
import re
import sys
import win32gui
import win32api
import win32con
import ctypes
import win32clipboard
import six
from typing import Pattern


class WindowsObject:
    def __init__(self, r_text=None):
        self.win_objs: list = []
        self.pattern: Pattern = re.compile(r_text)
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
            obj: dict = {}
            obj["handle"] = hwnd
            obj["text"] = wintext
            self.win_objs.append(obj)

class ChildObject:
    def __init__(self, parent_hwnd=None, match_class=None):
        self.parent_hwnd = parent_hwnd
        self.match_class = match_class
        self.pattern: Pattern = re.compile(self.match_class)
        self.win_objs: list = []
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
 
def getTextEditByClip(hwnd):
    # 원본 클립보드 값 저장하기
    try:
        win32clipboard.OpenClipboard()
        save_data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
    except:
        print("원복을 위한 클립보드 정보를 저장하려고 했으나 괜찮다.")

    retval = win32gui.SendMessage(hwnd, win32con.EM_SETSEL, 0, length)
    print(f"retval  =[{retval}]")

    retval = win32gui.SendMessage(hwnd, win32con.EM_GETLINE, 0, buf)
    print(f"retval  =[{retval}]")
    print(f"buf  =[{buf}]")

    retval = win32gui.SendMessage(hwnd, win32con.WM_COPY, 0, 0)
    print(f"retval  =[{retval}]")

    win32clipboard.OpenClipboard()
    # data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    data = win32clipboard.GetClipboardData()
    print(f"data  =[{data}]")
    win32clipboard.EmptyClipboard()
    win32clipboard.CloseClipboard()

    retval = win32gui.SendMessage(hwnd, win32con.EM_SETSEL, length, length)
    print(f"retval  =[{retval}]")

    ## 기존 클립보드 값 복원하기
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(save_data)
    win32clipboard.CloseClipboard()


if __name__ == "__main__":
    # win32gui.EnumWindows(EnumWindowsHandler, None)
    # w = WindowsObject("KRC-EC100")
    #w = WindowsObject("워드패드")

    w = WindowsObject(
        r"KRC-EC100 에이전트 v[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ 학원번호 : .* - \[.*\]"
    )

    print(f"w={w.win_objs}")
    print("w.handle,text=[%08X][%s]" % (w.obj["handle"], w.obj["text"]))

    parent = w.obj["handle"]

    class_name=CONFIG["class_name"]

    # children = ChildObject(parent, 'WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1')
    children = ChildObject(parent, class_name)
    print(f"children={children.win_objs}")

    for child in children.win_objs:
        hwnd = child["handle"]
        ctrl_id = win32gui.GetDlgCtrlID(hwnd)
        wnd_clas = win32gui.GetClassName(hwnd)
        wnd_text = win32gui.GetWindowText(hwnd)

        print("%08X(%d) %6d\t%s\t%s" % (hwnd, hwnd, ctrl_id, wnd_clas, wnd_text))

    # class: WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1
    # class: RICHEDIT50W

    control_hwnd = children.obj['handle']
    print("control_hwnd=[%d]" % (control_hwnd))
    print("control_hwnd=[%08X]" % (control_hwnd))
    # text = win32gui.GetWindowText(3086804)
    # print(f"text       =[{text}]")

    line_cnt = children.line_count()
    print(f"children.line_count = [{line_cnt}]")

    #text = children.get_line(line_cnt - 1)
    #print(f"text = [{text}]")

    for i in range(0, line_cnt):
        text = children.get_line(i)
        print(f"text[{i}] = [{text}]")

    """
    GetTextRange and get the range by using GetTextLength
    EM_GETTEXTEX
    GetWindowText
    GetDlgItemText
    WM_GETETXT
    """
    #############################################################################
    #############################################################################
    # WM_GETTEXTLENGTH
    # bufLen = win32gui.SendMessage(control_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
    # print(f"bufLen = [{bufLen}]")
    # buf = " " * bufLen

    # linecnt = win32gui.SendMessage(control_hwnd, win32con.EM_GETLINECOUNT, 0, buf)
    # print(f"linecnt  =[{linecnt}]")
    # #print(f"buf  =[{buf}]")
    # line_index = linecnt - 1
    # char_index = win32gui.SendMessage(control_hwnd, win32con.EM_LINEINDEX, line_index, 0)
    # print(f"line_index  =[{line_index}]")
    # print(f"type(line_index)  =[{type(line_index)}]")
    # print(f"char_index  =[{char_index}]")

    # line_length = win32gui.SendMessage(control_hwnd, win32con.EM_LINELENGTH, char_index, 0)
    # print(f"line_length  =[{line_length}]")

    # text = ctypes.create_unicode_buffer(line_length + 3)
    # text[0] = six.unichr(line_length)

    # textline = " " * line_length

    # # retrieve the line itself
    # #result = win32gui.SendMessage(control_hwnd, win32con.EM_GETLINE, line_index, ctypes.byref(text))
    # result = win32gui.SendMessage(control_hwnd, win32con.EM_GETLINE, line_index, text)
    # #result = win32gui.SendMessage(control_hwnd, win32con.EM_GETLINE, line_index, textline)
    # print(f"result  =[{result}]")
    # print(f"textline  =[{textline}]")
    # print(f"text.value  =[{text.value}]")
    #############################################################################
    #############################################################################

 
    # WM_GETTEXT
    # length = win32gui.SendMessage(control_hwnd, win32con.WM_GETTEXT, bufLen, buf)
    # print(f"length  =[{length}]")
    # print(f"buf  =[{buf}]")
    # result = buf[:length]
    # print(f"text  =[{result}]")


    # buf = ""
    # retval = win32gui.SendMessage(control_hwnd, win32con.EM_GETLINE, 0, buf)
    # print(f"retval  =[{retval}]")
    # print(f"buf  =[{buf}]")


    # GetWindowText
    #text = win32gui.GetWindowText(control_hwnd)
    #print(f"(GetWindowText) text = [{text}]")

    # GetDlgItemText
    #textA = win32gui.GetDlgItemText(3932736, 59648)
    #print(f"(GetDlgItemText) text = [{textA}]")

    #getTextEditByClip(control_hwnd)


    """
    #retval = SendMessage(Text1.hWnd, EM_SETSEL, ByVal CLng(0), ByVal CLng(5))
    retval = win32gui.SendMessage(control_hwnd, win32con.EM_SETSEL, 0, length)
    print(f"retval  =[{retval}]")

    retval = win32gui.SendMessage(control_hwnd, win32con.EM_GETLINE, 0, buf)
    print(f"retval  =[{retval}]")
    print(f"buf  =[{buf}]")

    retval = win32gui.SendMessage(control_hwnd, win32con.WM_COPY, 0, 0)
    print(f"retval  =[{retval}]")

    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    print(f"data  =[{data}]")
    win32clipboard.EmptyClipboard()
    win32clipboard.CloseClipboard()

    retval = win32gui.SendMessage(control_hwnd, win32con.EM_SETSEL, length, length)
    print(f"retval  =[{retval}]")

    #save_data = win32clipboard.GetClipboardData()

    #sys.sleep(1)
    """

    """
    print("***************")
    control_hwnd = win32gui.GetDlgItem(592654, 15)
    print("control_hwnd=[%d]"%(control_hwnd))
    print("control_hwnd=[%08X]"%(control_hwnd))
    text = win32gui.GetWindowText(control_hwnd)
    textA = win32gui.GetDlgItemText(592654, 15) 
    length = win32gui.GetWindowTextLength(control_hwnd)
    print(f"text length=[{length}]")
    print(f"text       =[{text}]")
    print(f"textA       =[{textA}]")


    print("control_hwnd=[%d]"%(parent))
    print("control_hwnd=[%08X]"%(parent))
    text = win32gui.GetWindowText(parent)
    print(f"win32gui.GetWindowText text       =[{text}]")

    buf = "한글이 써지나? \n 글씨는 잘써지는데 왜 못가져오지?"
    bufLen = len(buf)

    win32gui.SendMessage(control_hwnd, win32con.WM_SETTEXT, bufLen, buf)

    bufLen = win32gui.SendMessage(control_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
    print(bufLen)
    #buffer = win32gui.PyMakeBuffer(bufLen)
    buf = " " * bufLen
    length = win32gui.SendMessage(control_hwnd, win32con.WM_GETTEXT, bufLen, buf)
    print(f"buf  =[{buf}]")
    result = buf[:length]
    print(f"text  =[{result}]")

    #win32api.SendMessage(parent, win32con.WM_GETTEXT, WM_text, 10)
    #print(f"WM_GETTEXT text       =[{WM_text}]")
    #win32api.SendMessage(control_hwnd, win32con.WM_CHAR, ord('H'), 0)
    #win32api.Sleep(100)
    #win32api.SendMessage(control_hwnd, win32con.WM_CHAR, ord('i'), 0)
    #win32api.Sleep(100)
    """
