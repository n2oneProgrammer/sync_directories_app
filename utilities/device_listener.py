from threading import Thread

import win32api
import win32con
import win32gui

from utilities.settings import Settings


class DeviceListener:
    """
    Listens to Win32 `WM_DEVICECHANGE` messages
    and trigger a callback when a device has been plugged in or out

    See: https://docs.microsoft.com/en-us/windows/win32/devio/wm-devicechange
    """

    def __init__(self, on_change):
        self.on_change = on_change

    def _create_window(self):
        """
        Create a window for listening to messages
        https://docs.microsoft.com/en-us/windows/win32/learnwin32/creating-a-window#creating-the-window

        See also: https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createwindoww

        :return: window hwnd
        """
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._on_message
        wc.lpszClassName = self.__class__.__name__
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        return win32gui.CreateWindow(
            class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
        )

    def start(self):
        Thread(target=self._start, name=f"DeviceListener").start()

    def _start(self):
        hwnd = self._create_window()
        print(f"Created listener window with hwnd {hwnd:x}")
        win32gui.PumpMessages()

    def _on_message(self, hwnd: int, msg: int, wparam: int, lparam: int):
        if not Settings().get("pendrive_sync"):
            return
        if msg != win32con.WM_DEVICECHANGE:
            return 0
        print(f"Code: ({wparam:x})")
        if 0x8000 == wparam:
            print(f"A device has been plugged in")
            self.on_change()
        return 0
