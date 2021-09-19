from os import path

import easygui
from kivy.uix.screenmanager import Screen
from utilities.screens import ScreensUtilities
from utilities.settings import Settings


class CreateSyncScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.bind()

    def _bind(self):
        self.input_name.bind(on_text_validate=self.v_name)
        self.dir1.bind(on_text_validate=self.validate)
        self.dir2.bind(on_text_validate=self.validate)

    def open_dialog1(self):
        path = easygui.diropenbox()
        if path:
            self.dir1.text = path
        self.validate(self.dir1)
        self.dir1.check_text(1)

    def open_dialog2(self):
        path = easygui.diropenbox()
        if path:
            self.dir2.text = path
        self.validate(self.dir2)
        self.dir2.check_text(1)

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

        v1 = self.validate(self.dir1)
        v2 = self.validate(self.dir2)
        v3 = self.v_name(self.input_name)

        if not (v1 and v2 and v3):
            self.dir1.check_text(1)
            self.dir2.check_text(1)
            self.input_name.check_text(1)
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
        self.reset()
        Settings.getInstance().set("syncs", syncs)
        ScreensUtilities.getInstance().goToSync(len(syncs) - 1)

    def reset(self):
        self._reset(self.input_name)
        self._reset(self.dir1)
        self._reset(self.dir2)

    def _reset(self, instance):
        instance.text = ""
        instance.error = False
        instance.check_text(1)

    def back(self):
        self.reset()
        ScreensUtilities.getInstance().goTo("main", True)
