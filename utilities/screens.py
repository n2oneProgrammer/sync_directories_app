class ScreensUtilities:

    __instance = None

    @staticmethod
    def getInstance(sm=None):
        if ScreensUtilities.__instance == None:
            ScreensUtilities(sm=sm)
        return ScreensUtilities.__instance

    def __init__(self, sm=None):

        if ScreensUtilities.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            if sm:
                self.sm = sm
            ScreensUtilities.__instance = self

    def goTo(self, screen, right):
        if right:
            self.sm.transition.direction = "right"
        else:
            self.sm.transition.direction = "left"

        self.sm.current = screen

    def goToSync(self, sync, right = False):
        self.goTo("sync", right)
        self.sm.get_screen(self.sm.current).setSync(sync)

    def goToConfilct(self, sync, conflict):
        self.goTo("conflict", False)
        self.sm.get_screen(self.sm.current).setSync(sync, conflict)
