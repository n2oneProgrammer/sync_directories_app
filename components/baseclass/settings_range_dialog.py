from kivymd.uix.boxlayout import MDBoxLayout


class SettingsRangeDialog(MDBoxLayout):
    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.ids.field.value = value
