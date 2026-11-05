import cv2
import numpy as np
import matplotlib.pyplot as plt
import threading
import queue
import traceback
import customtkinter as ctk
from tkinter import filedialog, messagebox

from gui import WidokAplikacji
from vision import znajdz_aruco, wykryj_kontury
from measurement import oblicz_wymiary_obiektu

MAX_IMAGE_SIDE = 3200

class KontrolerPomiaru:
    def __init__(self):
        self.widok = WidokAplikacji()
        self.widok.btn_wczytaj.configure(command=self.akcja_wczytaj)
        self.widok.btn_detekcja.configure(command=self.akcja_wykrywaj)
        self.widok.btn_wykres.configure(command=self.akcja_wykres)
        
        self.widok.on_usun = self.usun_obiekt
        self.widok.on_szczegoly = self.akcja_szczegoly

        self.obraz_oryginalny = None
        self.punkty_aruco = None
        self.macierz_cm = None
        self.lista_obiektow = []
        self.rozmiar_aruco_cm = 5.0
        
        self._analiza_w_toku = False
        self._kolejka_wynikow = queue.Queue()
        self.widok.after(100, self._sprawdz_kolejke)

    def uruchom(self):
        self.widok.mainloop()

    def odswiez_widok(self):
        if self.obraz_oryginalny is None: return
        podglad = self.obraz_oryginalny.copy()

        if self.punkty_aruco is not None:
            marker = np.asarray(self.punkty_aruco, dtype=np.int32).reshape(4, 2)
            cv2.polylines(podglad, [marker], True, (255, 0, 0), 2, lineType=cv2.LINE_AA)
            cv2.putText(podglad, "ArUco", tuple(marker[3]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)

        self.widok.wyczysc_wyniki()

        for i, obj in enumerate(self.lista_obiektow):
            # Czerwony obrys (surowa otoczka wypukła w pikselach z detekcji)
            surowy_hull = np.asarray(obj.get("surowy_hull_px", []), dtype=np.int32).reshape(-1, 2)
            if len(surowy_hull) > 0:
                cv2.polylines(podglad, [surowy_hull], True, (0, 0, 255), 3, lineType=cv2.LINE_AA)

            # Jedna Zielona ramka obrazująca docelowy kształt
            if obj["metoda"] == "czworokat":
                wielokat = np.asarray(obj["czworokat_px"], dtype=np.int32).reshape(-1, 2)
            else:
                wielokat = np.asarray(obj["rogi_prostokata_px"], dtype=np.int32).reshape(-1, 2)
                
            cv2.polylines(podglad, [wielokat], True, (0, 255, 0), 2, lineType=cv2.LINE_AA)
            
            sx, sy = np.mean(wielokat, axis=0)
            cv2.putText(podglad, f"O {i+1}", (int(sx), int(sy)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, lineType=cv2.LINE_AA)
            cv2.putText(podglad, f"O {i+1}", (int(sx), int(sy)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, lineType=cv2.LINE_AA)

            self.widok.dodaj_kafelek_wyniku([obj["dlugosc_cm"], obj["szerokosc_cm"]], i + 1)

        self.widok.aktualizuj_podglad(podglad)
        self.widok.ustaw_stan_przyciskow(wykres="normal" if self.lista_obiektow else "disabled")

    def usun_obiekt(self, indeks):
        if 0 <= indeks < len(self.lista_obiektow):
            self.lista_obiektow.pop(indeks)
            self.odswiez_widok()

    def akcja_szczegoly(self, indeks):
        if 0 <= indeks < len(self.lista_obiektow):
            obj = self.lista_obiektow[indeks]
            okno = ctk.CTkToplevel(self.widok)
            okno.title(f"Szczegóły - Obiekt {indeks + 1}")
            okno.geometry("400x300")
            okno.attributes('-topmost', 'true')

            ctk.CTkLabel(okno, text=f"Analiza Geometrii - Obiekt {indeks + 1}", font=("Arial", 16, "bold")).pack(pady=10)
            
            metoda_tekst = "Uśredniony czworokąt (wymiar pokrywa >90% kształtu)" if obj["metoda"] == "czworokat" else "minAreaRect (kształt nieregularny, obwiednia)"
            ctk.CTkLabel(okno, text=f"Metoda pomiaru globalnego:\n{metoda_tekst}", font=("Arial", 12, "italic")).pack(pady=5)
            
            ctk.CTkLabel(okno, text="Długości krawędzi:", text_color="orange", font=("Arial", 14)).pack(pady=10)
            
            ramka_bokow = ctk.CTkScrollableFrame(okno, height=120)
            ramka_bokow.pack(fill="both", expand=True, padx=20, pady=10)
            
            for j, bok in enumerate(obj["boki_otoczki_cm"]):
                ctk.CTkLabel(ramka_bokow, text=f"Bok {j+1}: {bok:.2f} cm").pack(anchor="w", pady=2)

    def akcja_wczytaj(self):
        if self._analiza_w_toku: return
        sciezka = filedialog.askopenfilename(filetypes=[("Pliki obrazów", "*.png *.jpg *.jpeg *.bmp"), ("Wszystkie pliki", "*.*")])
        if not sciezka: return

        obraz = cv2.imread(sciezka)
        if obraz is None: return

        h, w = obraz.shape[:2]
        najdluzszy_bok = max(h, w)
        if najdluzszy_bok > MAX_IMAGE_SIDE:
            skala = MAX_IMAGE_SIDE / float(najdluzszy_bok)
            obraz = cv2.resize(obraz, (max(1, int(round(w * skala))), max(1, int(round(h * skala)))), interpolation=cv2.INTER_AREA)

        self.obraz_oryginalny = obraz
        self.lista_obiektow = []
        try:
            self.punkty_aruco, _ = znajdz_aruco(self.obraz_oryginalny, 5.0)
        except Exception as exc:
            self.punkty_aruco = None
            messagebox.showerror("Błąd ArUco", str(exc))

        if self.punkty_aruco is None:
            self.widok.ustaw_stan_przyciskow(detekcja="disabled", wykres="disabled")
            self.widok.aktualizuj_podglad(self.obraz_oryginalny)
            return

        self.widok.ustaw_stan_przyciskow(detekcja="normal", wykres="disabled")
        self.odswiez_widok()

    def akcja_wykrywaj(self):
        if self.obraz_oryginalny is None or self._analiza_w_toku: return
        try: bok_cm = float(self.widok.pobierz_rozmiar_aruco())
        except ValueError: return
        
        self._analiza_w_toku = True
        self.widok.ustaw_stan_przyciskow(detekcja="disabled", wczytaj="disabled", tekst_detekcji="Analizowanie...")
        threading.Thread(target=self._wykonaj_analize, args=(self.obraz_oryginalny.copy(), bok_cm), daemon=True).start()

    def _wykonaj_analize(self, obraz, bok_cm):
        try:
            punkty_aruco, H = znajdz_aruco(obraz, bok_cm)
            obiekty = wykryj_kontury(obraz, punkty_aruco)
            wyniki = []

            for obiekt in obiekty:
                rogi_prostokata_px, czworokat_px, prostokat_cm, dl, szer, czworokat_cm, pelny_hull_cm, boki_szczegoly, metoda = oblicz_wymiary_obiektu(H, obiekt["hull_px"])
                
                wyniki.append({
                    "surowy_hull_px": obiekt["hull_px"],
                    "rogi_prostokata_px": rogi_prostokata_px,
                    "czworokat_px": czworokat_px,
                    "prostokat_cm": prostokat_cm,      
                    "dlugosc_cm": dl,
                    "szerokosc_cm": szer,
                    "czworokat_cm": czworokat_cm,
                    "pelny_hull_cm": pelny_hull_cm, 
                    "boki_otoczki_cm": boki_szczegoly,
                    "metoda": metoda
                })

            self._kolejka_wynikow.put(("ok", punkty_aruco, H, wyniki, bok_cm))
        except Exception as exc:
            self._kolejka_wynikow.put(("error", str(exc), traceback.format_exc()))

    def _sprawdz_kolejke(self):
        try: wynik = self._kolejka_wynikow.get_nowait()
        except queue.Empty: wynik = None

        if wynik is not None:
            self._analiza_w_toku = False
            self.widok.ustaw_stan_przyciskow(detekcja="normal", wczytaj="normal", tekst_detekcji="Rozpocznij Wykrywanie")
            if wynik[0] == "error":
                messagebox.showerror("Błąd", wynik[1])
            else:
                _, self.punkty_aruco, self.macierz_cm, self.lista_obiektow, self.rozmiar_aruco_cm = wynik
                self.odswiez_widok()
        self.widok.after(100, self._sprawdz_kolejke)

    def akcja_wykres(self):
        if not self.lista_obiektow: return
        plt.figure("Wizualizacja Wymiarów 2D", figsize=(10, 8))
        plt.clf()
        plt.title("Analiza Zrzutowanych Kształtów (Wykres Warstwowy)")
        
        bok = self.rozmiar_aruco_cm
        plt.plot([0, bok, bok, 0, 0], [bok, bok, 0, 0, bok], "b--", linewidth=2, label="ArUco")

        kolory = ["r", "g", "c", "m", "y"]
        for i, obiekt in enumerate(self.lista_obiektow):
            kolor = kolory[i % len(kolory)]
            
            # Wizualizacja nr1 Pełna zrzutowana otoczka -> Cienka kropkowana linia
            hull = np.asarray(obiekt["pelny_hull_cm"], dtype=np.float64)
            hx = list(hull[:, 0]) + [hull[0, 0]]
            hy = list(hull[:, 1]) + [hull[0, 1]]
            plt.plot(hx, hy, f"{kolor}:", linewidth=2, label=f"O{i + 1} Pełna Otoczka")

            # Wizualizacja nr2 Aproksymowany czworokąt -> Gruba ciągła linia
            czw = np.asarray(obiekt["czworokat_cm"], dtype=np.float64)
            cx = list(czw[:, 0]) + [czw[0, 0]]
            cy = list(czw[:, 1]) + [czw[0, 1]]
            plt.plot(cx, cy, f"{kolor}-", linewidth=3, alpha=0.8, label=f"O{i + 1} Czworokąt")
            
            # Wizualizacja nr3 Sztuczny prostokąt minAreaRect -> Cienka przerywana linia
            rect = np.asarray(obiekt["prostokat_cm"], dtype=np.float64).reshape(4, 2)
            rx = list(rect[:, 0]) + [rect[0, 0]]
            ry = list(rect[:, 1]) + [rect[0, 1]]
            plt.plot(rx, ry, f"{kolor}--", linewidth=1, alpha=0.6, label=f"O{i + 1} minAreaRect")

        plt.grid(True, linestyle=":")
        plt.axis("equal")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
        
        plt.xlabel("Oś X [cm]")
        plt.ylabel("Oś Y [cm]")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    aplikacja = KontrolerPomiaru()
    aplikacja.uruchom()