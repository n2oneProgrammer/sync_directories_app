import json
import webbrowser

from components.baseclass.settings_range_dialog import SettingsRangeDialog
from components.baseclass.settings_string_dialog import SettingsStringDialog
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from utilities.path import slugify
from utilities.settings import Settings


class SettingsScreen(Screen):
    def on_pre_enter(self, *args):
        self.dialog = None
        self.set_list()

    def set_list(self):
        self.ids.rv.data = []
        for item in Settings().user_settings:
            self.ids.rv.data.append(
                {
                    "viewclass": "TwoLineListItem",
                    "text": item["title"],
                    "secondary_text": item["description"],
                    "on_release": lambda x=item: self.open_setting(x),
                }
            )

    def open_setting(self, item):
        if item["type"] == "url":
            webbrowser.open(item["url"])
        else:
            self.open_dialog(item)

    def get_dialog(self, item):

        content = None

        if item["type"] == "string":
            content = SettingsStringDialog(
                value=Settings().get(item["value"]), hint=item["title"]
            )
        elif item["type"] == "range":
            content = SettingsRangeDialog(value=Settings().get(item["value"]))

        return MDDialog(
            title=item["title"],
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancel", on_press=lambda x: self.dialog.dismiss()),
                MDRaisedButton(
                    text="Save",
                    on_press=lambda x: self.dialog_save(item, content.ids.field),
                ),
            ],
        )

    def open_dialog(self, item):
        if not self.dialog:
            self.dialog = self.get_dialog(item)
        self.dialog.open()
        self.dialog.on_dismiss = self.dismiss_dialog

    def dismiss_dialog(self):
        self.dialog = None
        return False

    def dialog_save(self, item, field):
        v = None
        if item["type"] == "string":
            v = field.text
        elif item["type"] == "range":
            v = field.value

        if item.get("converter") is not None:
            if item["converter"] == "filename":
                v = slugify(v, allow_unicode=True)

        key = item["value"]
        Settings().set(key, v)
        self.dialog.dismiss()
