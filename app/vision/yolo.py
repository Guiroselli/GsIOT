# app/vision/yolo.py
import os
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH", "./models/yolov8n.pt")
_model = None

def get_model():
    global _model
    if _model is None:
        _model = YOLO(MODEL_PATH)  # baixa na 1ª vez se não existir
    return _model

def run_inference(image_bgr, min_conf: float, imgsz: int = 640):
    model = get_model()
    results = model.predict(image_bgr, conf=min_conf, imgsz=imgsz, verbose=False)
    dets = []
    for r in results:
        for b in r.boxes:
            x1, y1, x2, y2 = b.xyxy[0].tolist()
            w, h = x2 - x1, y2 - y1
            cls = int(b.cls[0].item())
            label = r.names[cls]
            conf = float(b.conf[0].item())
            dets.append({
                "label": label,
                "confidence": conf,
                "bbox": [float(x1), float(y1), float(w), float(h)]
            })
    return dets
