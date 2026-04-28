import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from datetime import datetime
import csv
import os
from typing import Optional, List

from jarat import Jarat
from jaratok import BelfoldiJarat, NemzetkoziJarat
from jegyfoglalas import JegyFoglalas
from legitarsasag import LegiTarsasag
# from foglalas_app import RepulojegyApp


# Gui és csicsa
class RepulojegyApp:
    def __init__(self, tk_root: tk.Tk, tarsasag: LegiTarsasag):
        self.root = tk_root
        self.tarsasag = tarsasag
        self.root.title(f"{self.tarsasag.nev} - Foglalási Rendszer")
        self.root.geometry("600x600")
        self.root.protocol("WM_DELETE_WINDOW", self.kilepes_es_mentes)

        # Példányváltozók deklarálása a warningok elkerüléséhez
        # pyCharm hiszti
        self.datum_szuro: Optional[ttk.Combobox] = None
        self.jarat_listbox: Optional[tk.Listbox] = None
        self.utas_nev_entry: Optional[tk.Entry] = None
        self.foglalas_listbox: Optional[tk.Listbox] = None
        self.szurt_jaratok: List[Jarat] = []

        self.gui_felepitese()
        self.lista_frissitese()

    def gui_felepitese(self):
        menu_bar = tk.Frame(self.root)
        menu_bar.pack(fill="x", padx=10, pady=5)
        tk.Button(menu_bar, text="💾 Adatok mentése", command=self.manualis_mentes, bg="#e1e1e1").pack(side="right")

        szuro_frame = tk.LabelFrame(self.root, text="Járat keresése dátum szerint")
        szuro_frame.pack(fill="x", padx=10, pady=5)
        self.datum_szuro = ttk.Combobox(szuro_frame, state="readonly")
        self.datum_szuro.pack(side="left", padx=5, pady=5)
        # Az event paraméter használaton kívüliségét aláhúzással jelezzük
        self.datum_szuro.bind("<<ComboboxSelected>>", self.jaratok_szurese)

        jarat_frame = tk.LabelFrame(self.root, text="Elérhető járatok")
        jarat_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.jarat_listbox = tk.Listbox(jarat_frame)
        self.jarat_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        foglalas_frame = tk.Frame(self.root)
        foglalas_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(foglalas_frame, text="Utas neve:").pack(side="left")
        self.utas_nev_entry = tk.Entry(foglalas_frame)
        self.utas_nev_entry.pack(side="left", padx=5, fill="x", expand=True)
        tk.Button(foglalas_frame, text="Jegy foglalása", command=self.jegy_foglalasa, bg="#d4edda").pack(side="left",
                                                                                                         padx=5)

        lista_frame = tk.LabelFrame(self.root, text="Aktuális foglalások")
        lista_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.foglalas_listbox = tk.Listbox(lista_frame)
        self.foglalas_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Button(self.root, text="Kiválasztott foglalás lemondása", command=self.foglalas_lemondasa, fg="red").pack(
            pady=5)

    def lista_frissitese(self):
        if self.datum_szuro and self.foglalas_listbox:
            datumok = sorted(list(set([j.datum for j in self.tarsasag.jaratok])))
            self.datum_szuro['values'] = ["Összes"] + datumok
            if not self.datum_szuro.get(): self.datum_szuro.current(0)
            self.jaratok_szurese()

            self.foglalas_listbox.delete(0, tk.END)
            for f in self.tarsasag.foglalasok:
                self.foglalas_listbox.insert(tk.END,
                                             f"[{f.foglalas_id}] {f.utas_neve} - {f.jarat.jaratszam} ({f.jarat.datum})")

    def jaratok_szurese(self, _event=None):
        if self.jarat_listbox and self.datum_szuro:
            self.jarat_listbox.delete(0, tk.END)
            szuro = self.datum_szuro.get()
            self.szurt_jaratok = [j for j in self.tarsasag.jaratok if szuro == "Összes" or j.datum == szuro]
            for j in self.szurt_jaratok:
                self.jarat_listbox.insert(tk.END, str(j))

    def jegy_foglalasa(self):
        if not self.jarat_listbox or not self.utas_nev_entry: return
        try:
            idx = self.jarat_listbox.curselection()
            nev = self.utas_nev_entry.get().strip()
            if not idx: raise ValueError("Válassz járatot!")
            if not nev: raise ValueError("Add meg a nevedet!")

            jarat: Jarat = self.szurt_jaratok[idx[0]]
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
        if not self.foglalas_listbox: return
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
        mentes_csv_be(self.tarsasag)
        self.root.destroy()

# Adatkezelés
CSV_FILE = "jaratok.csv"

def mentes_csv_be(tarsasag: LegiTarsasag):
    try:
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Tipus", "ID", "Jaratszam", "Honnan", "Hova", "Tavolsag", "Datum", "Idopont", "Jegyar", "Utas"])
            writer.writerow(["Legitarsasag", tarsasag.nev, "", "", "", "", "", "", "", ""])
            for j in tarsasag.jaratok:
                tipus = "Jarat_B" if isinstance(j, BelfoldiJarat) else "Jarat_N"
                writer.writerow(
                    [tipus, "", j.jaratszam, j.honnan, j.hova, j.tavolsag, j.datum, j.idopont, j.jegyar, ""])
            for f_obj in tarsasag.foglalasok:
                writer.writerow(
                    ["Foglalas", f_obj.foglalas_id, f_obj.jarat.jaratszam, "", "", "", "", "", "", f_obj.utas_neve])
    except Exception as e:
        print(f"Hiba a mentés során: {e}")


def adatok_betoltese() -> LegiTarsasag:
    # Ha nincs CSV file legyen valami adat
    if not os.path.exists(CSV_FILE):
        t = LegiTarsasag("WizzAir")
        j1 = BelfoldiJarat("W6-101", "Budapest", "Debrecen", 200, "2026-10-10", "10:00", 15000)
        j2 = NemzetkoziJarat("W6-202", "Budapest", "London", 1500, "2026-11-12", "14:30", 45000)
        t.jarat_hozzaadasa(j1)
        t.jarat_hozzaadasa(j2)
        t.foglalas_hozzaadasa(JegyFoglalas("F1", j1, "Kovács Péter"))
        mentes_csv_be(t)
        return t

    tarsasag: Optional[LegiTarsasag] = None
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            temp_jaratok = {}
            for row in reader:
                if row["Tipus"] == "Legitarsasag":
                    tarsasag = LegiTarsasag(row["ID"])
                elif row["Tipus"] in ["Jarat_B", "Jarat_N"] and tarsasag is not None:
                    cls = BelfoldiJarat if row["Tipus"] == "Jarat_B" else NemzetkoziJarat
                    j = cls(row["Jaratszam"], row["Honnan"], row["Hova"], int(row["Tavolsag"]), row["Datum"],
                            row["Idopont"], int(row["Jegyar"]))
                    tarsasag.jarat_hozzaadasa(j)
                    temp_jaratok[j.jaratszam] = j
                elif row["Tipus"] == "Foglalas" and tarsasag is not None:
                    jarat = temp_jaratok.get(row["Jaratszam"])
                    if jarat:
                        tarsasag.foglalas_hozzaadasa(JegyFoglalas(row["ID"], jarat, row["Utas"]))
    except Exception as e:
        print(f"Betöltési hiba: {e}")

    return tarsasag if tarsasag is not None else LegiTarsasag("Ismeretlen")


def main():
    adatok = adatok_betoltese()
    main_root = tk.Tk()
    app = RepulojegyApp(main_root, adatok)
    main_root.mainloop()


if __name__ == "__main__":
    main()
