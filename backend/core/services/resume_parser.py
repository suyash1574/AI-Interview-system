import io
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import pypdf

from backend.core.services.extraction import GLiNERExtractor

logger = logging.getLogger(__name__)

class ParsedResume(BaseModel):
    filename: str
    raw_text: str
    skills: List[Dict[str, Any]]
    summary: str

class ResumeParserService:
    def __init__(self):
        self.extractor = GLiNERExtractor()

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
            return "\n".join(text_parts)
        except Exception as e:
            logger.warning(f"pypdf extraction failed ({e}), attempting fallback text decode")
            return file_bytes.decode("utf-8", errors="ignore")

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx:
                xml_content = docx.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                texts = [node.text for node in tree.iter() if node.tag.endswith("t") and node.text]
                return " ".join(texts)
        except Exception as e:
            logger.warning(f"DOCX extraction fallback ({e}): returning plain text decode")
            return file_bytes.decode("utf-8", errors="ignore")

    def parse(self, filename: str, file_bytes: bytes) -> ParsedResume:
        if filename.lower().endswith(".pdf"):
            raw_text = self.extract_text_from_pdf(file_bytes)
        elif filename.lower().endswith(".docx"):
            raw_text = self.extract_text_from_docx(file_bytes)
        else:
            raw_text = file_bytes.decode("utf-8", errors="ignore")

        # Extract competencies and skills
        extracted_skills = self.extractor.extract_competencies(raw_text)

        # Build clean summary for prompt injection
        skill_names = [s.get("name") for s in extracted_skills if isinstance(s, dict)]
        top_skills = ", ".join(skill_names[:8]) if skill_names else "General Software Development"
        
        # Take first 400 chars of raw text as introductory context
        preview_text = " ".join(raw_text.split()[:50])
        summary = f"Skills: {top_skills}. Background: {preview_text}"

        return ParsedResume(
            filename=filename,
            raw_text=raw_text,
            skills=extracted_skills,
            summary=summary,
        )
