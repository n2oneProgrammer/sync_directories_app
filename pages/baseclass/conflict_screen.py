from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.uix.snackbar import Snackbar
from utilities.conflict_resolver.conflict_resolver_file import ConflictResolverFile
from utilities.screens import ScreensUtilities


class ConflictScreen(Screen):
    def setSync(self, sync, conflict):
        self.sync = sync
        self.conflict = conflict
        self.title.title = self.conflict.path1 + " - " + self.conflict.path2
        self.resolver = ConflictResolverFile(self.conflict, self.sync.sync_core)
        self.text.text = self.resolver.get_diff()

    def goBack(self):
        ScreensUtilities().goToSync(self.sync, True)

    def file1(self):
        self.text.text = self.resolver.get_content_path1()

    def file2(self):
        self.text.text = self.resolver.get_content_path2()

    def compare(self):
        self.text.text = self.resolver.get_diff()

    def save(self):
        if not self.resolver.is_resolved(self.text.text):
            Snackbar(
                text="First you need to resolve it!",
                snackbar_x="10dp",
                snackbar_y="10dp",
                bg_color=(0.8, 0, 0, 1),
                size_hint_x=(Window.width - (dp(10) * 2)) / Window.width,
            ).open()
            return
        self.resolver.resolve(self.text.text)
        ScreensUtilities().goToSync(self.sync, True, True)
