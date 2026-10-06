from pydantic import BaseModel, Field
from typing import List, Optional, Union

# ---------------------------------------------------------
# INPUT SCHEMAS (What you expect from Person 2 & 3)
# ---------------------------------------------------------

class VisionFinding(BaseModel):
    label: str = Field(..., description="The name of the finding identified by the vision model (e.g., 'opacity')")
    score: float = Field(..., description="The confidence score from the vision model, typically 0.0 to 1.0")
    region_id: Optional[str] = Field(None, description="Identifier for the localized region (e.g., 'region_1')")

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
    finding: str = Field(..., description="The name of the finding from the vision model")
    image_region_id: Optional[str] = Field(None, description="The corresponding region_id from the vision model")
    model_score: float = Field(..., description="The exact score provided by the vision model")
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
