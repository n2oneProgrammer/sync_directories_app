from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from utilities.conflict_resolver.conflict_resolver_file import \
    ConflictResolverFile
from utilities.screens import ScreensUtilities


class ConflictScreen(Screen):
    def setSync(self, sync, conflict):
        self.sync = sync
        self.conflict = conflict
        self.title.title = self.conflict.path1 + " - " + self.conflict.path2
        self.resolver = ConflictResolverFile(self.conflict, self.sync.sync_core)

        self.comp_button.clear_widgets()

        if self.resolver.have_diff():
            self.content = self.resolver.get_content_path1()
        else:
            self.content = self.resolver.get_diff()
            self.comp_button.add_widget(
                MDRaisedButton(text="Compare", on_press=self.compare)
            )
        self.update()

    def goBack(self):
        ScreensUtilities().goToSync(self.sync, True)

    def file1(self):
        self.content = self.resolver.get_content_path1()
        self.update()

    def file2(self):
        self.content = self.resolver.get_content_path2()
        self.update()

    # this x is beceause of the kive require some argument when you call on press
    def compare(self, x):
        self.content = self.resolver.get_diff()
        self.update()

    def update(self):
        self.text.clear_widgets()

        if self.content.is_deleted:
            self.text.add_widget(
                MDLabel(
                    text="This file is deleted",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(1, 0.1, 0.1, 1),
                )
            )
        elif self.content.is_binary:
            self.text.add_widget(
                MDLabel(
                    text="This file is binary",
                    halign="center",
                )
            )
        else:
            self.text.add_widget(
                TextInput(
                    background_color=(0.05, 0.1, 0.1, 1),
                    cursor_color=(0.9, 0.9, 0.9, 1),
                    foreground_color=(0.9, 0.9, 0.9, 1),
                    text=self.content.get_content(),
                )
            )

    def save(self):
        self.content.text = self.text.children[0].text  # TODO: Do it in better way
        if not self.resolver.is_resolved(self.content):
            Snackbar(
                text="First you need to resolve it!",
                snackbar_x="10dp",
                snackbar_y="10dp",
                bg_color=(0.8, 0, 0, 1),
                size_hint_x=(Window.width - (dp(10) * 2)) / Window.width,
            ).open()
            return
        self.resolver.resolve(self.content)
        self.sync.resolve(self.conflict)
        ScreensUtilities().goToSync(self.sync, True)
