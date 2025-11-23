from typing import List, Dict

# Exemplo: pesos por label -> carreira
PESOS = {
    "python": {"Data/ML": 0.6, "Back-end": 0.4},
    "java": {"Back-end": 0.7, "Full-Stack": 0.3},
    "react": {"Front-end": 0.8, "Full-Stack": 0.2},
    "arduino": {"Embarcados": 0.9},
    "docker": {"DevOps": 0.7, "Full-Stack": 0.3},
    "kubernetes": {"DevOps": 0.9},
}

def score_from_detections(detections: List[Dict]) -> Dict[str, float]:
    score = {}
    for d in detections:
        label = d.get("label")
        conf = float(d.get("confidence", 0))
        if label in PESOS:
            for carreira, peso in PESOS[label].items():
                score[carreira] = score.get(carreira, 0.0) + peso * conf
    # normalização simples
    if not score:
        return {}
    max_v = max(score.values())
    if max_v > 0:
        score = {k: v / max_v for k, v in score.items()}
    return score
