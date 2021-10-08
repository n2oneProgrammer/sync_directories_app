from kivy.uix.screenmanager import Screen
from utilities.screens import ScreensUtilities


class ConflictScreen(Screen):
    def setSync(self, sync, conflict):
        self.sync = sync
        self.conflict = conflict
        self.title.title = self.conflict.path1 + " - " + self.conflict.path2

    def goBack(self):
        ScreensUtilities().goToSync(self.sync, True)
