from threading import Thread


def notify(title, message, duration=3):
    from main import Tray

    Thread(
        target=Tray.getInstance().notify,
        name="Notifcation",
        args=(
            title,
            message,
            duration,
        ),
    ).start()
