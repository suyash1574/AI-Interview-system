import pytest
from unittest.mock import patch, MagicMock
from backend.core.services.extraction import GLiNERExtractor

def test_gliner_extraction_fallback():
    extractor = GLiNERExtractor()
    # Force ImportError
    with patch('backend.core.services.extraction.GLiNERExtractor._load_model', side_effect=ImportError):
        result = extractor.extract_competencies("We need a Python developer with System Design experience.")
        
        assert len(result) == 2
        assert result[0]["name"] == "Python"
        assert result[1]["name"] == "System Design"

@patch('backend.core.services.extraction.GLiNERExtractor._load_model')
def test_gliner_extraction_success(mock_load):
    mock_model = MagicMock()
    mock_model.predict_entities.return_value = [
        {"text": "React", "label": "tool", "score": 0.98},
        {"text": "Communication", "label": "competency", "score": 0.85}
    ]
    mock_load.return_value = mock_model
    
    extractor = GLiNERExtractor()
    result = extractor.extract_competencies("Looking for React and Communication skills.")
    
    assert len(result) == 2
    assert result[0]["name"] == "React"
    assert result[0]["type"] == "tool"
    assert result[1]["name"] == "Communication"
    
    mock_model.predict_entities.assert_called_once()
