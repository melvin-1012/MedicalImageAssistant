import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from .ai_response_schema import GenAIInput, AIAnalysisReport

# Load environment variables
load_dotenv()

class ExplanationGenerator:
    def __init__(self):
        # Initialize the Gemini client. It automatically picks up GEMINI_API_KEY from the environment.
        self.client = genai.Client()
        # We use a model that supports structured outputs well.
        self.model_name = 'gemini-3.8-flash'
        
        self.system_instruction = """
You are a medical AI assistant designed to help doctors interpret medical imaging results alongside patient clinical notes.
Your primary task is to combine the vision model's findings with the patient's context to provide an evidence-grounded explanation.

CRITICAL RULES:
1. You are a decision-support tool. Never confirm a diagnosis.
2. Do not invent, guess, or hallucinate findings, bounding boxes, or confidence scores.
3. Only use the scores, regions, and findings provided in the vision model output.
4. If the vision model status is 'poor_quality' or 'unsupported', explain that the image cannot be analyzed reliably.
5. Use cautious language (e.g., "The model identified a possible finding...", "Clinical correlation is required").
6. Link patient symptoms to the vision findings only as supporting context, not as absolute proof.
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_explanation(self, inputs: GenAIInput) -> AIAnalysisReport:
        """
        Takes the combined vision model output and clinical context and generates
        a structured explanation matching the AIAnalysisReport schema.
        """
        
        # Prepare the prompt payload
        prompt = f"""
Please analyze the following inputs and provide a structured AI analysis report.

--- VISION MODEL OUTPUT ---
Status: {inputs.vision_output.status}
Modality: {inputs.vision_output.modality}
Findings: {[f.model_dump() for f in inputs.vision_output.findings]}

--- CLINICAL CONTEXT ---
Raw Notes: {inputs.clinical_context.raw_notes if inputs.clinical_context.raw_notes else "None provided"}
Symptoms: {', '.join(inputs.clinical_context.extracted_symptoms) if inputs.clinical_context.extracted_symptoms else "None"}
History: {', '.join(inputs.clinical_context.extracted_history) if inputs.clinical_context.extracted_history else "None"}

Generate the JSON response matching the required schema. Ensure you preserve the exact confidence and location for every finding.
"""
        
        # Call the Gemini API enforcing the Pydantic schema
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=AIAnalysisReport,
                temperature=0.0 # Low temperature for more deterministic, factual output
            ),
        )
        
        # The response.text is guaranteed to be a JSON string matching AIAnalysisReport
        # Parse it back into the Pydantic model and return
        return AIAnalysisReport.model_validate_json(response.text)
