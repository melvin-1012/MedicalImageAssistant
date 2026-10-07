import os
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List
import instructor
from groq import Groq
from .ai_response_schema import ClinicalContext

class NotesExtraction(BaseModel):
    symptoms: List[str]
    history: List[str]

class NotesProcessor:
    """
    Parses unstructured patient notes and extracts structured clinical information
    such as symptoms and medical history using GenAI (Groq).
    """
    def __init__(self):
        # Initialize Groq client with Instructor for Pydantic support
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY in environment.")
            
        self.client = instructor.from_groq(Groq(api_key=api_key), mode=instructor.Mode.TOOLS)
        # Llama 3 70B is extremely fast and smart for extraction
        self.model_name = 'llama3-70b-8192'
        
        self.system_instruction = """
You are a medical data extraction assistant. Your task is to extract explicitly mentioned 
symptoms and medical history from the provided patient notes.
Do not invent information. If none are found, return empty lists.
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _extract_with_retry(self, raw_notes: str) -> NotesExtraction:
        response = self.client.chat.completions.create(
            model=self.model_name,
            response_model=NotesExtraction,
            temperature=0.0,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": f"Extract information from these notes:\n\n{raw_notes}"}
            ]
        )
        return response

    def process_notes(self, raw_notes: str) -> ClinicalContext:
        """
        Takes raw string notes and returns a structured ClinicalContext object.
        """
        if not raw_notes or not raw_notes.strip():
            return ClinicalContext(raw_notes=raw_notes, extracted_symptoms=[], extracted_history=[])
            
        try:
            # Attempt to extract with automatic retries if the API is busy
            extracted = self._extract_with_retry(raw_notes)
            
            return ClinicalContext(
                raw_notes=raw_notes,
                extracted_symptoms=extracted.symptoms,
                extracted_history=extracted.history
            )
            
        except Exception as e:
            print(f"Warning: Failed to extract structured notes (API error: {e}). Proceeding with raw notes only.")
            # Fallback gracefully if the API is down or overloaded
            return ClinicalContext(
                raw_notes=raw_notes,
                extracted_symptoms=[],
                extracted_history=[]
            )
