from kivy.uix.screenmanager import NoTransition, SlideTransition


class ScreensUtilities:

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    def setSm(self, sm):
        self.sm = sm
        self.default_transition = SlideTransition() 

    def goTo(self, screen, right):
        self.sm.transition = self.default_transition
        if right:
            self.sm.transition.direction = "right"
        else:
            self.sm.transition.direction = "left"

        self.sm.current = screen

    def goToSync(self, sync, right=False):
        self.goTo("sync", right)
        screen = self.sm.get_screen(self.sm.current)
        screen.setSync(sync)

    def goToConfilct(self, sync, conflict):
        self.goTo("conflict", False)
        self.sm.get_screen(self.sm.current).setSync(sync, conflict)

    def reset(self):
        self.sm.transition = NoTransition()
        self.sm.current = "main"

