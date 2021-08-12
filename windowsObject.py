import sys
import win32gui
import win32api
import win32con
import ctypes
import win32clipboard


class WindowsObject:
    def __init__(self, text=None, parent_hwnd=None):
        self.win_objs = []
        win32gui.EnumWindows(self.__EnumWindowsHandler, text)
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
        if find_text:
            if wintext.find(find_text) != -1:
                obj = {}
                obj["handle"] = hwnd
                obj["text"] = wintext
                self.win_objs.append(obj)
        else:
            obj = {}
            obj["handle"] = hwnd
            obj["text"] = wintext
            self.win_objs.append(obj)
        # print ("%08X: %s" % (hwnd, wintext))


class ChildObject:
    def __init__(self, parent_hwnd=None, match_class=None):
        self.parent_hwnd = parent_hwnd
        self.match_class = match_class
        self.win_objs = []
        win32gui.EnumChildWindows(parent_hwnd, self.__EnumChildWindowsHandler, None)

    def __EnumChildWindowsHandler(self, hwnd, extra):
        ctrl_id = win32gui.GetDlgCtrlID(hwnd)
        win_text = win32gui.GetWindowText(hwnd)
        wnd_clas = win32gui.GetClassName(hwnd)

        if self.match_class:
            if wnd_clas.find(self.match_class) != -1:
                obj = {}
                obj["handle"] = hwnd
                obj["control_id"] = ctrl_id
                obj["class_name"] = wnd_clas
                obj["text"] = win_text
                self.win_objs.append(obj)
        else:
            obj = {}
            obj["handle"] = hwnd
            obj["control_id"] = ctrl_id
            obj["class_name"] = wnd_clas
            obj["text"] = win_text
            self.win_objs.append(obj)


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

    w = WindowsObject("워드패드")

    print(f"w={w.win_objs}")
    print("w.handle,text=[%08X][%s]" % (w.obj["handle"], w.obj["text"]))

    parent = w.obj["handle"]
    # children = ChildObject(parent, 'WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1')
    children = ChildObject(parent, "RICHEDIT50W")
    print(f"children={children.win_objs}")

    for child in children.win_objs:
        hwnd = child["handle"]
        ctrl_id = win32gui.GetDlgCtrlID(hwnd)
        wnd_clas = win32gui.GetClassName(hwnd)
        wnd_text = win32gui.GetWindowText(hwnd)

        print("%08X(%d) %6d\t%s\t%s" % (hwnd, hwnd, ctrl_id, wnd_clas, wnd_text))

    # class: WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1
    # class: RICHEDIT50W

    control_hwnd = 3086804
    print("control_hwnd=[%d]" % (control_hwnd))
    print("control_hwnd=[%08X]" % (control_hwnd))
    # text = win32gui.GetWindowText(3086804)
    # print(f"text       =[{text}]")

    """
    GetTextRange and get the range by using GetTextLength
    EM_GETTEXTEX
    GetWindowText
    GetDlgItemText
    WM_GETETXT
    """
    # WM_GETTEXTLENGTH
    bufLen = win32gui.SendMessage(control_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
    print(f"bufLen = [{bufLen}]")
    buf = " " * bufLen

    # WM_GETTEXT
    length = win32gui.SendMessage(control_hwnd, win32con.WM_GETTEXT, bufLen, buf)
    print(f"buf  =[{buf}]")
    result = buf[:length]
    print(f"text  =[{result}]")

    # GetWindowText
    text = win32gui.GetWindowText(control_hwnd)
    print(f"(GetWindowText) text = [{text}]")

    # GetDlgItemText
    textA = win32gui.GetDlgItemText(3932736, 59648)
    print(f"(GetDlgItemText) text = [{textA}]")

    getTextEditByClip(control_hwnd)

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
