"""Service that uses the LLM to filter route engine output to only the info the user asked for."""

import json
import os
from dotenv import load_dotenv
from google.genai import Client
from google.genai import types
from typing import List, Dict, Any

load_dotenv()

FILTER_SYSTEM_PROMPT = """You are a response formatting engine for a transit routing system in Alexandria, Egypt.

You will receive:
1. The user's original question.
2. The full route response from the routing engine (JSON).
3. A list of requested_info fields the user cares about.

Possible requested_info values:
- "price"          → return the fare / cost of each route
- "time"           → return the expected duration of each route
- "transport_name" → return the names / types of transport used
- "walking"        → return walking distance / time info
- "all"            → return the full route (should not reach this filter)

CRITICAL RULES for a good answer:
1. For EVERY journey, ALWAYS include a brief trip description so the user can tell them apart.
   Use the text_summary or describe the transport (e.g. "اتوبيس 739 من محطة مصر لكوبري كليوبترا").
2. Then show the specific requested info (time, price, etc.).
3. If there is walking involved, mention it briefly (e.g. "بعد ما تمشي 4 دقايق").
4. If there are transfers, mention them.
5. Respond in Egyptian Arabic, in a friendly and clear way.
6. Format the answer as readable numbered list.
7. Do NOT make up data — use only what is in the route response.
8. At the end, add a brief recommendation for the best option based on the requested info
   (e.g. fastest if they asked about time, cheapest if they asked about price).
"""

client = Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


def llm_filter_response(
    user_query: str,
    route_response: Dict[str, Any],
    requested_info: List[str],
) -> str:
    """Filter the route engine response to only the info the user asked for.

    Returns a human-readable Arabic string.
    """
    # Build a compact version of the route data (strip path arrays to save tokens)
    compact_journeys = []
    for j in route_response.get("journeys", []):
        compact_legs = []
        for leg in j.get("legs", []):
            leg_copy = {k: v for k, v in leg.items() if k != "path"}
            compact_legs.append(leg_copy)
        compact_journeys.append({
            "id": j.get("id"),
            "text_summary": j.get("text_summary"),
            "summary": j.get("summary"),
            "legs": compact_legs,
        })

    compact_response = {
        "num_journeys": route_response.get("num_journeys"),
        "journeys": compact_journeys,
    }

    prompt = (
        f"سؤال المستخدم: {user_query}\n\n"
        f"المعلومات المطلوبة: {json.dumps(requested_info, ensure_ascii=False)}\n\n"
        f"نتيجة محرك الرحلات:\n{json.dumps(compact_response, ensure_ascii=False, indent=2, default=str)}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=FILTER_SYSTEM_PROMPT,
                temperature=0.3,
            ),
        )
        return response.text.strip()

    except Exception as e:
        print(f"[LLM FILTER ERROR] {e}")
        return "حصل مشكلة في تصفية النتائج. جرّب تاني."
