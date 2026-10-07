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
            
        self.client = instructor.from_groq(Groq(api_key=api_key), mode=instructor.Mode.TOOLS)
        # We use llama3-70b for advanced medical reasoning
        self.model_name = 'llama3-70b-8192'
        
        self.system_instruction = """
You are a medical AI assistant designed to help doctors interpret medical imaging results alongside patient clinical notes.
Your primary task is to combine the vision model's findings with the patient's context to provide an evidence-grounded explanation.

STRICT MEDICAL RULES:
1. Do not invent, guess, or hallucinate findings, bounding boxes, or confidence scores.
2. The vision model's score and location MUST be preserved exactly as provided.
3. You are an assistive decision-support tool, not an autonomous diagnostic system.
4. If a finding is mentioned, explain its potential clinical correlation to the patient's notes.
5. Always state that the finding requires physician review.
6. Link patient symptoms to the vision findings only as supporting context, not as absolute proof.
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
