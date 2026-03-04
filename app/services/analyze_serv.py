"""Service that calls the LLM to extract routing intent and parameters."""

import json
import os
from dotenv import load_dotenv
from google.genai import Client
from google.genai import types

load_dotenv()

ANALYZE_SYSTEM_PROMPT = """You are a routing intent and parameter extraction engine.

Your ONLY task is to analyze the user's message and extract parameters
for the following routing function:

find_route(
    start_lat,
    start_lon,
    end_lat,
    end_lon,
    walking_cutoff,
    max_transfers,
    restricted_modes,
    top_k
)

Rules (VERY IMPORTANT):
- Do NOT answer the user.
- Do NOT explain anything.
- Do NOT guess or infer values that are not explicitly mentioned.
- Do NOT invent numbers.
- If a value is not clearly stated by the user, set it to null.
- Do NOT translate place names.
- Return ONLY valid JSON.
- Follow the schema EXACTLY.

Interpretation rules:
- Extract origin and destination as place names only.
- Coordinates (lat/lon) must ALWAYS be a coordinate pair from the previous node in this step.
- walking_cutoff MUST be 1000 unless the user provides an explicit numeric value (e.g. "500 متر").
- max_transfers MUST be 2 unless the user provides an explicit numeric value.
- If the user mentions "من غير مشي كتير" or "أقل مشي" WITHOUT a number, keep walking_cutoff = 1000.
- If the user mentions "مواصلات قليلة" WITHOUT a number, keep max_transfers = 2.
- restricted_modes should only be filled if the user explicitly mentions a transport mode to avoid (e.g. "من غير مترو").

Response info rules:
- Determine what specific information the user is asking about.
- If the user asks about price/cost ("بكام", "السعر", "التكلفة"), add "price" to requested_info.
- If the user asks about time/duration ("هياخد قد ايه", "الوقت", "المدة"), add "time" to requested_info.
- If the user asks about transport name/type ("اركب ايه", "اسم المواصلة", "نوع المواصلة"), add "transport_name" to requested_info.
- If the user asks about number of stops ("كام محطة"), add "stops" to requested_info.
- If the user asks about walking distance ("هامشي قد ايه"), add "walking" to requested_info.
- If the user asks a general routing question ("ازاي اروح", "عايز اروح") with NO specific info request, set requested_info to ["all"].
- requested_info must ALWAYS be a non-empty array.

Output JSON schema:

{
  "origin": string | null,
  "destination": string | null,
  "requested_info": string[],
  "find_route_args": {
    "start_lat": number | null,
    "start_lon": number | null,
    "end_lat": number | null,
    "end_lon": number | null,
    "walking_cutoff": number | null,
    "max_transfers": number | null,
    "restricted_modes": string[] | null,
    "top_k": number | null
  }
}
"""

client = Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


def llm_analyze(user_input: str) -> dict:
    """Send the user message to the LLM and return structured routing parameters.

    Returns a dict with keys: origin, destination, find_route_args.
    On failure every value defaults to None.
    """
    empty = {
        "origin": None,
        "destination": None,
        "requested_info": ["all"],
        "find_route_args": {
            "start_lat": None,
            "start_lon": None,
            "end_lat": None,
            "end_lon": None,
            "walking_cutoff": None,
            "max_transfers": None,
            "restricted_modes": None,
            "top_k": None,
        },
    }

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[user_input],
            config=types.GenerateContentConfig(
                system_instruction=ANALYZE_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )

        parsed = json.loads(response.text)
        args = parsed.get("find_route_args", {})

        return {
            "origin": parsed.get("origin"),
            "destination": parsed.get("destination"),
            "requested_info": parsed.get("requested_info", ["all"]),
            "find_route_args": {
                "start_lat": args.get("start_lat"),
                "start_lon": args.get("start_lon"),
                "end_lat": args.get("end_lat"),
                "end_lon": args.get("end_lon"),
                "walking_cutoff": args.get("walking_cutoff"),
                "max_transfers": args.get("max_transfers"),
                "restricted_modes": args.get("restricted_modes"),
                "top_k": args.get("top_k"),
            },
        }

    except Exception as e:
        print(f"[LLM ANALYZE ERROR] {e}")
        return empty
