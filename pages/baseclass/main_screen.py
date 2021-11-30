from components.baseclass.sync_list_item import SyncListItem  # it's in use via kivy
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from utilities.screens import ScreensUtilities
from utilities.storage import Storage


class MainScreen(Screen):
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
        self.dialog = None
        self.snackbar = None
        for sync in Storage().syncs:
            sync.event.new_status += self.set_folder_list
        self.set_folder_list()

    def sync_all(self):
        for sync in Storage().syncs:
            sync.sync()

    def goToSync(self, sync):
        if not sync.valid():
            sync.event.new_status()
            self.open_dialog(
                MDDialog(
                    text="Cannot acess sync dir. Do you want to delete this sync?",
                    buttons=[
                        MDFlatButton(
                            text="Back", on_press=lambda _: self.dialog.dismiss()
                        ),
                        MDRaisedButton(
                            text="Delete",
                            md_bg_color=(1, 0, 0, 1),
                            on_press=lambda _, x=sync: self.del_sync(x),
                        ),
                    ],
                )
            )
            return
        ScreensUtilities().goToSync(sync)

    def go_to_settings(self):
        if Storage().is_in_sync_or_resolving():
            self.open_dialog(
                MDDialog(
                    text="You cannot use settings while syncing or resolving.",
                    buttons=[
                        MDFlatButton(
                            text="Ok", on_press=lambda _: self.dialog.dismiss()
                        ),
                    ],
                )
            )
            return
        ScreensUtilities().goTo("settings", False)

    def open_dialog(self, dialog):
        if not self.dialog:
            self.dialog = dialog

        self.dialog.open()
        self.dialog.on_dismiss = self.dismiss_dialog

    def dismiss_dialog(self):
        self.dialog = None
        return False

    def del_sync(self, sync):
        if sync in Storage().syncs:
            if self.dialog:
                self.dialog.dismiss()
            Storage().remove(sync)
            self.set_folder_list()

    def on_pre_leave(self, *args):
        Storage().unsubscribe_new_status(self.set_folder_list)
