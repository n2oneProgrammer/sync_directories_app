from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from utilities.screens import ScreensUtilities
from utilities.settings import Settings
from utilities.sync_core import SyncCore


class SyncScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.dialog = None

    def setSync(self, id):
        self.id = id
        self.sync = Settings.getInstance().get("syncs")[id]
        self.title.title = self.sync["name"]

    def delete_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Are you sure you want to delete it?",
                buttons=[
                    MDFlatButton(
                        text="Cancel", on_press=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="Delete",
                        md_bg_color=(1, 0, 0, 1),
                        on_press=lambda x: self.delete(),
                    ),
                ],
            )
        self.dialog.open()

    def delete(self):
        if self.dialog:
            self.dialog.dismiss()

        syncs = Settings.getInstance().get("syncs")
        syncs.pop(self.id)
        Settings.getInstance().set("syncs", syncs)
        ScreensUtilities.getInstance().goTo("main", True)

    def sync_now(self):
        SyncCore(self.sync["dir1"],self.sync["dir2"]).sync_dir()
