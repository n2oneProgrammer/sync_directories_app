from kivymd.uix.boxlayout import MDBoxLayout


class SettingsBoolDialog(MDBoxLayout):
    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.ids.field.active = value
