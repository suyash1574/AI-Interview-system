import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class GLiNERExtractor:
    """
    Service to extract skills and competencies from JDs and Resumes.
    Utilizes GLiNER (Generalist and Lightweight Model for Named Entity Recognition).
    """
    def __init__(self, model_name="urchade/gliner_medium-v2.1"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from gliner import GLiNER
            self._model = GLiNER.from_pretrained(self.model_name)
        return self._model

    def extract_competencies(self, text: str) -> List[Dict]:
        try:
            model = self._load_model()
            labels = ["skill", "competency", "tool", "technology", "certification"]
            entities = model.predict_entities(text, labels)
            return [
                {
                    "name": entity["text"],
                    "type": entity["label"],
                    "score": float(entity.get("score", 1.0))
                }
                for entity in entities
            ]
        except ImportError:
            logger.warning("gliner library not installed. Using fallback mock.")
            return [
                {"name": "Python", "type": "skill", "score": 0.99},
                {"name": "System Design", "type": "competency", "score": 0.95}
            ]
