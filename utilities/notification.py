import time
from threading import Thread


def notify(title, message, duration=3):
    Thread(
        target=_notify,
        name="Notifcation",
        args=(
            title,
            message,
            duration,
        ),
    ).start()


def _notify(title, message, duration):

    from main import Tray

    tray = Tray.getInstance()

    print(title, message, tray.n)

    while tray.n:
        pass

    tray.n = True
    tray.notify(title, message, duration)
    tray.n = False
