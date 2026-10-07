import cv2
import json
from cv.classifier import DenseNet121Classifier

def run_test():
    print("Loading test_xray.png...")
    # Load image in grayscale
    image = cv2.imread("test_xray.png", cv2.IMREAD_GRAYSCALE)
    
    if image is None:
        print("Error: Could not find test_xray.png")
        return

    print("Initializing DenseNet-121 Classifier...")
    classifier = DenseNet121Classifier()
    
    print("Downloading/Loading weights (this may take a minute the first time)...")
    classifier.load_model()
    
    print(f"Model successfully loaded on: {classifier.get_model_info()['device']}")
    
    print("Running classification inference...")
    results = classifier.predict(image)
    
    print("\n=== Classification Results ===")
    # Print results sorted by highest probability
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
    print(json.dumps(sorted_results, indent=2))

if __name__ == "__main__":
    run_test()
