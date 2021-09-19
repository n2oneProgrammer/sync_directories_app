from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from pages.baseclass.create_sync_screen import CreateSyncScreen
from pages.baseclass.main_screen import MainScreen
from pages.baseclass.settings_screen import SettingsScreen
from pages.baseclass.sync_screen import SyncScreen
from utilities.loader import load_kv
from utilities.screens import ScreensUtilities


class SyncDirectories(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        ScreensUtilities.getInstance().sm.add_widget(MainScreen(name="main"))
        ScreensUtilities.getInstance().sm.add_widget(SyncScreen(name="sync"))
        ScreensUtilities.getInstance().sm.add_widget(SettingsScreen(name="settings"))
        ScreensUtilities.getInstance().sm.add_widget(CreateSyncScreen(name="create"))

        return ScreensUtilities.getInstance().sm

    def goTo(self, screen, right):
        ScreensUtilities.getInstance().goTo(screen=screen, right=right)

def run():
    load_kv()
    ScreensUtilities.getInstance(sm=ScreenManager())
    SyncDirectories().run()
