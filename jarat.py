from abc import ABC, abstractmethod
from datetime import datetime

# Járat absztrakt
class Jarat(ABC):
    def __init__(self, jaratszam: str, honnan: str, hova: str, tavolsag: int, datum: str, idopont: str, jegyar: int):
        self.__jaratszam = jaratszam
        self.__honnan = honnan
        self.__hova = hova
        self.__tavolsag = tavolsag
        self.__datum = datum
        self.__idopont = idopont
        self.__jegyar = jegyar

    @property
    def jaratszam(self) -> str: return self.__jaratszam

    @property
    def honnan(self) -> str: return self.__honnan

    @property
    def hova(self) -> str: return self.__hova

    @property
    def tavolsag(self) -> int: return self.__tavolsag

    @property
    def datum(self) -> str: return self.__datum

    @property
    def idopont(self) -> str: return self.__idopont

    @property
    def jegyar(self) -> int: return self.__jegyar

    @property
    def indulas_ideje(self) -> datetime:
        return datetime.strptime(f"{self.__datum} {self.__idopont}", "%Y-%m-%d %H:%M")

    @abstractmethod
    def __str__(self) -> str:
        return f"{self.__jaratszam}: {self.__honnan} -> {self.__hova} | {self.__datum} {self.__idopont} | {self.__jegyar} HUF"
