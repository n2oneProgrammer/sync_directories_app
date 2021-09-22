from components.baseclass.sync_list_item import \
    SyncListItem  # it's in use via kivy
from kivy.uix.screenmanager import Screen
from utilities.folder import Folder
from utilities.screens import ScreensUtilities


class MainScreen(Screen):
    def set_list_md_icons(self):
        self.ids.rv.data = []
        syncs = Folder.load_all()
        for item in syncs:
            self.ids.rv.data.append(
                {
                    "viewclass": "SyncListItem",
                    "icon": "check",  # TODO
                    "text": item.name,
                    "secondary_text": item.dir1 + " - " + item.dir2,
                    "on_release": lambda x=item: self.goToSync(x),
                }
            )

    def on_pre_enter(self, *args):
        self.set_list_md_icons()

    def goToSync(self, sync):
        ScreensUtilities.getInstance().goToSync(sync)
