import cv2
import numpy as np
from core_math import przelicz_punkty, oblicz_dlugosc_boku

def oblicz_wymiary_obiektu(H, hull_px):
    # Rzutowanie surowej otoczki wypukłej na centymetry
    punkty_px = hull_px.reshape(-1, 2)
    hull_cm = przelicz_punkty(H, punkty_px)
    
    # Sztuczny prostokąt zamykający kształt (minAreaRect)
    prostokat_cm = cv2.minAreaRect(np.float32(hull_cm))
    rogi_prostokata_cm = cv2.boxPoints(prostokat_cm)
    
    # wyliczamy 4-kąt aproksymujący do analizy w "Szczegółach" i na wykresie
    obwod = cv2.arcLength(np.float32(hull_cm), True)
    uproszczony_czworokat_cm = None
    
    # Przeszukujemy szerszy zakres eps, aby ZAWSZE znaleźć 4 wierzchołki, nawet dla kluczyka
    for eps in np.linspace(0.005, 0.3, 300):
        approx = cv2.approxPolyDP(np.float32(hull_cm), eps * obwod, True)
        if len(approx) == 4:
            uproszczony_czworokat_cm = approx.reshape(4, 2)
            break

    # Jeśli z jakiegoś powodu approxPolyDP zawiedzie i zwróci np trójkąt, używamy rogi_prostokata_cm
    if uproszczony_czworokat_cm is None:
        uproszczony_czworokat_cm = rogi_prostokata_cm

    # Zawsze obliczamy 4 boki tego czworokąta do panelu "Szczegóły"
    p0, p1, p2, p3 = uproszczony_czworokat_cm
    boki_szczegoly = [
        oblicz_dlugosc_boku(p0, p1),
        oblicz_dlugosc_boku(p1, p2),
        oblicz_dlugosc_boku(p2, p3),
        oblicz_dlugosc_boku(p3, p0)
    ]

    pole_otoczki = cv2.contourArea(np.float32(hull_cm))
    pole_czworokata = cv2.contourArea(np.float32(uproszczony_czworokat_cm))
    
    # Warunek 90% (ochrona przed okręgami i przedmiotami o nieregularnym ksztalcie)
    if pole_otoczki > 0 and (pole_czworokata / pole_otoczki) >= 0.90:
        # Prawdziwy czworokąt -> wymiary z jego średnich boków
        wymiar_a = (boki_szczegoly[0] + boki_szczegoly[2]) / 2.0
        wymiar_b = (boki_szczegoly[1] + boki_szczegoly[3]) / 2.0
        dlugosc = max(wymiar_a, wymiar_b)
        szerokosc = min(wymiar_a, wymiar_b)
        metoda_pomiaru = "czworokat"
    else:
        # Niestandardowy kształt (moneta, kluczyk) -> wymiary z minAreaRect
        (cx, cy), (bok_a, bok_b), kat = prostokat_cm
        dlugosc = max(bok_a, bok_b)
        szerokosc = min(bok_a, bok_b)
        metoda_pomiaru = "minAreaRect"

    # Odwrotne rzutowanie z powrotem na piksele (Tylko 2 warstwy)
    H_inv = np.linalg.inv(H)
    rogi_prostokata_px = przelicz_punkty(H_inv, rogi_prostokata_cm)
    czworokat_px = przelicz_punkty(H_inv, uproszczony_czworokat_cm)
    
    return rogi_prostokata_px, czworokat_px, rogi_prostokata_cm, dlugosc, szerokosc, uproszczony_czworokat_cm, hull_cm, boki_szczegoly, metoda_pomiaru