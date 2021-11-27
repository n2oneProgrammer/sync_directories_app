import webbrowser

from components.baseclass.settings_bool_dialog import SettingsBoolDialog
from components.baseclass.settings_list_item import \
    SettingsListItem  # it's in use via kivy
from components.baseclass.settings_range_dialog import SettingsRangeDialog
from components.baseclass.settings_string_dialog import SettingsStringDialog
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from utilities.autostart import Autostart
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
                    "viewclass": "SettingsListItem",
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
            content = SettingsRangeDialog(
                value=Settings().get(item["value"]), min=item["min"], max=item["max"]
            )
        elif item["type"] == "bool":
            content = SettingsBoolDialog(value=Settings().get(item["value"]))

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
        key = item["value"]

        if item["type"] == "string":
            v = field.text
        elif item["type"] == "range":
            v = field.value
            
        elif item["type"] == "bool":
            v = field.active

        if item.get("converter") is not None:
            if item["converter"] == "filename":
                v = slugify(v, allow_unicode=True)
                Settings().set(key, v)
            elif item["converter"] == "autostart":
                Settings().set(key, v)
                Autostart().update()
            elif item["converter"] == "int":
                v = int(v)
                Settings().set(key, v)
            else:
                Settings().set(key, v)
        else:
            Settings().set(key, v)
        self.dialog.dismiss()
