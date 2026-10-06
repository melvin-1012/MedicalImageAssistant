from genai_module.pipeline import GenAIPipeline
import json

def run_mock_demo():
    print("--- Running Full Pipeline Demo ---")
    
    pipeline = GenAIPipeline()

    # 1. Mock inputs exactly as Person 2 (Backend) would provide them
    mock_vision_data = {
        "status": "success",
        "modality": "X-Ray",
        "findings": [
            {
                "finding": "possible_abnormal_opacity",
                "confidence": 0.82,
                "location": {
                    "x1": 320,
                    "y1": 240,
                    "x2": 610,
                    "y2": 520
                },
                "heatmap_available": True,
                "requires_physician_review": True
            }
        ]
    }
    
    mock_raw_notes = "Patient reports a persistent cough for 2 weeks and mild fever."
    
    print("\n[Test 1: Standard Successful Run]")
    print("Executing pipeline...")
    final_output = pipeline.run_analysis(vision_data=mock_vision_data, raw_notes=mock_raw_notes)
    
    print("\n=== Final JSON Response (For Backend) ===")
    print(json.dumps(final_output, indent=2))
    
    print("\n--------------------------------------------------")
    
    print("\n[Test 2: Edge Case - Poor Quality Image]")
    bad_vision_data = {
        "status": "poor_quality",
        "modality": "X-Ray",
        "findings": []
    }
    
    bad_image_output = pipeline.run_analysis(vision_data=bad_vision_data, raw_notes=mock_raw_notes)
    print("\n=== Fast-Fail JSON Response ===")
    print(json.dumps(bad_image_output, indent=2))

if __name__ == "__main__":
    run_mock_demo()
