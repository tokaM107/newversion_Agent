#geocode.py
import time

from app.services.geocoding_serv import geocode_address
from app.graph.state import AgentState

def geocode_node(state: AgentState) -> AgentState:
    start = time.time()
    origin = state.get("origin")
    destination = state.get("destination")

    if not origin and not destination:
        print("[GEOCODE] Skipping - no origin and no destination")
        return state

    print(f"[GEOCODE] Starting geocode for: {origin} -> {destination}")

    # --- Geocode origin (if provided) ---
    if origin:
        s = geocode_address(origin) or {"error": True}
        print(f"[GEOCODE] Origin done in {time.time()-start:.1f}s: {s}")
        state["origin_geo"] = None if "error" in s else {"lat": s["lat"], "lon": s["lon"]}
    else:
        state["origin_geo"] = None

    # --- Geocode destination (if provided) ---
    if destination:
        e = geocode_address(destination) or {"error": True}
        print(f"[GEOCODE] Destination done in {time.time()-start:.1f}s: {e}")
        state["destination_geo"] = None if "error" in e else {"lat": e["lat"], "lon": e["lon"]}
    else:
        state["destination_geo"] = None

    # --- Always build find_route_args matching find_route() signature ---
    og = state.get("origin_geo")
    dg = state.get("destination_geo")

    state["find_route_args"] = {
        "start_lat": og["lat"] if og else None,
        "start_lon": og["lon"] if og else None,
        "end_lat":   dg["lat"] if dg else None,
        "end_lon":   dg["lon"] if dg else None,
        "walking_cutoff":  state.get("walking_cutoff", 1000.0),
        "max_transfers":   state.get("max_transfers", 2),
        "restricted_modes": state.get("restricted_modes"),
        "weights":          None,
        "top_k":            state.get("top_k", 5),
    }
    print(f"[GEOCODE] find_route_args built: {state['find_route_args']}")

    # --- Set error if any coordinate is still missing ---
    if og is None and dg is None:
        state["error"] = "geocoding_failed"
        state["final_answer"] = "تعذّر تحديد المواقع. جرّب أسماء أدق."
    elif og is None:
        state["error"] = "missing_origin_coords"
        if not state.get("final_answer"):
            state["final_answer"] = "ماذكرتش هتبدأ منين. ممكن تقولي نقطة البداية؟"
    elif dg is None:
        state["error"] = "missing_destination_coords"
        if not state.get("final_answer"):
            state["final_answer"] = "تعذّر تحديد موقع الوجهة. جرّب اسم أدق."

    print(f"[GEOCODE] Complete in {time.time()-start:.1f}s")
    return state
