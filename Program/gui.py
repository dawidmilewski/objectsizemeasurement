import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2

class WidokAplikacji(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Pomiar Wizyjny - Praca Inżynierska")
        self.geometry("1400x850")
        self.minsize(1000, 650)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.on_usun = None 
        self.on_szczegoly = None
        
        # Zmienne do nawigacji (Zoom & Pan)
        self.base_image = None
        self.tk_image = None
        self.min_scale = 1.0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_data = {"x": 0, "y": 0}

        self._buduj_interfejs()
        self._podepnij_skroty()

    def _buduj_interfejs(self):
        self.panel_lewy = ctk.CTkFrame(self, width=380, corner_radius=0)
        self.panel_lewy.pack(side="left", fill="y", padx=10, pady=10)
        self.panel_lewy.pack_propagate(False)

        ctk.CTkLabel(self.panel_lewy, text="1. Kalibracja", font=("Arial", 15, "bold")).pack(pady=(15, 5))
        self.btn_wczytaj = ctk.CTkButton(self.panel_lewy, text="Wczytaj Obraz")
        self.btn_wczytaj.pack(pady=5, fill="x", padx=20)

        ctk.CTkLabel(self.panel_lewy, text="Fizyczny rozmiar znacznika [cm]:").pack(pady=(10, 0))
        self.pole_rozmiar_aruco = ctk.CTkEntry(self.panel_lewy, justify="center")
        self.pole_rozmiar_aruco.insert(0, "5.0")
        self.pole_rozmiar_aruco.pack(pady=5, fill="x", padx=20)

        ctk.CTkLabel(self.panel_lewy, text="2. Analiza Obrazu", font=("Arial", 15, "bold")).pack(pady=(20, 5))
        self.btn_detekcja = ctk.CTkButton(self.panel_lewy, text="Rozpocznij Wykrywanie", state="disabled")
        self.btn_detekcja.pack(pady=5, fill="x", padx=20)

        ctk.CTkLabel(self.panel_lewy, text="3. Wyniki i Wykresy", font=("Arial", 15, "bold")).pack(pady=(20, 5))
        self.btn_wykres = ctk.CTkButton(self.panel_lewy, text="Pokaż Interaktywny Wykres 2D", state="disabled")
        self.btn_wykres.pack(pady=5, fill="x", padx=20)

        self.ramka_wynikow = ctk.CTkScrollableFrame(self.panel_lewy, height=350)
        self.ramka_wynikow.pack(pady=10, padx=20, fill="both", expand=True)

        self.panel_obrazu = ctk.CTkFrame(self)
        self.panel_obrazu.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.panel_obrazu, bg="#212121", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Podpięcie przesuwania (przesuwanie zadziała tylko po przybliżeniu)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def _podepnij_skroty(self):
        # Skróty klawiszowe do przybliżania/oddalania (Ctrl/Cmd +/-)
        self.bind_all("<Control-plus>", self.zoom_in)
        self.bind_all("<Control-equal>", self.zoom_in)
        self.bind_all("<Command-plus>", self.zoom_in)
        self.bind_all("<Command-equal>", self.zoom_in)

        self.bind_all("<Control-minus>", self.zoom_out)
        self.bind_all("<Command-minus>", self.zoom_out)

    def wyczysc_wyniki(self):
        for widget in self.ramka_wynikow.winfo_children():
            widget.destroy()

    def dodaj_kafelek_wyniku(self, wymiary, indeks):
        ramka = ctk.CTkFrame(self.ramka_wynikow)
        ramka.pack(fill="x", pady=5)
        
        tekst = f"Obiekt {indeks}\nDługość: {wymiary[0]:.2f} cm\nSzerokość: {wymiary[1]:.2f} cm"
        ctk.CTkLabel(ramka, text=tekst, justify="left").pack(side="left", padx=10, pady=5)
        
        btn_usun = ctk.CTkButton(
            ramka, text="X", width=30, fg_color="#8B0000", hover_color="#5A0000",
            command=lambda idx=indeks-1: self.on_usun(idx) if self.on_usun else None
        )
        btn_usun.pack(side="right", padx=5)

        btn_szczegoly = ctk.CTkButton(
            ramka, text="Szczegóły", width=60,
            command=lambda idx=indeks-1: self.on_szczegoly(idx) if self.on_szczegoly else None
        )
        btn_szczegoly.pack(side="right", padx=5)

    def pobierz_rozmiar_aruco(self):
        return self.pole_rozmiar_aruco.get().strip().replace(",", ".")

    def ustaw_stan_przyciskow(self, detekcja=None, wykres=None, wczytaj=None, tekst_detekcji=None):
        if detekcja is not None: self.btn_detekcja.configure(state=detekcja)
        if wykres is not None: self.btn_wykres.configure(state=wykres)
        if wczytaj is not None: self.btn_wczytaj.configure(state=wczytaj)
        if tekst_detekcji is not None: self.btn_detekcja.configure(text=tekst_detekcji)

    # zoom i pan
    def aktualizuj_podglad(self, obraz_bgr):
        obraz_rgb = cv2.cvtColor(obraz_bgr, cv2.COLOR_BGR2RGB)
        self.base_image = Image.fromarray(obraz_rgb)
        
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()
        if c_width <= 1: c_width = 800
        if c_height <= 1: c_height = 600
        
        skala_w = c_width / self.base_image.width
        skala_h = c_height / self.base_image.height
        
        self.min_scale = min(skala_w, skala_h)
        self.scale = self.min_scale
        
        self._wycentruj_obraz(c_width, c_height)
        self.redraw_image()

    def _wycentruj_obraz(self, c_width, c_height):
        self.offset_x = (c_width - (self.base_image.width * self.scale)) / 2
        self.offset_y = (c_height - (self.base_image.height * self.scale)) / 2

    def redraw_image(self):
        if self.base_image is None: return
        nowa_szer = int(self.base_image.width * self.scale)
        nowa_wys = int(self.base_image.height * self.scale)
        
        if nowa_szer < 10 or nowa_wys < 10: return
        
        img_resized = self.base_image.resize((nowa_szer, nowa_wys), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img_resized)
        
        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, anchor="nw", image=self.tk_image)

    def on_press(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        # Przesuwanie możliwe TYLKO gdy obraz jest przybliżony
        if self.base_image is None or self.scale <= self.min_scale + 0.01:
            return 
            
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.offset_x += dx
        self.offset_y += dy
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.redraw_image()

    def zoom_in(self, event):
        if self.base_image is None: return
        zoom_factor = 1.2
        self._zastosuj_zoom(zoom_factor)

    def zoom_out(self, event):
        if self.base_image is None: return
        zoom_factor = 1.0 / 1.2
        self._zastosuj_zoom(zoom_factor)

    def _zastosuj_zoom(self, zoom_factor):
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()
        
        mouseX = c_width / 2
        mouseY = c_height / 2

        nowa_skala = self.scale * zoom_factor
        
        # Blokada przed oddaleniem bardziej niż rozmiar okna
        if nowa_skala < self.min_scale:
            self.scale = self.min_scale
            self._wycentruj_obraz(c_width, c_height)
        else:
            self.offset_x = mouseX - zoom_factor * (mouseX - self.offset_x)
            self.offset_y = mouseY - zoom_factor * (mouseY - self.offset_y)
            self.scale = nowa_skala
            
        self.redraw_image()