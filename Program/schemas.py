from typing import List, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class CheckArucoResponse(BaseModel):
    image_base64: str
    width: int
    height: int
    aruco_found: bool
    punkty_aruco: Optional[List[List[float]]] = None


class MeasuredObject(BaseModel):
    id: int
    surowy_hull_px: List[List[float]]
    rogi_prostokata_px: List[List[float]]
    czworokat_px: List[List[float]]
    prostokat_cm: List[List[float]]
    dlugosc_cm: float
    szerokosc_cm: float
    czworokat_cm: List[List[float]]
    pelny_hull_cm: List[List[float]]
    boki_otoczki_cm: List[float]
    metoda: str


class AnalyzeResponse(BaseModel):
    width: int
    height: int
    rozmiar_aruco_cm: float
    punkty_aruco: List[List[float]]
    obiekty: List[MeasuredObject]