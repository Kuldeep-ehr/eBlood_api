import json
import re
import io
import base64
from typing import Optional
from PIL import Image
import google.generativeai as genai

from form_schema import VALID_FIELDS, REQUIRED_FIELDS, FIELD_LABELS


def get_extraction_prompt() -> str:
    fields_desc = "\n".join(f"- {k}: {v}" for k, v in FIELD_LABELS.items())
    return f"""You are a medical/blood bank form data extraction assistant.
Extract ALL available information from the provided document and map it to the exact form field names below.

Valid form fields:
{fields_desc}

Special field notes:
- blood_request_type: "1" for adult, "2" for neonatal/pediatric
- age_type: "Y" for years, "M" for months, "D" for days
- gender: "Male", "Female", or "Other"
- blood_group: Use format like "A+Ve", "B-Ve", "O+Ve", "AB+Ve", "A+", "B-", etc. Preserve "Ve" suffix if present in document
- request_type: reason for the blood request (e.g. "General", "Emergency", "Thalassemia")
- transfusion_reason: reason for transfusion (e.g. "General", "Surgery", etc.)
- Dates should be in ISO 8601 format: "YYYY-MM-DDTHH:mm:ss.sssZ"
- hospital_id: numeric hospital ID if available
- cross_match_for: numeric value (e.g. 1)
- searchfor: usually "patient"
- patient_relation: e.g. "Father", "Mother", "Spouse"
- component_details: array of objects with:
  - "component": blood component name (e.g. "Fresh Frozen Plasma", "Whole Blood", "PRBC", "Platelets", "Packed Red Blood Cells")
  - "unit": number of units as string (e.g. "2")
  - "volume_normal": normal volume as string (empty if aliquot)
  - "volume": array of volume strings, one per unit (e.g. ["50", "50"] for 2 units of 50ml each)
  - "req_date": request date in ISO format
  - "req_comp_id": numeric component ID (integer starting from 1)

Required fields: {', '.join(REQUIRED_FIELDS)}

IMPORTANT:
- Extract as many fields as possible from the document
- For fields like hospital address, patient address - extract the full address
- For component_details, if volume info exists and is_aliqout is true, split volumes into the "volume" array (one entry per unit)
- Do not guess or hallucinate values that are not in the document
- Return ONLY valid JSON, no markdown or extra text

RESPONSE FORMAT:
{{
  "updates": {{ "fieldName": "extractedValue" }},
  "reply": "Summary of what was extracted",
  "missingFields": ["list of required fields not found in document"]
}}"""


def get_chat_prompt(pending_field: Optional[str] = None) -> str:
    fields_desc = "\n".join(f"- {k}: {v}" for k, v in FIELD_LABELS.items())
    pending_info = f"\nCurrent pending field: {pending_field}" if pending_field else "\nCurrent pending field: none"

    return f"""You are a blood bank request form assistant.
You must respond ONLY with valid JSON. Do not include markdown, explanations, or extra text.
{pending_info}

Valid form fields:
{fields_desc}

RULES:
1. If pending field is set, treat the user's message as the answer to that field
2. For gender, normalize to: Male, Female, Other
3. For blood_group, normalize to standard format: A+, A-, B+, B-, O+, O-, AB+, AB-
4. For age_type, normalize to: Y (years), M (months), D (days)
5. For blood_request_type, use "1" for adult, "2" for neonatal
6. For dates, try to normalize to DD/MM/YYYY format
7. If user says "skip" or "n/a", set completed but don't update the field
8. If user says "submit", set submit: true
9. If user asks a question (contains ?), answer it in reply without updating fields
10. For component_details, expect format like "PRBC 2 units" or "Platelets 1 unit 50ml"

RESPONSE FORMAT (strict JSON):
{{
  "reply": "Your conversational response",
  "updates": {{ "fieldName": "value" }},
  "completed": ["fieldName"],
  "submit": false
}}"""


def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)


def get_model(system_instruction: str):
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_instruction,
    )


def parse_ai_json(text: str) -> Optional[dict]:
    try:
        cleaned = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
        cleaned = re.sub(r"```", "", cleaned).strip()
        match = re.search(r"\{[\s\S]*\}", cleaned)
        candidate = match.group(0) if match else cleaned
        return json.loads(candidate)
    except (json.JSONDecodeError, AttributeError):
        return None


def filter_updates(updates: dict) -> dict:
    filtered = {}
    for k, v in updates.items():
        if k not in VALID_FIELDS:
            continue
        if v is None:
            continue
        # Allow booleans, numbers, lists/dicts (component_details), and non-empty strings
        if isinstance(v, bool) or isinstance(v, (int, float)):
            filtered[k] = v
        elif isinstance(v, (list, dict)):
            filtered[k] = v
        elif isinstance(v, str) and v:
            filtered[k] = v
    return filtered


def get_missing_required(current_form: dict, updates: dict) -> list:
    merged = {**current_form, **updates}
    return [f for f in REQUIRED_FIELDS if not merged.get(f)]


async def extract_from_text(text: str, current_form: dict, api_key: str) -> dict:
    configure_gemini(api_key)
    model = get_model(get_extraction_prompt())

    prompt = f"""Extract form data from this document text.

Current form state (already filled):
{json.dumps(current_form, indent=2)}

Document text:
{text}"""

    response = model.generate_content(prompt)
    result = parse_ai_json(response.text)

    if not result:
        return {
            "updates": {},
            "missingFields": REQUIRED_FIELDS,
            "reply": "Could not extract data from the document. Please try a clearer document.",
        }

    updates = filter_updates(result.get("updates", {}))
    missing = get_missing_required(current_form, updates)

    return {
        "updates": updates,
        "missingFields": missing,
        "reply": result.get("reply", f"Extracted {len(updates)} field(s) from the document."),
    }


async def extract_from_image(image_bytes: bytes, current_form: dict, api_key: str, mime_type: str = "image/png") -> dict:
    configure_gemini(api_key)
    model = get_model(get_extraction_prompt())

    image_part = {
        "mime_type": mime_type,
        "data": image_bytes,
    }

    prompt = f"""Extract form data from this medical/blood bank document image.

Current form state (already filled):
{json.dumps(current_form, indent=2)}

Analyze the image and extract all relevant form fields."""

    response = model.generate_content([prompt, image_part])
    result = parse_ai_json(response.text)

    if not result:
        return {
            "updates": {},
            "missingFields": REQUIRED_FIELDS,
            "reply": "Could not extract data from the image. Please try a clearer image.",
        }

    updates = filter_updates(result.get("updates", {}))
    missing = get_missing_required(current_form, updates)

    return {
        "updates": updates,
        "missingFields": missing,
        "reply": result.get("reply", f"Extracted {len(updates)} field(s) from the image."),
    }


async def chat_response(user_message: str, current_form: dict, pending_field: Optional[str], is_question: bool, api_key: str) -> dict:
    configure_gemini(api_key)
    model = get_model(get_chat_prompt(pending_field))

    prompt = f"""User message: {user_message}

Current form state:
{json.dumps(current_form, indent=2)}

{"This is a question - answer it without updating fields." if is_question else "Process the user's input and update relevant fields."}"""

    response = model.generate_content(prompt)
    result = parse_ai_json(response.text)

    if not result:
        return {
            "reply": "I didn't understand that. Could you please rephrase?",
            "updates": {},
            "completed": [],
            "submit": False,
        }

    updates = filter_updates(result.get("updates", {}))

    return {
        "reply": result.get("reply", ""),
        "updates": updates,
        "completed": result.get("completed", []),
        "submit": result.get("submit", False),
    }
