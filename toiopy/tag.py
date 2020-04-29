class TagHandler:
    def __init__(self):
        self._tag = 0

    def current(self) -> int:
        return self._tag

    def next(self) -> int:
        self._tag = (self._tag + 1) % 256
        return self._tag


def createTagHandler():
    return TagHandler()
