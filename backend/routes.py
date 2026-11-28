import logging
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from starlette.concurrency import run_in_threadpool

from image_utils import decode_and_resize_image
from measurement_service import detect_aruco_preview, analyze_objects
from schemas import HealthResponse, CheckArucoResponse, AnalyzeResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Pomiar Wizyjny"])
MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB


async def _read_validated_image(file: UploadFile) -> bytes:
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Przesłany plik jest pusty.")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Plik przekracza limit 20 MB.")
    return file_bytes


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")


@router.post("/check-aruco", response_model=CheckArucoResponse)
async def check_aruco(file: UploadFile = File(...)):
    file_bytes = await _read_validated_image(file)
    try:
        image = await run_in_threadpool(decode_and_resize_image, file_bytes)
        return await run_in_threadpool(detect_aruco_preview, image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Nieoczekiwany błąd podczas detekcji ArUco")
        raise HTTPException(status_code=500, detail="Wewnętrzny błąd serwera podczas przetwarzania obrazu.")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(file: UploadFile = File(...), bok_cm: float = Form(5.0)):
    if bok_cm <= 0:
        raise HTTPException(status_code=400, detail="Rozmiar znacznika musi być większy od zera.")

    file_bytes = await _read_validated_image(file)
    try:
        image = await run_in_threadpool(decode_and_resize_image, file_bytes)
        return await run_in_threadpool(analyze_objects, image, bok_cm)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        logger.exception("Nieoczekiwany błąd podczas analizy obiektów")
        raise HTTPException(status_code=500, detail="Wewnętrzny błąd serwera podczas analizy obiektów.")