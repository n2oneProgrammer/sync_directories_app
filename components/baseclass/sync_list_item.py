from kivy.properties import StringProperty
from kivymd.uix.list import TwoLineAvatarIconListItem


class SyncListItem(TwoLineAvatarIconListItem):
    icon = StringProperty()
