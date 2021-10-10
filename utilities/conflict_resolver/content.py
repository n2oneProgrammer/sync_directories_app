class Content:
    def __init__(self, text, is_deleted=False, is_binary=False, path=""):
        self.text = text
        self.is_deleted = is_deleted
        self.is_binary = is_binary
        self.path = path

    def get_content(self):
        return "".join(self.text)
