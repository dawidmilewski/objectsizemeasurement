import numpy as np

def wylicz_macierz(punkty_piksele, punkty_docelowe):
    A, B = [], []
    for i in range(4):
        u, v = punkty_piksele[i]
        X, Y = punkty_docelowe[i]
        A.extend([
            [u, v, 1, 0, 0, 0, -X*u, -X*v],
            [0, 0, 0, u, v, 1, -Y*u, -Y*v]
        ])
        B.extend([X, Y])
        
    h = np.linalg.solve(np.array(A, dtype=np.float64), np.array(B, dtype=np.float64))
    return np.array([[h[0], h[1], h[2]], [h[3], h[4], h[5]], [h[6], h[7], 1.0]])

def przelicz_punkty(H, punkty_piksele):
    wyniki = []
    for pt in punkty_piksele:
        wektor = np.array([pt[0], pt[1], 1.0])
        przeliczone = np.dot(H, wektor)
        wyniki.append([przeliczone[0] / przeliczone[2], przeliczone[1] / przeliczone[2]])
    return np.array(wyniki, dtype=np.float32)

def oblicz_dlugosc_boku(p1, p2):
    return float(np.linalg.norm(np.array(p1) - np.array(p2)))