from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from .pipeline import GenAIPipeline

# Create a FastAPI router that Person 2 can easily include in their main app
router = APIRouter(prefix="/genai", tags=["GenAI Module"])

# Initialize the pipeline once when the server starts
pipeline = GenAIPipeline()

# Define the exact JSON payload Person 2 needs to send us
class AnalyzeRequest(BaseModel):
    vision_data: Dict[str, Any] = Field(..., description="The exact JSON output from the Vision Model (Person 3)")
    raw_notes: Optional[str] = Field(None, description="The raw patient notes or symptoms from the database")

@router.post("/analyze")
async def analyze_case(request: AnalyzeRequest):
    """
    Endpoint for Person 2 (Backend) to send vision data and patient notes.
    Returns the fully validated, evidence-grounded AI Analysis Report.
    """
    try:
        # Run our central GenAI pipeline
        result = pipeline.run_analysis(
            vision_data=request.vision_data,
            raw_notes=request.raw_notes
        )
        return result
        
    except Exception as e:
        # Catch any unexpected crashes and return a clean 500 HTTP error
        raise HTTPException(status_code=500, detail=f"Internal GenAI Pipeline Error: {str(e)}")
