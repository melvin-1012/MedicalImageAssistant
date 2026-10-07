"""
Mock Data Scenarios for Frontend and Backend Testing.
Person 1 and Person 2 can use these payloads to build the UI and Database
before the real Vision model (Person 3) is fully trained.
"""

MOCK_SCENARIOS = {
    # Scenario 1: A normal successful detection with patient context
    "standard_finding": {
        "vision_data": {
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
        },
        "raw_notes": "Patient reports a persistent cough for 2 weeks and mild fever."
    },
    
    # Scenario 2: High confidence finding but NO patient notes provided
    "missing_notes": {
        "vision_data": {
            "status": "success",
            "modality": "CT Scan",
            "findings": [
                {
                    "finding": "suspected_fracture",
                    "confidence": 0.95,
                    "location": {
                        "x1": 100,
                        "y1": 150,
                        "x2": 200,
                        "y2": 250
                    },
                    "heatmap_available": False,
                    "requires_physician_review": True
                }
            ]
        },
        "raw_notes": ""
    },
    
    # Scenario 3: The image was too blurry or corrupted to analyze
    "poor_quality_image": {
        "vision_data": {
            "status": "poor_quality",
            "modality": "MRI",
            "findings": []
        },
        "raw_notes": "Patient complains of severe headaches."
    },
    
    # Scenario 4: The vision model found absolutely nothing (healthy patient)
    "healthy_patient": {
        "vision_data": {
            "status": "success",
            "modality": "X-Ray",
            "findings": []
        },
        "raw_notes": "Routine annual physical checkup. No complaints."
    }
}
