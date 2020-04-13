class TagHandler:
    def __init__(self):
        self.__tag = 0

    def current(self) -> int:
        return self.__tag

    def next(self) -> int:
        self.__tag = (self.__tag + 1) % 256
        return self.__tag


def createTagHandler():
    return TagHandler()
