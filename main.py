import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from datetime import datetime
import csv
import os


# --- 1. BACKEND OSZTÁLYOK ---

class Jarat(ABC):
    def __init__(self, jaratszam, honnan, hova, tavolsag, datum, idopont, jegyar):
        self.__jaratszam = jaratszam
        self.__honnan = honnan
        self.__hova = hova
        self.__tavolsag = tavolsag
        self.__datum = datum
        self.__idopont = idopont
        self.__jegyar = jegyar

    @property
    def jaratszam(self): return self.__jaratszam

    @property
    def honnan(self): return self.__honnan

    @property
    def hova(self): return self.__hova

    @property
    def tavolsag(self): return self.__tavolsag

    @property
    def datum(self): return self.__datum

    @property
    def idopont(self): return self.__idopont

    @property
    def jegyar(self): return self.__jegyar

    @property
    def indulas_ideje(self):
        return datetime.strptime(f"{self.__datum} {self.__idopont}", "%Y-%m-%d %H:%M")

    def __str__(self):
        return f"{self.__jaratszam}: {self.__honnan} -> {self.__hova} | {self.__datum} {self.__idopont} | {self.__jegyar} HUF"


class BelfoldiJarat(Jarat):
    def __init__(self, jaratszam, honnan, hova, tavolsag, datum, idopont, jegyar):
        super().__init__(jaratszam, honnan, hova, tavolsag, datum, idopont, jegyar)


class NemzetkoziJarat(Jarat):
    def __init__(self, jaratszam, honnan, hova, tavolsag, datum, idopont, jegyar):
        super().__init__(jaratszam, honnan, hova, tavolsag, datum, idopont, jegyar)


class JegyFoglalas:
    def __init__(self, foglalas_id, jarat, utas_neve):
        self.__foglalas_id = foglalas_id
        self.__jarat = jarat
        self.__utas_neve = utas_neve

    @property
    def foglalas_id(self): return self.__foglalas_id

    @property
    def jarat(self): return self.__jarat

    @property
    def utas_neve(self): return self.__utas_neve


class LegiTarsasag:
    def __init__(self, nev):
        self.__nev = nev
        self.__jaratok = []
        self.__foglalasok = []

    @property
    def nev(self): return self.__nev

    @property
    def jaratok(self): return self.__jaratok

    @property
    def foglalasok(self): return self.__foglalasok

    def jarat_hozzaadasa(self, jarat):
        self.__jaratok.append(jarat)

    def foglalas_hozzaadasa(self, foglalas):
        self.__foglalasok.append(foglalas)

    def foglalas_torlese(self, foglalas_id):
        eredeti_hossz = len(self.__foglalasok)
        self.__foglalasok = [f for f in self.__foglalasok if f.foglalas_id != foglalas_id]
        if len(self.__foglalasok) == eredeti_hossz:
            raise ValueError("A megadott foglalás nem található!")


# --- 2. ADATKEZELÉS (CSV) ---

CSV_FILE = "jaratok.csv"


def mentes_csv_be(tarsasag):
    try:
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Tipus", "ID", "Jaratszam", "Honnan", "Hova", "Tavolsag", "Datum", "Idopont", "Jegyar", "Utas"])
            # Légitársaság mentése
            writer.writerow(["Legitarsasag", tarsasag.nev, "", "", "", "", "", "", "", ""])
            # Járatok mentése
            for j in tarsasag.jaratok:
                tipus = "Jarat_B" if isinstance(j, BelfoldiJarat) else "Jarat_N"
                writer.writerow(
                    [tipus, "", j.jaratszam, j.honnan, j.hova, j.tavolsag, j.datum, j.idopont, j.jegyar, ""])
            # Foglalások mentése
            for f_obj in tarsasag.foglalasok:
                writer.writerow(
                    ["Foglalas", f_obj.foglalas_id, f_obj.jarat.jaratszam, "", "", "", "", "", "", f_obj.utas_neve])
    except Exception as e:
        print(f"Hiba a mentés során: {e}")


def adatok_betoltese():
    if not os.path.exists(CSV_FILE):
        # Alapértelmezett adatok létrehozása, ha a fájl még nem létezik
        t = LegiTarsasag("WizzAir")
        j1 = BelfoldiJarat("W6-101", "Budapest", "Debrecen", 200, "2026-10-10", "10:00", 15000)
        j2 = NemzetkoziJarat("W6-202", "Budapest", "London", 1500, "2026-11-12", "14:30", 45000)
        j3 = NemzetkoziJarat("W6-303", "Budapest", "Párizs", 1300, "2026-12-01", "08:15", 38000)
        t.jarat_hozzaadasa(j1)
        t.jarat_hozzaadasa(j2)
        t.jarat_hozzaadasa(j3)
        t.foglalas_hozzaadasa(JegyFoglalas("F1", j1, "Kovács Péter"))
        mentes_csv_be(t)
        return t

    tarsasag = None
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            temp_jaratok = {}
            for row in reader:
                if row["Tipus"] == "Legitarsasag":
                    tarsasag = LegiTarsasag(row["ID"])
                elif row["Tipus"] in ["Jarat_B", "Jarat_N"]:
                    cls = BelfoldiJarat if row["Tipus"] == "Jarat_B" else NemzetkoziJarat
                    j = cls(row["Jaratszam"], row["Honnan"], row["Hova"], int(row["Tavolsag"]), row["Datum"],
                            row["Idopont"], int(row["Jegyar"]))
                    tarsasag.jarat_hozzaadasa(j)
                    temp_jaratok[j.jaratszam] = j
                elif row["Tipus"] == "Foglalas":
                    jarat = temp_jaratok.get(row["Jaratszam"])
                    if jarat:
                        tarsasag.foglalas_hozzaadasa(JegyFoglalas(row["ID"], jarat, row["Utas"]))
    except Exception as e:
        print(f"Betöltési hiba: {e}")
    return tarsasag


# --- 3. GUI ---

class RepulojegyApp:
    def __init__(self, root, tarsasag):
        self.root = root
        self.tarsasag = tarsasag
        self.root.title(f"{self.tarsasag.nev} - Foglalási Rendszer")
        self.root.geometry("600x600")

        # Kilépéskori automatikus mentés beállítása
        self.root.protocol("WM_DELETE_WINDOW", self.kilepes_es_mentes)

        self.gui_felepitese()
        self.lista_frissitese()

    def gui_felepitese(self):
        # -- Navigációs/Mentés sáv --
        menu_bar = tk.Frame(self.root)
        menu_bar.pack(fill="x", padx=10, pady=5)
        tk.Button(menu_bar, text="💾 Adatok mentése", command=self.manualis_mentes, bg="#e1e1e1").pack(side="right")

        # -- Szűrés --
        szuro_frame = tk.LabelFrame(self.root, text="Járat keresése dátum szerint")
        szuro_frame.pack(fill="x", padx=10, pady=5)
        self.datum_szuro = ttk.Combobox(szuro_frame, state="readonly")
        self.datum_szuro.pack(side="left", padx=5, pady=5)
        self.datum_szuro.bind("<<ComboboxSelected>>", self.jaratok_szurese)

        # -- Járatok --
        jarat_frame = tk.LabelFrame(self.root, text="Elérhető járatok")
        jarat_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.jarat_listbox = tk.Listbox(jarat_frame)
        self.jarat_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # -- Foglalás --
        foglalas_frame = tk.Frame(self.root)
        foglalas_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(foglalas_frame, text="Utas neve:").pack(side="left")
        self.utas_nev_entry = tk.Entry(foglalas_frame)
        self.utas_nev_entry.pack(side="left", padx=5, fill="x", expand=True)
        tk.Button(foglalas_frame, text="Jegy foglalása", command=self.jegy_foglalasa, bg="#d4edda").pack(side="left",
                                                                                                         padx=5)

        # -- Foglalások --
        lista_frame = tk.LabelFrame(self.root, text="Aktuális foglalások")
        lista_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.foglalas_listbox = tk.Listbox(lista_frame)
        self.foglalas_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Button(self.root, text="Kiválasztott foglalás lemondása", command=self.foglalas_lemondasa, fg="red").pack(
            pady=5)

    def lista_frissitese(self):
        datumok = sorted(list(set([j.datum for j in self.tarsasag.jaratok])))
        self.datum_szuro['values'] = ["Összes"] + datumok
        if not self.datum_szuro.get(): self.datum_szuro.current(0)
        self.jaratok_szurese(None)

        self.foglalas_listbox.delete(0, tk.END)
        for f in self.tarsasag.foglalasok:
            self.foglalas_listbox.insert(tk.END,
                                         f"[{f.foglalas_id}] {f.utas_neve} - {f.jarat.jaratszam} ({f.jarat.datum})")

    def jaratok_szurese(self, event):
        self.jarat_listbox.delete(0, tk.END)
        szuro = self.datum_szuro.get()
        self.szurt_jaratok = [j for j in self.tarsasag.jaratok if szuro == "Összes" or j.datum == szuro]
        for j in self.szurt_jaratok:
            self.jarat_listbox.insert(tk.END, str(j))

    def jegy_foglalasa(self):
        try:
            idx = self.jarat_listbox.curselection()
            nev = self.utas_nev_entry.get().strip()
            if not idx: raise ValueError("Válassz járatot!")
            if not nev: raise ValueError("Add meg a nevedet!")

            jarat = self.szurt_jaratok[idx[0]]
            if jarat.indulas_ideje < datetime.now():
                raise ValueError("Ez a járat már elindult!")

            f_id = f"F{len(self.tarsasag.foglalasok) + 100}"
            self.tarsasag.foglalas_hozzaadasa(JegyFoglalas(f_id, jarat, nev))
            self.lista_frissitese()
            self.utas_nev_entry.delete(0, tk.END)
            messagebox.showinfo("Siker", f"Foglalás mentve! Ár: {jarat.jegyar} HUF")
        except ValueError as e:
            messagebox.showwarning("Figyelem", str(e))

    def foglalas_lemondasa(self):
        try:
            idx = self.foglalas_listbox.curselection()
            if not idx: raise ValueError("Válassz ki egy foglalást!")
            f_szoveg = self.foglalas_listbox.get(idx[0])
            f_id = f_szoveg.split("]")[0][1:]
            self.tarsasag.foglalas_torlese(f_id)
            self.lista_frissitese()
            messagebox.showinfo("Infó", "Foglalás törölve.")
        except ValueError as e:
            messagebox.showwarning("Hiba", str(e))

    def manualis_mentes(self):
        mentes_csv_be(self.tarsasag)
        messagebox.showinfo("Mentés", "Az adatok sikeresen mentve a jaratok.csv fájlba!")

    def kilepes_es_mentes(self):
        # Automatikus mentés bezáráskor
        mentes_csv_be(self.tarsasag)
        self.root.destroy()


if __name__ == "__main__":
    adatok = adatok_betoltese()
    root = tk.Tk()
    app = RepulojegyApp(root, adatok)
    root.mainloop()
