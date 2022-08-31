from abc import ABC, abstractmethod


class Instrument(ABC):
    @abstractmethod
    def analysis(self):
        pass

    @abstractmethod
    def enter_long(self):
        pass

    @abstractmethod
    def enter_short(self):
        pass

    @abstractmethod
    def exit_long(self):
        pass

    @abstractmethod
    def exit_short(self):
        pass


class InstumentContructor(ABC):
    @staticmethod
    @abstractmethod
    def construct(name):
        return Instrument()

    @staticmethod
    @abstractmethod
    def deconstruct(name):
        pass
