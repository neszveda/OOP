from abc import ABC, abstractmethod
from datetime import datetime

# Járat absztrakt
class Jarat(ABC):
    def __init__(self, jaratszam: str, honnan: str, hova: str, tavolsag: int, datum: str, idopont: str, jegyar: int):
        self.__jaratszam = jaratszam
        self.__honnan = honnan
        self.__hova = hova
        self.__tavolsag = tavolsag
#        self.__datum = datum
#        self.__idopont = idopont
#        self.__jegyar = jegyar

        # A közvetlen értékadás helyett a settereket hívjuk meg, így lefut a validáció
        self.datum = datum
        self.idopont = idopont
        self.jegyar = jegyar

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

    @jegyar.setter
    def jegyar(self, uj_ar: int):
        if uj_ar <= 0:
            raise ValueError("A jegyár csak pozitív szám lehet!")
        self.__jegyar = uj_ar

    @datum.setter
    def datum(self, uj_datum: str):
        try:
            # Csak akkor engedi beállítani, ha a formátum helyes
            datetime.strptime(uj_datum, "%Y-%m-%d")
            self.__datum = uj_datum
        except ValueError:
            raise ValueError("A dátum formátuma érvénytelen! Helyes formátum: ÉÉÉÉ-HH-NN")

    @idopont.setter
    def idopont(self, uj_idopont: str):
        try:
            datetime.strptime(uj_idopont, "%H:%M")
            self.__idopont = uj_idopont
        except ValueError:
            raise ValueError("Az időpont formátuma érvénytelen! Helyes formátum: ÓÓ:PP")

    @abstractmethod
    def __str__(self) -> str:
        return f"{self.__jaratszam}: {self.__honnan} -> {self.__hova} | {self.__datum} {self.__idopont} | {self.__jegyar} HUF"
