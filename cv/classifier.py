"""Model-agnostic classifier interface and DenseNet-121 medical classifier implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import numpy as np

from utils.logger import get_logger

logger = get_logger("classifier")

class ModelNotLoadedError(RuntimeError):
    """Raised when inference is requested without a loaded model."""

class BaseClassifier(ABC):
    """Core classifier interface depended upon by the pipeline."""
    name = "Classifier interface"

    @property
    @abstractmethod
    def is_loaded(self) -> bool: ...

    @property
    def ready(self) -> bool:
        return True

    @abstractmethod
    def load_model(self) -> None: ...

    @abstractmethod
    def predict(self, image: np.ndarray) -> Dict[str, float]:
        """Run classification on a preprocessed image."""

class MedicalClassifier(BaseClassifier):
    """Abstract medical abnormality classifier interface."""
    name = "Medical Classifier"

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata (architecture, version, target classes, device)."""

class NullClassifier(MedicalClassifier):
    """Placeholder used when no trained classification model exists."""

    @property
    def is_loaded(self) -> bool:
        return False

    def load_model(self) -> None:
        raise ModelNotLoadedError("No model available.")

    def predict(self, image: np.ndarray) -> Dict[str, float]:
        raise ModelNotLoadedError("No medical classifier loaded.")

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": "NullClassifier",
            "is_loaded": False,
            "supported_classes": []
        }

class DenseNet121Classifier(MedicalClassifier):
    """TorchXRayVision DenseNet-121 classifier for Chest X-Rays.
    Uses weights pre-trained specifically on medical chest X-ray datasets.
    """
    name = "TorchXRayVision DenseNet-121"

    def __init__(self, weights: str = "densenet121-res224-all"):
        self.weights = weights
        self._model = None
        self._device = None
        self._pathologies = []
        self._transform = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load_model(self) -> None:
        try:
            import torch
            import torchvision.transforms as T
            import torchxrayvision as xrv
        except ImportError:
            raise RuntimeError("torch, torchvision, and torchxrayvision are required to use DenseNet121Classifier.")
        
        if self.is_loaded:
            return
            
        logger.info(f"Loading {self.name} with weights {self.weights}")
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            # Load the DenseNet-121 model with specified weights
            self._model = xrv.models.DenseNet(weights=self.weights)
            self._model.to(self._device)
            self._model.eval()
            self._pathologies = self._model.pathologies
            
            # Resize and crop to 224x224 as expected by the model
            self._transform = T.Compose([
                T.Resize(224, antialias=True),
                T.CenterCrop(224)
            ])
            logger.info(f"Successfully loaded {self.name} on {self._device}")
        except Exception as e:
            logger.error(f"Failed to load {self.name}: {e}")
            self._model = None
            raise

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess standard uint8/uint16 image for TorchXRayVision.
        TorchXRayVision expects values scaled between [-1024, 1024] and shape (1, H, W).
        """
        # Convert to grayscale if RGB
        if len(image.shape) == 3:
            if image.shape[2] == 3:
                # Luminosity grayscale conversion
                image = 0.2989 * image[:,:,0] + 0.5870 * image[:,:,1] + 0.1140 * image[:,:,2]
            elif image.shape[2] == 1:
                image = image[:, :, 0]

        img = image.astype(np.float32)
        
        # Scale to [-1024, 1024]
        # A robust dynamic range scaling assuming the image contains meaningful signal
        img_min = img.min()
        img_max = img.max()
        if img_max > img_min:
            img = 2048 * (img - img_min) / (img_max - img_min) - 1024
        
        # Add channel dimension (C, H, W) -> (1, H, W)
        img = img[np.newaxis, ...]
        return img

    def predict(self, image: np.ndarray) -> Dict[str, float]:
        """Runs classification on the input image using inference mode."""
        if not self.is_loaded:
            raise ModelNotLoadedError("Model is not loaded. Call load_model() first.")
            
        import torch
        
        try:
            # 1. Apply TorchXRayVision specific numerical scaling
            img_xrv = self.preprocess_image(image)
            
            # 2. Convert to PyTorch Tensor
            img_tensor = torch.from_numpy(img_xrv)
            
            # 3. Apply spatial transforms (resize, crop)
            if self._transform:
                img_tensor = self._transform(img_tensor)
                
            # 4. Add batch dimension -> (1, 1, 224, 224)
            img_tensor = img_tensor.unsqueeze(0).to(self._device)
            
            # 5. Run inference with no gradient computation
            with torch.inference_mode():
                outputs = self._model(img_tensor)
                
            # TorchXRayVision returns a tensor of probabilities (sigmoid applied)
            probs = outputs[0].cpu().numpy()
            
            # 6. Map probabilities to pathology labels
            results = {}
            for i, pathology in enumerate(self._pathologies):
                results[pathology] = float(probs[i])
                
            return results
        except Exception as e:
            logger.error(f"Classification inference failed: {e}")
            return {}

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "weights": self.weights,
            "is_loaded": self.is_loaded,
            "device": str(self._device) if self._device else "none",
            "supported_classes": self._pathologies
        }
