from os import path

import easygui
from kivy.uix.screenmanager import Screen
from utilities.screens import ScreensUtilities
from utilities.settings import Settings


class CreateSyncScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.input_name.bind(on_text_validate=self.v_name)
        self.dir1.bind(on_text_validate=self.validate)
        self.dir2.bind(on_text_validate=self.validate)

    def open_dialog1(self):
        path = easygui.diropenbox()
        if path:
            self.dir1.text = path

    def open_dialog2(self):
        path = easygui.diropenbox()
        if path:
            self.dir2.text = path

    def v_name(self, instance):
        if not len(instance.text) >= 4:
            instance.error = True
            instance.helper_text = "Must be at least 4 characters long"
            return False
        else:
            instance.error = False
            return True

    def validate(self, instance):
        if not path.exists(instance.text):
            instance.error = True
            instance.helper_text = "Invalid path"
            return False
        else:
            instance.error = False
            return True

    def save(self):
        if not (
            self.validate(self.dir1)
            and self.validate(self.dir2)
            and self.v_name(self.input_name)
        ):
            self.dir1.text = self.dir1.text
            return
        syncs = Settings.getInstance().get("syncs")
        if syncs == None:
            syncs = []
        syncs.append(
            {
                "name": self.input_name.text,
                "dir1": self.dir1.text,
                "dir2": self.dir2.text,
                "status": "check",
            }
        )
        Settings.getInstance().set("syncs", syncs)
        ScreensUtilities.getInstance().goToSync(len(syncs) - 1)
