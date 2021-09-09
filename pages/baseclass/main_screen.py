from components.baseclass.sync_list_item import \
    SyncListItem  # it's in use via kivy
from kivy.uix.screenmanager import Screen
from utilities.screens import ScreensUtilities
from utilities.settings import Settings


class MainScreen(Screen):
    def set_list_md_icons(self):
        self.ids.rv.data = []
        i = 0
        syncs = Settings.getInstance().get("syncs")
        if not syncs:
            return
        for item in syncs:
            self.ids.rv.data.append(
                {
                    "viewclass": "SyncListItem",
                    "icon": item["status"],
                    "text": item["name"],
                    "secondary_text": item["dir1"] + " - " + item["dir2"],
                    "on_release": lambda x=i: self.goToSync(x),
                }
            )
            i += 1

    def on_pre_enter(self, *args):
        self.set_list_md_icons()

    def goToSync(self, id):
        ScreensUtilities.getInstance().goToSync(id)
