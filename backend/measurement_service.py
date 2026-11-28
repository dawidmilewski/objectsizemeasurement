import numpy as np

from vision import znajdz_aruco, wykryj_kontury
from measurement import oblicz_wymiary_obiektu
from image_utils import encode_image_to_base64
from schemas import CheckArucoResponse, AnalyzeResponse, MeasuredObject


def detect_aruco_preview(image: np.ndarray) -> CheckArucoResponse:
    height, width = image.shape[:2]
    punkty_aruco, _ = znajdz_aruco(image, wylicz_h=False)

    return CheckArucoResponse(
        image_base64=encode_image_to_base64(image),
        width=width,
        height=height,
        aruco_found=punkty_aruco is not None,
        punkty_aruco=punkty_aruco.reshape(4, 2).tolist() if punkty_aruco is not None else None,
    )


def analyze_objects(image: np.ndarray, bok_cm: float) -> AnalyzeResponse:
    height, width = image.shape[:2]
    punkty_aruco, H = znajdz_aruco(image, bok_cm, wylicz_h=True)

    if punkty_aruco is None or H is None:
        raise LookupError("Nie wykryto znacznika ArUco na zdjęciu.")

    try:
        H_inv = np.linalg.inv(H)
    except np.linalg.LinAlgError as exc:
        raise ValueError("Wyznaczona macierz homografii jest osobliwa i nieodwracalna.") from exc

    detected_contours = wykryj_kontury(image, punkty_aruco)
    measured_objects = []

    for idx, obiekt in enumerate(detected_contours):
        (
            rogi_prostokata_px,
            czworokat_px,
            prostokat_cm,
            dl,
            szer,
            czworokat_cm,
            pelny_hull_cm,
            boki_szczegoly,
            metoda,
        ) = oblicz_wymiary_obiektu(H, obiekt["hull_px"], H_inv=H_inv)

        measured_objects.append(
            MeasuredObject(
                id=idx + 1,
                surowy_hull_px=obiekt["hull_px"].reshape(-1, 2).tolist(),
                rogi_prostokata_px=rogi_prostokata_px.reshape(-1, 2).tolist(),
                czworokat_px=czworokat_px.reshape(-1, 2).tolist(),
                prostokat_cm=prostokat_cm.reshape(4, 2).tolist(),
                dlugosc_cm=float(dl),
                szerokosc_cm=float(szer),
                czworokat_cm=czworokat_cm.reshape(-1, 2).tolist(),
                pelny_hull_cm=pelny_hull_cm.reshape(-1, 2).tolist(),
                boki_czworokata_cm=[float(b) for b in boki_szczegoly],
                metoda=metoda,
            )
        )

    return AnalyzeResponse(
        width=width,
        height=height,
        rozmiar_aruco_cm=float(bok_cm),
        punkty_aruco=punkty_aruco.reshape(4, 2).tolist(),
        obiekty=measured_objects,
    )