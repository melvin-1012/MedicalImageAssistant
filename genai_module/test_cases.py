from genai_module.ai_response_schema import GenAIInput, VisionModelOutput, VisionFinding, ClinicalContext, AIAnalysisReport, ExplainedFinding, SupportingNote
from genai_module.explanation_generator import ExplanationGenerator
from genai_module.evidence_validator import EvidenceValidator
import json

def run_mock_demo():
    print("--- Running Mock Demo ---")
    
    # 1. Create mock input from the Vision Model (Person 3)
    mock_vision_output = VisionModelOutput(
        status="success",
        modality="X-Ray",
        findings=[
            VisionFinding(
                label="possible_lung_opacity",
                score=0.82,
                region_id="region_1"
            )
        ]
    )
    
    # 2. Create mock input from the Patient/Backend (Person 2)
    mock_clinical_context = ClinicalContext(
        raw_notes="Patient reports a persistent cough for 2 weeks and mild fever.",
        extracted_symptoms=["persistent cough", "mild fever"],
        extracted_history=[]
    )
    
    # 3. Combine them into the GenAI input
    inputs = GenAIInput(
        vision_output=mock_vision_output,
        clinical_context=mock_clinical_context
    )
    
    print("\n[Testing Evidence Validator (Offline)]")
    # Simulate an AI output to test our validator offline
    mock_ai_report = AIAnalysisReport(
        summary="Requires clinician review",
        findings=[
            ExplainedFinding(
                finding="possible_lung_opacity",
                image_region_id="region_1",
                model_score=0.82, # Correct score
                supporting_notes=[SupportingNote(text="persistent cough for 2 weeks")],
                explanation="The model identified a possible opacity. The patient's cough may be relevant context.",
                uncertainty=["Clinical correlation is required."],
                status="review_required"
            )
        ]
    )
    
    validator = EvidenceValidator()
    validation_result = validator.validate(inputs, mock_ai_report)
    print(f"Validation Result (Valid Report): {validation_result}")
    
    # Simulate a hallucinated report
    bad_ai_report = mock_ai_report.model_copy(deep=True)
    bad_ai_report.findings[0].model_score = 0.99 # Hallucinated score
    bad_ai_report.findings[0].finding = "lung_cancer" # Hallucinated finding
    
    bad_validation = validator.validate(inputs, bad_ai_report)
    print(f"Validation Result (Hallucinated Report): {bad_validation}")
    
    print("\n[Testing Explanation Generator (Requires API)]")
    generator = ExplanationGenerator()
    try:
        report = generator.generate_explanation(inputs)
        print("\n=== AI Analysis Report ===")
        print(json.dumps(report.model_dump(), indent=2))
        
        # Validate the real output
        real_validation = validator.validate(inputs, report)
        print(f"\nReal Report Validation: {real_validation}")
        
    except Exception as e:
        print(f"\nError generating explanation: {e}")

if __name__ == "__main__":
    run_mock_demo()
