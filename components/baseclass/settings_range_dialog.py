from kivymd.uix.boxlayout import MDBoxLayout


class SettingsRangeDialog(MDBoxLayout):
    def __init__(self, value, min, max, **kwargs):
        super().__init__(**kwargs)
        self.ids.field.value = value
        self.ids.field.min = min
        self.ids.field.max = max
