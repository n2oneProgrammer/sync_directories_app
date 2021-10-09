from kivy.uix.screenmanager import Screen
from utilities.conflict_resolver.conflict_resolver_file import \
    ConflictResolverFile
from utilities.screens import ScreensUtilities


class ConflictScreen(Screen):
    def setSync(self, sync, conflict):
        self.sync = sync
        self.conflict = conflict
        self.title.title = self.conflict.path1 + " - " + self.conflict.path2
        self.resolver = ConflictResolverFile(self.conflict, self.sync.sync_core)
        self.text.text = self.resolver.get_content_merge()

    def goBack(self):
        ScreensUtilities().goToSync(self.sync, True)

    def file1(self):
        self.text.text = self.resolver.get_content_path1()

    def file2(self):
        self.text.text = self.resolver.get_content_path2()

    def compare(self):
        self.text.text = self.resolver.get_content_merge()

    def save(self):
        self.resolver.resolve(self.text.text)
        ScreensUtilities().goToSync(self.sync, True, True)
