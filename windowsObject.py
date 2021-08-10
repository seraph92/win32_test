import win32gui
import win32api
import win32con
import ctypes


class WindowsObject:
    def __init__(self, text=None, parent_hwnd=None):
        self.win_objs = []
        win32gui.EnumWindows(self.__EnumWindowsHandler, text)
 
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

class ChildObject:
    def __init__(self, parent_hwnd=None, match_class=None):
        self.parent_hwnd = parent_hwnd
        self.match_class = match_class
        self.win_objs = []
        win32gui.EnumChildWindows(parent_hwnd, self.__EnumChildWindowsHandler, None)

    def __EnumChildWindowsHandler(self, hwnd, find_text):
        wintext = win32gui.GetWindowText(hwnd)
        print(f"wintext=[{wintext}]")

        if find_text:
            if wintext.find(find_text) != -1:
                if self.match_class:
                    wnd_clas = win32gui.GetClassName(hwnd)
                    if wnd_clas.find():
                        obj = {}
                        obj['handle'] = hwnd
                        obj['text'] = wintext
                        self.win_objs.append(obj)
                else:
                    obj = {}
                    obj['handle'] = hwnd
                    obj['text'] = wintext
                    self.win_objs.append(obj)
        else:
            obj = {}
            obj['handle'] = hwnd
            obj['text'] = wintext
            self.win_objs.append(obj)

if __name__ == '__main__':
    #win32gui.EnumWindows(EnumWindowsHandler, None)
    w = WindowsObject("KRC-EC100")
    print(f"w={w.win_objs}")
    #print(f"child = {w.getFirstObj().get('handle')}")
    #print(f"child = {w.getFirstObj()['handle']}")
    print(f"parent.handle=[{w.getFirstObj()['handle']}], parent.text=[{w.getFirstObj()['text']}]")
    parent = w.getFirstObj()['handle']
    children = ChildObject(w.getFirstObj()['handle'], 'WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1')
    print(f"children={children.win_objs}")

    for child in children.win_objs:
        hwnd = child['handle']
        ctrl_id  = win32gui.GetDlgCtrlID(hwnd)
        wnd_clas = win32gui.GetClassName(hwnd)
        wnd_text = win32gui.GetWindowText(hwnd)        

        print( "%08X %6d\t%s\t%s" % (hwnd, ctrl_id, wnd_clas, wnd_text) )

    # class: WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1
    '''
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
    '''