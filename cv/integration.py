"""End-to-end integration orchestrator between Medical CV and Multimodal GenAI.

Connects:
1. MedicalCVPipeline (OpenCV, YOLO, Localization, Heatmap, Quality) -> CVAnalysisResult
2. GenAIPipeline (NotesProcessor, ExplanationGenerator, EvidenceValidator) -> AIAnalysisReport
3. Produces the single authoritative Integrated Medical AI contract.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from cv.pipeline import MedicalCVPipeline
from cv.schemas import AnalysisStatus, CVAnalysisResult
from genai_module.pipeline import GenAIPipeline


class IntegratedMedicalAIPipeline:
    """Orchestrates end-to-end medical CV inference and grounded GenAI explanation."""

    def __init__(
        self,
        cv_pipeline: Optional[MedicalCVPipeline] = None,
        genai_pipeline: Optional[GenAIPipeline] = None,
    ) -> None:
        self.cv = cv_pipeline or MedicalCVPipeline()
        self.genai = genai_pipeline or GenAIPipeline()

    def initialize(self) -> None:
        """Initialize underlying pipelines."""
        if hasattr(self.cv, "initialize"):
            self.cv.initialize()

    def run(
        self,
        image_path: Path | str,
        clinical_notes: Optional[str] = None,
        output_dir: Optional[Path | str] = None,
    ) -> Dict[str, Any]:
        """Execute end-to-end CV and GenAI analysis with fast-fail safety checks."""
        # 1. Run CV Pipeline
        cv_result: CVAnalysisResult = self.cv.run(image_path, output_dir=output_dir)
        cv_dict = cv_result.to_genai_dict()

        # 2. Check for fast-fail quality rejection (Phase 7 requirement)
        if cv_result.status == AnalysisStatus.REJECTED or cv_dict.get("status") == "poor_quality":
            issues = cv_dict.get("quality", {}).get("issues", [])
            reasons_str = f" Reason(s): {', '.join(issues)}." if issues else ""
            genai_report = {
                "summary": "Image quality is insufficient for reliable AI analysis.",
                "findings": [],
                "limitations": [
                    f"Image quality is insufficient for reliable AI analysis.{reasons_str}",
                    "Please upload a standard diagnostic-quality radiograph.",
                    "AI generation was bypassed to prevent misleading medical interpretations."
                ],
                "validation_status": {
                    "is_valid": True,
                    "errors": [],
                    "warnings": ["Fast-fail triggered: GenAI bypassed due to image quality."]
                }
            }
        else:
            # 3. Call GenAI with real CV data (no mock data!)
            genai_report = self.genai.run_analysis(
                vision_data=cv_dict,
                raw_notes=clinical_notes
            )

        # 4. Assemble the final unified integration payload (Phase 8 contract)
        integrated_payload = {
            "status": cv_dict.get("status", "success"),
            "modality": cv_dict.get("modality", "X-Ray"),
            "image": cv_dict.get("image", {}),
            "quality": cv_dict.get("quality", {}),
            "findings": cv_dict.get("findings", []),
            "artifacts": cv_dict.get("artifacts", {}),
            "genai_analysis": {
                "summary": genai_report.get("summary", ""),
                "findings": genai_report.get("findings", []),
                "limitations": genai_report.get("limitations", []),
                "validation_status": genai_report.get("validation_status", {"is_valid": True, "errors": [], "warnings": []}),
            },
            "safety": {
                "physician_review_required": True,
                "no_confirmed_diagnosis": True,
            },
            # Keep cv_result reference for UI visualization rendering
            "_cv_result": cv_result,
        }

        return integrated_payload
