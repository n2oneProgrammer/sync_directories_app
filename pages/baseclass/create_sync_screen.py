from os import path

import easygui
from kivy.uix.screenmanager import Screen
from utilities.folder import Folder
from utilities.screens import ScreensUtilities


class CreateSyncScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.bind()

    def _bind(self):
        self.input_name.bind(on_text_validate=self.v_name, on_focus=self.v_name)
        self.dir1.bind(on_text_validate=self.v_dir1, on_focus=self.v_dir1)
        self.dir2.bind(on_text_validate=self.v_dir2, on_focus=self.v_dir2)

    def open_dialog1(self):
        path = easygui.diropenbox()
        if path:
            self.dir1.text = path
        self.v_dir1()
        self.dir1.check_text(1)

    def open_dialog2(self):
        path = easygui.diropenbox()
        if path:
            self.dir2.text = path
        self.v_dir2()
        self.dir2.check_text(1)

    def v_name(self):
        if not len(self.input_name.text) >= 4:
            self.input_name.error = True
            self.input_name.helper_text = "Must be at least 4 characters long"
            return False
        else:
            self.input_name.error = False
            return True

    def v_dir1(self):
        if not path.exists(self.dir1.text):
            self.dir1.error = True
            self.dir1.helper_text = "Invalid path"
            return False
        elif self.dir1.text == self.dir2.text:
            self.dir1.error = True
            self.dir1.helper_text = "Cannot be the same as directory 1"
            return False
        else:
            self.dir1.error = False
            return True

    def v_dir2(self):
        if not path.exists(self.dir2.text):
            self.dir2.error = True
            self.dir2.helper_text = "Invalid path"
            return False
        elif self.dir1.text == self.dir2.text:
            self.dir2.error = True
            self.dir2.helper_text = "Cannot be the same as directory 2"
            return False
        else:
            self.dir2.error = False
            return True

    def save(self):

        v1 = self.v_dir1()
        v2 = self.v_dir2()
        v3 = self.v_name()

        if not (v1 and v2 and v3):
            self.dir1.check_text(1)
            self.dir2.check_text(1)
            self.input_name.check_text(1)
            return

        f = Folder(
            {
                "name": self.input_name.text,
                "dir1": self.dir1.text,
                "dir2": self.dir2.text,
            }
        )
        f.force_update()
        self.reset()
        ScreensUtilities().goToSync(f)

    def reset(self):
        self._reset(self.input_name)
        self._reset(self.dir1)
        self._reset(self.dir2)

    def _reset(self, instance):
        instance.text = ""
        instance.helper_text = ""
        instance.error = False
        instance.check_text(1)

    def back(self):
        self.reset()
        ScreensUtilities().goTo("main", True)
