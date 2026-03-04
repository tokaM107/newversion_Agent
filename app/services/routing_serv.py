"""Service that calls the Alexandria Routing API."""

import requests
from typing import Optional, List, Dict, Any

ROUTING_API_BASE = "https://routing-demo-eval.azurewebsites.net"
ROUTING_API_URL = f"{ROUTING_API_BASE}/api/routes"


def call_routing_api(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    walking_cutoff: int = 1000,
    max_transfers: int = 2,
    restricted_modes: Optional[List[str]] = None,
    top_k: int = 5
  
) -> Dict[str, Any]:
    """Call the routing API and return the JSON response.

    Returns the parsed JSON on success, or a dict with 'error' key on failure.
    """
    payload: Dict[str, Any] = {
        "start_lat": start_lat,
        "start_lon": start_lon,
        "end_lat": end_lat,
        "end_lon": end_lon,
        "max_transfers": max_transfers,
        "walking_cutoff": int(walking_cutoff),
        "top_k": top_k
    }

    if restricted_modes:
        payload["restricted_modes"] = restricted_modes

    print(f"[ROUTING API] POST {ROUTING_API_URL}")
    print(f"[ROUTING API] Payload: {payload}")

    try:
        resp = requests.post(ROUTING_API_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print(f"[ROUTING API] Success — status {resp.status_code}")
        return data

    except requests.exceptions.Timeout:
        print("[ROUTING API] Timeout")
        return {"error": "routing_api_timeout"}
    except requests.exceptions.HTTPError as e:
        print(f"[ROUTING API] HTTP error: {e} — {resp.text[:300]}")
        return {"error": f"routing_api_http_{resp.status_code}", "detail": resp.text[:500]}
    except Exception as e:
        print(f"[ROUTING API] Error: {e}")
        return {"error": "routing_api_error", "detail": str(e)}
