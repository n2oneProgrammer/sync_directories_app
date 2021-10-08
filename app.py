import asyncio

from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from pages.baseclass.conflict_screen import ConflictScreen
from pages.baseclass.create_sync_screen import CreateSyncScreen
from pages.baseclass.main_screen import MainScreen
from pages.baseclass.settings_screen import SettingsScreen
from pages.baseclass.sync_screen import SyncScreen
from utilities.loader import load_kv
from utilities.path import get_icon_path
from utilities.screens import ScreensUtilities


class SyncDirectories(MDApp):
    def build(self):

        # TODO: fix icon
        self.icon = get_icon_path()
        Window.set_icon(self.icon)

        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"

        if App().first:
            self.setup_sm()

        return ScreensUtilities().sm

    def goTo(self, screen, right):
        ScreensUtilities().goTo(screen=screen, right=right)

    def on_stop(self):
        App().on_close()
        Window.hide()

    def setup_sm(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(SyncScreen(name="sync"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(CreateSyncScreen(name="create"))
        sm.add_widget(ConflictScreen(name="conflict"))
        ScreensUtilities().setSm(sm)


class App:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance._init()
        return cls.__instance

    def _init(self):
        load_kv()

        self.first = True
        self.opened = False

    def on_close(self):
        self.opened = False

    def run(self):
        if not self.opened:
            self.opened = True
            Window.show()
            SyncDirectories().run()
            self.first = False
