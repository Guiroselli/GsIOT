# app/routers/analysis.py
import time, base64, os, cv2, numpy as np
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional, List, Dict
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.vision.yolo import run_inference
from app.db.session import SessionLocal
from app.db import models as m

load_dotenv()
MIN_CONF = float(os.getenv("MIN_CONFIDENCE", "0.35"))

router = APIRouter(prefix="/api", tags=["analysis"])

class DetectOut(BaseModel):
    detections: List[Dict]
    career_scores: Dict[str, float]
    latency_ms: int
    deteccao_id: int | None = None

@router.post("/analisar-imagem", response_model=DetectOut)
async def analisar_imagem(
    file: UploadFile = File(None),
    image_base64: Optional[str] = Form(None),
    min_confidence: Optional[float] = Form(None),
    usuario_id: Optional[int] = Form(1),
):
    t0 = time.time()
    minc = float(min_confidence) if min_confidence is not None else MIN_CONF

    # carrega a imagem
    if file:
        data = await file.read()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    elif image_base64:
        raw = base64.b64decode(image_base64.split(",")[-1])
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    else:
        return DetectOut(detections=[], career_scores={}, latency_ms=0)

    # YOLOv8 de verdade
    detections = run_inference(img, minc)

    # persiste no banco
    db: Session = SessionLocal()
    det_id = None
    try:
        det = m.Deteccao(usuario_id=usuario_id)
        db.add(det); db.flush()   # pega det.id
        det_id = det.id
        for d in detections:
            x, y, w, h = d["bbox"]
            db.add(m.DetalheDeteccao(
                deteccao_id=det_id,
                label=d["label"],
                confidence=float(d["confidence"]),
                x=float(x), y=float(y), w=float(w), h=float(h)
            ))
        db.commit()
    finally:
        db.close()

    latency = int((time.time()-t0)*1000)
    return DetectOut(detections=detections, career_scores={}, latency_ms=latency, deteccao_id=det_id)
