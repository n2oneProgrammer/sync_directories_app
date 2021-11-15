from threading import Thread

from win10toast import ToastNotifier

from utilities.path import convert_path


class Notification:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance._init()
        return cls.__instance

    def _init(self):
        self.toaster = ToastNotifier()
        self.n = False

    def notify(self, title, message, duration=5):

        Thread(
            target=self._notify,
            name="Notifcation",
            args=(
                title,
                message,
                duration,
            ),
        ).start()

    def _notify(self, title, message, duration):

        while self.n:
            pass

        self.n = True
        ToastNotifier().show_toast(
            title,
            message,
            icon_path=convert_path("icon.ico"),
            duration=duration,
        )
        self.n = False
