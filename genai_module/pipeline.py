import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
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
        self.validator = EvidenceValidator()
        self._notes_processor = None
        self._generator = None

    @property
    def notes_processor(self):
        if self._notes_processor is None:
            self._notes_processor = NotesProcessor()
        return self._notes_processor

    @property
    def generator(self):
        if self._generator is None:
            self._generator = ExplanationGenerator()
        return self._generator

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
                "summary": "Image quality is insufficient for reliable AI analysis.",
                "findings": [],
                "limitations": [
                    "The provided image was flagged as insufficient quality or an unsupported modality for reliable computer-vision inference.",
                    "Please upload a standard diagnostic-quality radiograph."
                ],
                "validation_status": {"is_valid": True, "errors": [], "warnings": ["Aborted before AI generation due to image quality failure."]}
            }

        # Check for GROQ_API_KEY / demo fallback mode
        if not os.getenv("GROQ_API_KEY") or os.getenv("USE_MOCK_LLM", "False").lower() == "true":
            if not vision_output.findings:
                return {
                    "summary": "No abnormal opacity was detected by the current computer-vision model. Routine physician review is recommended.",
                    "findings": [],
                    "limitations": [
                        "IMPORTANT DISCLAIMER: AI-generated analysis is an assistive decision-support tool, not a confirmed diagnosis.",
                        "Absence of detected abnormal opacity does not exclude other thoracic pathologies. Routine physician review is recommended."
                    ],
                    "validation_status": {
                        "is_valid": True,
                        "errors": [],
                        "warnings": []
                    }
                }

            findings_list = []
            for f in vision_output.findings:
                loc_dict = f.location.model_dump() if f.location else None
                finding_display = "possible abnormal opacity" if f.finding == "possible_abnormal_opacity" else f.finding
                findings_list.append({
                    "finding": f.finding,
                    "location": loc_dict,
                    "confidence": f.confidence,
                    "supporting_notes": [
                        {"text": raw_notes or "Clinical correlation indicated", "source": "Clinical Notes"}
                    ] if raw_notes else [],
                    "explanation": (
                        f"An area of {finding_display} was identified in the localized region "
                        f"with model confidence {f.confidence:.6f}. The finding is uncertain and "
                        f"requires physician review and clinical correlation."
                    ),
                    "uncertainty": [
                        "Probabilistic computer-vision inference; requires attending physician verification.",
                        "Clinical correlation with patient history and physical examination is recommended."
                    ],
                    "status": "review_required"
                })
            
            return {
                "summary": "Possible abnormal opacity identified; clinical correlation and physician review required.",
                "findings": findings_list,
                "limitations": [
                    "IMPORTANT DISCLAIMER: AI-generated analysis is not a confirmed diagnosis. Final interpretation must be performed by a qualified physician.",
                    "The current computer-vision model detects possible abnormal opacities and does not evaluate all thoracic pathologies."
                ],
                "validation_status": {
                    "is_valid": True,
                    "errors": [],
                    "warnings": []
                }
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
