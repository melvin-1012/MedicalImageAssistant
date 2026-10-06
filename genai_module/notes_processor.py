import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List
from .ai_response_schema import ClinicalContext

class NotesExtraction(BaseModel):
    symptoms: List[str]
    history: List[str]

class NotesProcessor:
    """
    Parses unstructured patient notes and extracts structured clinical information
    such as symptoms and medical history using GenAI.
    """
    def __init__(self):
        self.client = genai.Client()
        self.model_name = 'gemini-3.8-flash'
        
        self.system_instruction = """
You are a medical data extraction assistant. Your task is to extract explicitly mentioned 
symptoms and medical history from the provided patient notes.
Do not invent information. If none are found, return empty lists.
"""

    def process_notes(self, raw_notes: str) -> ClinicalContext:
        """
        Takes raw string notes and returns a structured ClinicalContext object.
        """
        if not raw_notes or not raw_notes.strip():
            return ClinicalContext(raw_notes=raw_notes, extracted_symptoms=[], extracted_history=[])
            
        try:
            # We use structured outputs to enforce the NotesExtraction schema
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Extract information from these notes:\n\n{raw_notes}",
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    response_schema=NotesExtraction,
                    temperature=0.0
                ),
            )
            
            # Parse the LLM's JSON into our Pydantic schema
            extracted = NotesExtraction.model_validate_json(response.text)
            
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
