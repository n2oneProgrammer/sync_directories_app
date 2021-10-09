from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from utilities.screens import ScreensUtilities


class SyncScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.dialog = None

    def setSync(self, sync):
        self.sync = sync
        self.title.title = self.sync.name
        self.dir.text = self.sync.dir1 + " - " + self.sync.dir2
        self.set_conflicts_list()

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
        ScreensUtilities().goTo("main", True)

    def sync_now(self):
        self.sync.sync(self.set_conflicts_list)

    def resolve_all(self):
        self.sync.resolve_all()

    def resolve(self, conflict):
        conflict.resolve()

    def set_conflicts_list(self):
        self.ids.rv.data = []
        collisions = self.sync.conflicts
        for item in collisions:
            self.ids.rv.data.append(
                {
                    "viewclass": "SyncListItem",
                    "icon": item.type.value,
                    "text": f"{item.path1} - {item.path2}",
                    "on_release": lambda conf=item, sync=self.sync: ScreensUtilities().goToConfilct(
                        sync, conf
                    ),
                }
            )
