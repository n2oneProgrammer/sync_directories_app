import winreg

from kivy.logger import Logger

from utilities.path import get_package_name, get_self_path
from utilities.settings import Settings


class Autostart:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance._init()
        return cls.__instance

    def _init(self):
        self.path = get_self_path()

    def update(self):
        if self.path is None:
            return

        app_name = get_package_name()
        if Settings().get("autostart") != self.check_autostart_registry(app_name):
            Logger.info(f"Updating autostart registry to { Settings().get('autostart') }")
            self.set_autostart_registry(
                app_name, self.path, Settings().get("autostart")
            )

    def set_autostart_registry(self, app_name, path, autostart: bool = True) -> bool:
        with winreg.OpenKey(
            key=winreg.HKEY_CURRENT_USER,
            sub_key=r"Software\Microsoft\Windows\CurrentVersion\Run",
            reserved=0,
            access=winreg.KEY_ALL_ACCESS,
        ) as key:
            try:
                if autostart:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, path)
                else:
                    winreg.DeleteValue(key, app_name)
            except OSError:
                return False
        return True

    def check_autostart_registry(self, value_name):
        with winreg.OpenKey(
            key=winreg.HKEY_CURRENT_USER,
            sub_key=r"Software\Microsoft\Windows\CurrentVersion\Run",
            reserved=0,
            access=winreg.KEY_ALL_ACCESS,
        ) as key:
            idx = 0
            while idx < 1_000:  # Max 1.000 values
                try:
                    key_name, _, _ = winreg.EnumValue(key, idx)
                    if key_name == value_name:
                        return True
                    idx += 1
                except OSError:
                    break
        return False
