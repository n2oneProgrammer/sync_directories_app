from components.baseclass.sync_list_item import \
    SyncListItem  # it's in use via kivy
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import Snackbar
from utilities.screens import ScreensUtilities
from utilities.storage import Storage


class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.snackbar = None
        for sync in Storage().syncs:
            sync.event.new_status += self.set_folder_list


    def set_folder_list(self):
        self.ids.rv.data = []
        try:
            for item in Storage().syncs:
                self.ids.rv.data.append(
                    {
                        "viewclass": "SyncListItem",
                        "icon": item.status(),
                        "text": item.name,
                        "secondary_text": item.dir1 + " - " + item.dir2,
                        "on_release": lambda x=item: self.goToSync(x),
                    }
                )
        except:
            pass

    def on_pre_enter(self, *args):
        self.snackbar = None
        self.set_folder_list()

    def sync_all(self):
        for sync in Storage().syncs:
            sync.sync()

    def goToSync(self, sync):
        if not sync.valid():
            sync.event.new_status()
            if self.snackbar is None:
                self.snackbar = Snackbar(
                    text="Cannot acess folder dir!",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    bg_color=(0.8, 0, 0, 1),
                    size_hint_x=(Window.width - (dp(10) * 2)) / Window.width,
                )
                button = MDFlatButton(
                    text="DELETE",
                    text_color=(1, 1, 1, 1),
                    on_release=lambda y, x=sync: self.del_sync(x),
                )
                self.snackbar.buttons.append(button)
                self.snackbar.open()
                self.snackbar.on_dismiss = self.dismiss_snackbar

            return
        ScreensUtilities().goToSync(sync)

    def dismiss_snackbar(self):
        self.snackbar = None

    def del_sync(self, sync):
        if sync in Storage().syncs:
            if self.snackbar is not None:
                self.snackbar.dismiss()
            Storage().remove(sync)
            self.set_folder_list()
