import cv2
import numpy as np
from core_math import wylicz_macierz, oblicz_dlugosc_boku

def znajdz_aruco(obraz, bok_cm=5.0):
    slownik = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
    parametry = cv2.aruco.DetectorParameters()
    
    parametry.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    
    detektor = cv2.aruco.ArucoDetector(slownik, parametry)
    
    rogi, ids, _ = detektor.detectMarkers(obraz)
    if ids is None or len(ids) == 0:
        return None, None

    punkty_aruco = rogi[0][0]
    punkty_cm = np.array([
        [0.0, 0.0], 
        [bok_cm, 0.0], 
        [bok_cm, bok_cm], 
        [0.0, bok_cm]
    ], dtype=np.float32)
    
    macierz = wylicz_macierz(punkty_aruco, punkty_cm)
    return punkty_aruco, macierz

def wykryj_kontury(obraz, punkty_aruco):
    wysokosc_obr, szerokosc_obr = obraz.shape[:2]
    szary = cv2.cvtColor(obraz, cv2.COLOR_BGR2GRAY)
    rozmycie = cv2.GaussianBlur(szary, (7, 7), 0)
    
    binarne = cv2.adaptiveThreshold(
        rozmycie, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 21, 5
    )
    
    if punkty_aruco is not None:
        srodek_aruco = np.mean(punkty_aruco, axis=0)
        wektory = punkty_aruco - srodek_aruco
        aruco_maska = (srodek_aruco + wektory * 1.5).astype(np.int32)
        cv2.fillPoly(binarne, [aruco_maska], 0)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    zamkniete = cv2.morphologyEx(binarne, cv2.MORPH_CLOSE, kernel, iterations=2)
    kontury, _ = cv2.findContours(zamkniete, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    prawidlowe_obiekty = []
    srodek_aruco = np.mean(punkty_aruco, axis=0) if punkty_aruco is not None else np.array([-1000, -1000])

    for cnt in kontury:
        pole = cv2.contourArea(cnt)
        if pole < 500 or pole > (wysokosc_obr * szerokosc_obr * 0.85):
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        margines = 10
        if x < margines or y < margines or (x + w) > (szerokosc_obr - margines) or (y + h) > (wysokosc_obr - margines):
            continue
            
        srodek_obj = np.mean(cnt.reshape(-1, 2), axis=0)
        if oblicz_dlugosc_boku(srodek_obj, srodek_aruco) < 100:
            continue
            
        hull = cv2.convexHull(cnt)
        prawidlowe_obiekty.append({"hull_px": hull})

    return prawidlowe_obiekty