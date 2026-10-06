import os
from typing import Dict, Any, Optional
from .ai_response_schema import VisionModelOutput, GenAIInput
from .notes_processor import NotesProcessor
from .explanation_generator import ExplanationGenerator
from .evidence_validator import EvidenceValidator

class GenAIPipeline:
    """
    The central orchestrator for the GenAI module. 
    This is the only class Person 2 (Backend) needs to interact with.
    """
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_LLM", "False").lower() == "true"
        self.notes_processor = NotesProcessor()
        self.generator = ExplanationGenerator()
        self.validator = EvidenceValidator()

    def run_analysis(self, vision_data: Dict[str, Any], raw_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the full GenAI pipeline.
        
        :param vision_data: A dictionary containing the output from Person 3 (the vision model).
        :param raw_notes: A raw string containing patient symptoms or clinical notes.
        :return: A fully structured and validated dictionary ready to be returned as a JSON API response.
        """
        
        # 1. Parse the raw dict from the vision model into our strict Pydantic schema
        try:
            vision_output = VisionModelOutput(**vision_data)
        except Exception as e:
            return self._build_error_response(f"Invalid vision data format: {str(e)}")

        # 2. Fast-fail edge case: If the image is poor quality or unsupported, bypass the LLM entirely!
        if vision_output.status in ["poor_quality", "unsupported"]:
            return {
                "summary": f"Image analysis aborted. Status: {vision_output.status}",
                "findings": [],
                "limitations": [
                    "The provided image was flagged as poor quality or an unsupported modality.",
                    "Please upload a suitable medical image."
                ],
                "validation_status": {"is_valid": True, "errors": [], "warnings": ["Aborted before LLM generation."]}
            }

        # Demo Safety Net
        if self.use_mock:
            print("[INFO] MOCK MODE ENABLED: Returning pre-written safe response to bypass API issues.")
            return {
              "summary": "The vision model identified a possible finding that warrants clinician review alongside the reported symptoms.",
              "findings": [
                {
                  "finding": vision_output.findings[0].label if vision_output.findings else "possible_finding",
                  "image_region_id": vision_output.findings[0].region_id if vision_output.findings else "unknown",
                  "model_score": vision_output.findings[0].score if vision_output.findings else 0.0,
                  "supporting_notes": [
                    {
                      "text": raw_notes or "No notes provided",
                      "source": "Raw Notes"
                    }
                  ],
                  "explanation": f"The vision model identified a possible finding with a score of {vision_output.findings[0].score if vision_output.findings else 0.0}. Clinical correlation is required.",
                  "uncertainty": ["The model score represents an automated probability and is not definitive proof of pathology."],
                  "status": "review_required"
                }
              ],
              "limitations": ["This system is an assistive decision-support tool."],
              "validation_status": {"is_valid": True, "errors": [], "warnings": ["Generated in MOCK mode."]}
            }

        # 3. Process the clinical notes to extract structured symptoms/history
        clinical_context = self.notes_processor.process_notes(raw_notes)
        
        # 4. Combine inputs for the generator
        genai_input = GenAIInput(
            vision_output=vision_output,
            clinical_context=clinical_context
        )
        
        # 5. Generate the AI explanation
        try:
            ai_report = self.generator.generate_explanation(genai_input)
        except Exception as e:
            return self._build_error_response(f"Failed to generate AI explanation: {str(e)}")
            
        # 6. Validate the final report to ensure no hallucinations
        validation_result = self.validator.validate(genai_input, ai_report)
        
        # If the validator catches a critical hallucination, we can choose to suppress the findings
        if not validation_result["is_valid"]:
            return self._build_error_response(
                "Safety Validation Failed: The generated report contained hallucinated data.", 
                validation_errors=validation_result["errors"]
            )
            
        # 7. Package the final result
        final_output = ai_report.model_dump()
        final_output["validation_status"] = validation_result
        
        return final_output

    def _build_error_response(self, message: str, validation_errors: Optional[list] = None) -> Dict[str, Any]:
        """Helper to return a safe fallback response if the pipeline fails."""
        return {
            "summary": "AI Analysis Failed",
            "findings": [],
            "limitations": [message],
            "validation_status": {
                "is_valid": False, 
                "errors": validation_errors or [message], 
                "warnings": []
            }
        }
