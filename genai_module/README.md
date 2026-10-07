# GenAI and Clinical Context Module

This module is responsible for taking the outputs from the Computer Vision model (Person 3) and the Clinical Notes (Person 2) and generating a structured, cautious, and evidence-grounded explanation for the doctor using the Gemini API.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Gemini API key:
   `cp .env.example .env`

## Module Structure
- `ai_response_schema.py`: Pydantic models defining the expected inputs and strict JSON output contract.
- More files will be added slowly (e.g., `explanation_generator.py`).
