from genai_module.ai_response_schema import GenAIInput, VisionModelOutput, VisionFinding, ClinicalContext
from genai_module.explanation_generator import ExplanationGenerator
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
        patient_notes="Patient reports a persistent cough for 2 weeks and mild fever."
    )
    
    # 3. Combine them into the GenAI input
    inputs = GenAIInput(
        vision_output=mock_vision_output,
        clinical_context=mock_clinical_context
    )
    
    # 4. Generate the explanation
    print("Initializing Explanation Generator...")
    generator = ExplanationGenerator()
    
    print("Calling Gemini API...")
    try:
        report = generator.generate_explanation(inputs)
        
        # 5. Print the result
        print("\n=== AI Analysis Report ===")
        # Dump the Pydantic model to a formatted JSON string for display
        print(json.dumps(report.model_dump(), indent=2))
        
    except Exception as e:
        print(f"\nError generating explanation: {e}")

if __name__ == "__main__":
    run_mock_demo()
