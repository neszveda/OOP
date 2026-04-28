class LegiTarsasag:
    def __init__(self, nev: str):
        self.__nev = nev
        self.__jaratok: List[Jarat] = []
        self.__foglalasok: List[JegyFoglalas] = []

    @property
    def nev(self) -> str: return self.__nev

    @property
    def jaratok(self) -> List[Jarat]: return self.__jaratok

    @property
    def foglalasok(self) -> List[JegyFoglalas]: return self.__foglalasok

    def jarat_hozzaadasa(self, jarat: Jarat):
        self.__jaratok.append(jarat)

    def foglalas_hozzaadasa(self, foglalas: JegyFoglalas):
        self.__foglalasok.append(foglalas)

    def foglalas_torlese(self, foglalas_id: str):
        eredeti_hossz = len(self.__foglalasok)
        self.__foglalasok = [f for f in self.__foglalasok if f.foglalas_id != foglalas_id]
        if len(self.__foglalasok) == eredeti_hossz:
            raise ValueError("A megadott foglalás nem található!")
