from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from utilities.screens import ScreensUtilities
from utilities.settings import Settings


class SyncScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.dialog = None

    def setSync(self, sync):
        self.sync = sync
        self.title.title = self.sync.name
        self.dir.text = self.sync.dir1 + " - " + self.sync.dir2

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

        self.sync.delete()
        ScreensUtilities.getInstance().goTo("main", True)

    def sync_now(self):
        self.sync.sync()

    def resolve_all(self):
        self.sync.resolve_all()

    def resolve(self, conflict):
        conflict.resolve()


    def set_list_md_icons(self):
        self.ids.rv.data = []
        i = 0
        collisions = [{"dir": "blablabla"}]  # TODO
        for item in collisions:
            self.ids.rv.data.append(
                {
                    "viewclass": "SyncListItem",
                    "text": item["dir"],
                    "on_release": lambda x=i: self.resolve(x),
                }
            )
            i += 1

    def on_pre_enter(self, *args):
        self.set_list_md_icons()
