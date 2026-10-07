import os
from dotenv import load_dotenv
import instructor
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from .ai_response_schema import GenAIInput, AIAnalysisReport

# Load environment variables explicitly from the genai_module folder
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class ExplanationGenerator:
    def __init__(self):
        # Initialize Groq client with Instructor for Pydantic support
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY in environment.")
            
        self.client = instructor.from_groq(Groq(api_key=api_key, timeout=60.0, max_retries=3), mode=instructor.Mode.TOOLS)
        # We use a powerful open-source model available on Groq for medical reasoning
        self.model_name = 'openai/gpt-oss-120b'
        
        self.system_instruction = """
You are a medical AI assistant designed to help doctors interpret medical imaging results alongside patient clinical notes.
Your primary task is to combine the vision model's findings with the patient's context to provide an evidence-grounded explanation.

STRICT MEDICAL GROUNDING RULES:
1. Do not invent, guess, or hallucinate findings, bounding boxes, or confidence scores.
2. The vision model's score and location MUST be preserved exactly as provided. Never modify confidence or coordinates.
3. You are an assistive decision-support tool, not an autonomous diagnostic system. Never claim or state a confirmed diagnosis.
4. The supported finding from the vision model is 'possible_abnormal_opacity'. Do NOT invent or infer ungrounded abnormalities such as pleural effusion, fracture, pneumothorax, cardiomegaly, mass, or pneumonia unless explicitly provided in the input vision findings.
5. If vision model findings are empty, the summary MUST be:
   "No abnormal opacity was detected by the current computer-vision model. Routine physician review is recommended."
   Do NOT say "No abnormal findings detected."
6. If finding is 'possible_abnormal_opacity', explain that an area of possible abnormal opacity was identified in the localized region, that the finding is uncertain, and that physician review and clinical correlation are recommended.
7. Use careful uncertainty language ("may represent...", "suggestive of...", "possible...", "requires physician review...", "clinical correlation recommended...").
8. Any explainability heatmap is a "Model-Grounded Heatmap" / "AI Explainability Heatmap". Do not refer to it as Grad-CAM.
9. Link patient symptoms to the vision findings only as supporting context, not as absolute proof.
10. CRITICAL: Every finding MUST include the 'status' field (e.g., 'review_required').
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_explanation(self, inputs: GenAIInput) -> AIAnalysisReport:
        """
        Takes the combined vision model output and clinical context and generates
        a safe, structured, evidence-grounded explanation.
        """
        
        prompt = f"""
Analyze the following patient data and generate an AIAnalysisReport.

Vision Model Status: {inputs.vision_output.status}
Vision Model Modality: {inputs.vision_output.modality}
Vision Model Findings: {inputs.vision_output.findings}

Patient Raw Notes: {inputs.clinical_context.raw_notes}
Symptoms: {', '.join(inputs.clinical_context.extracted_symptoms) if inputs.clinical_context.extracted_symptoms else "None"}
History: {', '.join(inputs.clinical_context.extracted_history) if inputs.clinical_context.extracted_history else "None"}

Generate the JSON response matching the required schema. Ensure you preserve the exact confidence and location for every finding.
"""
        
        # Call the Groq API enforcing the Pydantic schema
        response = self.client.chat.completions.create(
            model=self.model_name,
            response_model=AIAnalysisReport,
            temperature=0.0,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response
