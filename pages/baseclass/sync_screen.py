from components.baseclass.sync_list_item import \
    SyncListItem  # it's in use via kivy
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from utilities.screens import ScreensUtilities
from utilities.storage import Storage
from utilities.sync_core_libs.diff_type import DiffType


class SyncScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.dialog = None

    def setSync(self, sync):
        self.sync = sync
        self.sync.event.new_detail += self.detail
        self.sync.event.new_status += self.set_conflicts_list
        self.title.title = self.sync.name
        self.dir.text = self.sync.dir1 + " - " + self.sync.dir2

        self.set_conflicts_list()
        self.detail()

    def resolve_all_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Files from which folder should be copy?",
                buttons=[
                    MDRaisedButton(
                        text="Directory 1", on_press=lambda _: self.resolve_all(1)
                    ),
                    MDRaisedButton(
                        text="Directory 2", on_press=lambda _: self.resolve_all(2)
                    ),
                ],
            )
        self.dialog.open()
        self.dialog.on_dismiss = self.dismiss_dialog

    def resolve_all(self, dir):
        if self.dialog:
            self.dialog.dismiss()

        self.sync.resolve_all(dir)

    def delete_dialog(self):
        if not self.dialog:
            if self.sync.in_sync:
                self.dialog = MDDialog(
                    text="You cannot delete it while it's syncing.",
                    buttons=[
                        MDFlatButton(
                            text="Ok", on_press=lambda _: self.dialog.dismiss()
                        ),
                    ],
                )
            else:
                self.dialog = MDDialog(
                    text="Are you sure you want to delete it?",
                    buttons=[
                        MDFlatButton(
                            text="Cancel", on_press=lambda _: self.dialog.dismiss()
                        ),
                        MDRaisedButton(
                            text="Delete",
                            md_bg_color=(1, 0, 0, 1),
                            on_press=lambda _: self.delete(),
                        ),
                    ],
                )
        self.dialog.open()
        self.dialog.on_dismiss = self.dismiss_dialog

    def dismiss_dialog(self):
        self.dialog = None
        return False

    def delete(self):
        if self.dialog:
            self.dialog.dismiss()

        Storage().remove(self.sync)
        ScreensUtilities().goTo("main", True)

    def sync_now(self):
        if self.sync_button.text == "Sync":
            self.sync.sync()
        elif self.sync_button.text == "Stop":
            self.sync.stop()

    def detail(self):
        self.log.text = self.sync.detail

        self.resolve_all_button.clear_widgets()
        if self.sync.conflicts and not self.sync.resolving and not self.sync.in_sync:
            self.resolve_all_button.add_widget(
                MDRaisedButton(
                    text="Resolve all", on_press=lambda _: self.resolve_all_dialog()
                )
            )

        if self.sync.resolving:
            if self.sync.break_sync == True:
                self.sync_button.text = "Stoping..."
                self.sync_button.disabled = True
            else:
                self.sync_button.text = "Stop"
                self.sync_button.disabled = False
        elif self.sync.in_sync:
            if self.sync.detail != "Looking for differences...":
                if self.sync.break_sync == True:
                    self.sync_button.text = "Stoping..."
                    self.sync_button.disabled = True

                else:
                    self.sync_button.text = "Stop"
                    self.sync_button.disabled = False

            else:
                self.sync_button.text = "Syncing..."
                self.sync_button.disabled = True

        else:
            self.sync_button.text = "Sync"
            self.sync_button.disabled = False

    def set_conflicts_list(self):
        self.ids.rv.data = []

        if self.sync.in_sync or self.sync.resolving:
            self.ids.spiner.active = True
            self.ids.spiner.size = (dp(50), dp(50))
        else:
            self.ids.spiner.active = False
            self.ids.spiner.size = (dp(0), dp(0))

            for item in self.sync.conflicts:
                self.ids.rv.data.append(
                    {
                        "viewclass": "SyncListItem",
                        "icon": item.type.value,
                        "text": f"{item.path1} - {item.path2}",
                        "on_release": lambda conf=item, sync=self.sync: self.open_conflict(
                            sync, conf
                        ),
                    }
                )

    def open_conflict(self, sync, conflict):
        if conflict.type == DiffType.Error:
            if not self.dialog:
                self.dialog = MDDialog(
                    title = "Error",
                    text = f"There is a problem with this conflict so you have to resolve it manually. Sync again when done.\n\nError Details:\n{conflict.error}",
                    buttons=[
                        MDFlatButton(text="Ok", on_press=lambda _: self.dialog.dismiss()),
                    ],
                )
            self.dialog.open()
            self.dialog.on_dismiss = self.dismiss_dialog
        else:
            ScreensUtilities().goToConfilct(sync, conflict)

    def on_pre_leave(self, *args):
        Storage().unsubscribe_new_status(self.set_conflicts_list)
        Storage().unsubscribe_new_detail(self.detail)
