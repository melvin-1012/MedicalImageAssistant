from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict

# ---------------------------------------------------------
# INPUT SCHEMAS (What you expect from Person 2 & 3)
# ---------------------------------------------------------

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class VisionFinding(BaseModel):
    finding: str = Field(..., description="The standardized finding label or code (e.g., 'possible_abnormal_opacity')")
    confidence: float = Field(..., description="The confidence score from the vision model, typically 0.0 to 1.0")
    location: Optional[BoundingBox] = Field(None, description="Bounding box coordinates of the finding")
    heatmap_available: Optional[bool] = Field(False)
    requires_physician_review: Optional[bool] = Field(True)

class VisionModelOutput(BaseModel):
    status: str = Field(..., description="Status of the image analysis ('success', 'poor_quality', 'unsupported', 'inconclusive')")
    findings: List[VisionFinding] = Field(default_factory=list, description="List of findings detected by the model")
    modality: str = Field(..., description="The imaging modality used (e.g., 'X-Ray', 'CT Scan')")

class ClinicalContext(BaseModel):
    raw_notes: Optional[str] = Field(None, description="Original raw clinical notes provided by the patient or doctor")
    extracted_symptoms: List[str] = Field(default_factory=list, description="Symptoms explicitly mentioned in the notes")
    extracted_history: List[str] = Field(default_factory=list, description="Relevant medical history or supplied test results")

class GenAIInput(BaseModel):
    vision_output: VisionModelOutput
    clinical_context: ClinicalContext


# ---------------------------------------------------------
# OUTPUT SCHEMAS (What you will return to Person 2)
# ---------------------------------------------------------

class SupportingNote(BaseModel):
    text: str = Field(..., description="Excerpt or summary from the patient notes")
    source: str = Field(default="patient_notes", description="Where this evidence came from")

class ExplainedFinding(BaseModel):
    finding: str = Field(..., description="The standardized code from the vision model")
    location: Optional[Dict[str, float]] = Field(None, description="The bounding box coordinates precisely preserved")
    confidence: float = Field(..., description="The exact confidence score provided by the vision model")
    supporting_notes: List[SupportingNote] = Field(default_factory=list, description="Relevant clinical context extracted from notes")
    explanation: str = Field(..., description="Evidence-grounded explanation. Must be cautious and link finding to notes without diagnosing.")
    uncertainty: List[str] = Field(default_factory=list, description="Statements regarding limitations or uncertainty for this finding")
    status: str = Field(..., description="Action required ('review_required', 'insufficient_evidence', 'inconclusive')")

class AIAnalysisReport(BaseModel):
    summary: str = Field(..., description="Overall summary of the GenAI analysis (e.g., 'Requires clinician review')")
    findings: List[ExplainedFinding] = Field(default_factory=list, description="List of explained findings")
    limitations: List[str] = Field(
        default=["AI-generated analysis is not a confirmed diagnosis. Clinical correlation is required."],
        description="Global system limitations and disclaimers"
    )
