import time
from threading import Thread

from PIL import Image
from pystray import Icon, Menu, MenuItem


def create_image():
    image = Image.new("RGB", (64, 64), 0)
    return image


def notify():
    icon.notify(title="Hello World!", message="xd")
    time.sleep(3)
    icon.remove_notification()


def on_click():
    Thread(target=notify).start()


def run():
    from app import run

    run()


icon = Icon("test name", title="xd")
icon.icon = create_image()
icon.menu = Menu(MenuItem("text", on_click), MenuItem("run", run))

if __name__ == "__main__":
    icon.run()
