from .ai_response_schema import GenAIInput, AIAnalysisReport
from typing import List, Dict

class EvidenceValidator:
    """
    Validates the AI-generated explanation to ensure it strictly grounds itself
    in the provided vision findings and does not hallucinate scores, regions, or findings.
    """
    
    def validate(self, original_inputs: GenAIInput, ai_report: AIAnalysisReport) -> Dict[str, any]:
        is_valid = True
        warnings: List[str] = []
        errors: List[str] = []
        
        # Extract valid vision finding labels for checking
        valid_findings = {f.finding: f for f in original_inputs.vision_output.findings}
        
        for ai_finding in ai_report.findings:
            # 1. Check if the finding label actually exists in the vision output
            if ai_finding.finding not in valid_findings:
                is_valid = False
                errors.append(f"Hallucinated finding: '{ai_finding.finding}' was not present in the vision model output.")
                continue
                
            original_finding = valid_findings[ai_finding.finding]
            
            # 2. Check if the score was preserved exactly
            if ai_finding.confidence != original_finding.confidence:
                is_valid = False
                errors.append(f"Altered confidence for '{ai_finding.finding}': Expected {original_finding.confidence}, but AI reported {ai_finding.confidence}.")
                
            # 3. Check if the location was preserved exactly
            original_loc = original_finding.location.model_dump() if original_finding.location else None
            if ai_finding.location != original_loc:
                is_valid = False
                errors.append(f"Altered location for '{ai_finding.finding}': Expected {original_loc}, but AI reported {ai_finding.location}.")
                
            # 4. Check for appropriate status based on uncertainty/notes
            if not ai_finding.supporting_notes and original_inputs.clinical_context.raw_notes:
                warnings.append(f"Warning: Finding '{ai_finding.finding}' has no supporting notes linked, but clinical context was provided.")

        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
