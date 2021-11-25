from re import S

from kivymd.uix.boxlayout import MDBoxLayout


class SettingsStringDialog(MDBoxLayout):
    def __init__(self, value, hint, **kwargs):
        super().__init__(**kwargs)
        self.ids.field.text = value
        self.ids.field.hint_text = hint
