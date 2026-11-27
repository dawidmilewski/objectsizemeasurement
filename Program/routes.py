from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from image_utils import decode_and_resize_image
from measurement_service import detect_aruco_preview, analyze_objects
from schemas import HealthResponse, CheckArucoResponse, AnalyzeResponse

router = APIRouter(prefix="/api", tags=["Pomiar Wizyjny"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")


@router.post("/check-aruco", response_model=CheckArucoResponse)
async def check_aruco(file: UploadFile = File(...)):
    file_bytes = await file.read()
    try:
        image = decode_and_resize_image(file_bytes)
        return detect_aruco_preview(image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(file: UploadFile = File(...), bok_cm: float = Form(5.0)):
    if bok_cm <= 0:
        raise HTTPException(status_code=400, detail="Rozmiar znacznika musi być większy od zera.")

    file_bytes = await file.read()
    try:
        image = decode_and_resize_image(file_bytes)
        return analyze_objects(image, bok_cm)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))