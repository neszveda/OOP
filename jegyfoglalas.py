# jegyek foglalása

class JegyFoglalas:
    def __init__(self, foglalas_id: str, jarat: Jarat, utas_neve: str):
        self.__foglalas_id = foglalas_id
        self.__jarat = jarat
        self.__utas_neve = utas_neve

    @property
    def foglalas_id(self) -> str: return self.__foglalas_id

    @property
    def jarat(self) -> Jarat: return self.__jarat

    @property
    def utas_neve(self) -> str: return self.__utas_neve

