from jarat import Jarat

# belföldi, külföldi járatok
class BelfoldiJarat(Jarat):
    def __str__(self) -> str:
        return f"[Belföldi] " + super().__str__()


class NemzetkoziJarat(Jarat):
    def __str__(self) -> str:
        return f"[Nemzetközi] " + super().__str__()

