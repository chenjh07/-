import pyautogui
import pynput
import time
import ctypes
import ctypes.wintypes
from threading import Thread
import win32con

Radius = 6
YAxisRatio = 1.414
left = 0
top = 0
width = 200
height = 200
ori_x = 0  # 834
ori_y = 0  # 510
me_x = 900
me_y = 500
aim_x = 0
aim_y = 0
momentum = 1.3


class Hotkey(Thread):

    def run(self):
        user32 = ctypes.windll.user32
        if not user32.RegisterHotKey(None, 100, win32con.MOD_ALT, 0x5A):
            print('RuntimeError')
        if not user32.RegisterHotKey(None, 101, win32con.MOD_ALT, 0x31):
            print('RuntimeError')
        if not user32.RegisterHotKey(None, 102, win32con.MOD_ALT, 0x32):
            print('RuntimeError')
        if not user32.RegisterHotKey(None, 103, win32con.MOD_ALT, 0x33):
            print('RuntimeError')
        if not user32.RegisterHotKey(None, 104, win32con.MOD_ALT, 0x53):
            print('RuntimeError')
        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:  # GetMessageA 会堵塞线程直到收到事件
                # print(msg.message, msg.wParam)
                if msg.message == win32con.WM_HOTKEY:
                    id = msg.wParam
                    if id == 100:
                        print('alt+z')
                        rescan()
                    elif id == 101:
                        print('alt+1')
                        aim()
                    elif id == 102:
                        print('alt+2')
                        aim_hot()
                    elif id == 103:
                        print('alt+3')
                        predict('suan.png')
                    elif id == 104:
                        print('alt+s')
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)


# 把字符串按'|'切割
def word_cut(args):
    tup = []
    if '|' in args:
        re1 = args.split('|')
        return re1
    else:
        tup.append(args)
        return tuple(tup)


# 循环找图，找到就返回图像中心点，没找到就打印'没找到'
def enemy_locate(args):
    arg = word_cut(args)
    l = len(arg)
    for i in range(0, l):
        loc = pyautogui.locateOnScreen(arg[i], grayscale=True,
                                       region=(
                                       int(me_x - width / 4), int(me_y - height / 4), int(width / 2), int(height / 2)),
                                       confidence=0.6)
        if loc is not None:
            return pyautogui.center(loc)
        # else:
        # print("没找到", i)


def rescan():
    global left, top, width, height, ori_x, ori_y
    s = pyautogui.locateOnScreen("map.png", confidence=0.6)
    s_full = pyautogui.locateOnScreen("map_full.png", confidence=0.6)
    t = pyautogui.locateOnScreen("set.png", confidence=0.6)
    t_full = pyautogui.locateOnScreen("set_full.png", confidence=0.6)
    if s is not None and t is not None:
        width = int(s.width * 1.25)
        height = int(s.height * 1.25)
        left = max(int(s.left - s.width / 8), 0)
        top = max(int(s.top - s.height / 8), 0)
        ori_x = int((t.left + t.width * 3 - s.left) / 2)
        ori_y = int(ori_x * 0.61)
    elif s_full is not None and t_full is not None:
        width = int(s_full.width * 1.25)
        height = int(s_full.height * 1.25)
        left = max(int(s_full.left - s_full.width / 8), 0)
        top = max(int(s_full.top - s_full.height / 8), 0)
        ori_x = int((t_full.left + t_full.width * 1.6 - s_full.left) / 2)
        ori_y = int((ori_x * 0.59))
    # print(s, left, top, width, height, ori_x, ori_y)
    pyautogui.moveTo(left + ori_x, top + ori_y)


def find():
    global me_x, me_y
    me_locate = pyautogui.locateOnScreen("me.png", grayscale=True, region=(left, top, width, height), confidence=0.7)
    me_locate_full = pyautogui.locateOnScreen("me_full.png", grayscale=True, region=(left, top, width, height),
                                              confidence=0.7)
    if me_locate_full is not None:
        me_x, me_y = pyautogui.center(me_locate_full)
    elif me_locate is not None:
        me_x, me_y = pyautogui.center(me_locate)


def on_click(x, y, button, pressed):
    enemy_pos = enemy_locate('suan.png')  # mark.png|mark_full.png|suan.png|suan_full.png|
    if enemy_pos is not None:
        aim_x = (enemy_pos[0] - me_x) * YAxisRatio * Radius + left + ori_x
        aim_y = (enemy_pos[1] - me_y) * Radius + top + ori_y
        pyautogui.moveTo(aim_x, aim_y)
    if not pressed:
        # Stop listener
        return False


def listen():
    def on_press(key):
        if key == pynput.keyboard.KeyCode(char='w'):
            predict('suan.png')
        # 通过属性判断按键类型。

    def on_release(key):
        if key == pynput.keyboard.KeyCode(char='w'):
            pyautogui.moveTo(aim_x, aim_y)
            # Stop listener
            return False

    with pynput.keyboard.Listener(on_press=on_press,
                                  on_release=on_release) as listener:
        listener.join()


class ListenThread(Thread):

    def __init__(self):
        super().__init__()

    def run(self):
        listen()


def aim():
    find()
    with pynput.mouse.Listener(on_click=on_click) as listener:
        listener.join()
    print('aimed')


def aim_hot():
    find()
    listenThread = ListenThread()
    listenThread.start()


def predict(args):
    print('predict', args)
    global aim_x, aim_y, me_x, me_y, width, height
    enemy_pos_pre = [0, 0]

    enemy_pos_last = None
    while enemy_pos_last is None:
        enemy_pos_last = enemy_locate(args)

    enemy_pos_now = None
    while enemy_pos_now is None:
        enemy_pos_now = enemy_locate(args)
    if enemy_pos_now is not None and enemy_pos_last is not None:
        enemy_pos_pre[0] = enemy_pos_now[0] * (1 + momentum) - enemy_pos_last[0] * momentum
        enemy_pos_pre[1] = enemy_pos_now[1] * (1 + momentum) - enemy_pos_last[1] * momentum
        aim_x = (enemy_pos_pre[0] - me_x) * YAxisRatio * Radius + left + ori_x
        aim_y = (enemy_pos_pre[1] - me_y) * Radius + top + ori_y

        pyautogui.moveTo(aim_x, aim_y)


if __name__ == "__main__":
    time.sleep(5)
    rescan()
    hot = Hotkey()
    hot.start()
