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

    print("\n--------------------------------------------------\n")
    
    print("[Test 3: Normal Image (No Findings)]")
    normal_vision_data = {
        "status": "success",
        "modality": "X-Ray",
        "findings": []
    }
    normal_result = pipeline.run_analysis(normal_vision_data, "Routine checkup. Patient feels fine.")
    print("\n=== Normal Image JSON Response ===")
    print(json.dumps(normal_result, indent=2))
    
    print("\n--------------------------------------------------\n")
    
    print("[Test 4: Multiple Findings with No Clinical Notes]")
    multi_vision_data = {
        "status": "success",
        "modality": "X-Ray",
        "findings": [
            {
                "finding": "possible_abnormal_opacity",
                "confidence": 0.88,
                "location": {"x1": 100, "y1": 100, "x2": 200, "y2": 200},
                "heatmap_available": True,
                "requires_physician_review": True
            },
            {
                "finding": "pleural_effusion",
                "confidence": 0.75,
                "location": {"x1": 50, "y1": 400, "x2": 150, "y2": 500},
                "heatmap_available": False,
                "requires_physician_review": True
            }
        ]
    }
    multi_result = pipeline.run_analysis(multi_vision_data, "")
    print("\n=== Multiple Findings JSON Response ===")
    print(json.dumps(multi_result, indent=2))

if __name__ == "__main__":
    run_mock_demo()
