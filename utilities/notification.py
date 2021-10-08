from threading import Thread

from win10toast import ToastNotifier

from utilities.path import convert_path


class Notification:
    __instance = None

    @staticmethod
    def getInstance():
        if Notification.__instance == None:
            Notification()
        return Notification.__instance

    def __init__(self):

        if Notification.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Notification.__instance = self

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
