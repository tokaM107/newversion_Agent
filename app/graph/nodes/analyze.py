# analyze.py
"""Graph node that analyzes the user query to extract routing parameters."""

import time

from app.services.analyze_serv import llm_analyze
from app.graph.state import AgentState


def analyze_node(state: AgentState) -> AgentState:
    """Use the LLM to extract origin, destination and routing parameters."""

    query = state.get("query", "")
    print(f"[ANALYZE] Starting analysis for query: {query[:80]}")
    start = time.time()

    result = llm_analyze(query)
    args = result.get("find_route_args", {})

    requested_info = result.get("requested_info", ["all"])

    print(
        f"[ANALYZE] Done in {time.time() - start:.1f}s -> "
        f"origin={result.get('origin')}, dest={result.get('destination')}, "
        f"requested_info={requested_info}, "
        f"walking_cutoff={args.get('walking_cutoff')}, "
        f"max_transfers={args.get('max_transfers')}, "
        f"restricted_modes={args.get('restricted_modes')}, "
        f"top_k={args.get('top_k')}"
    )

    # Populate state with extracted values
    state["origin"] = result.get("origin")
    state["destination"] = result.get("destination")
    state["requested_info"] = requested_info

    # Apply find_route defaults for any null routing parameters
    state["walking_cutoff"] = args.get("walking_cutoff") if args.get("walking_cutoff") is not None else 1000.0
    state["max_transfers"] = args.get("max_transfers") if args.get("max_transfers") is not None else 2
    state["restricted_modes"] = args.get("restricted_modes")  # None is a valid default
    state["top_k"] = args.get("top_k") if args.get("top_k") is not None else 5

    # If the LLM already returned explicit coordinates, store them
    if args.get("start_lat") is not None and args.get("start_lon") is not None:
        state["origin_geo"] = {
            "lat": args["start_lat"],
            "lon": args["start_lon"],
        }
    if args.get("end_lat") is not None and args.get("end_lon") is not None:
        state["destination_geo"] = {
            "lat": args["end_lat"],
            "lon": args["end_lon"],
        }

    # Mark an error if we couldn't extract either endpoint
    if not state.get("origin") and not state.get("destination"):
        state["error"] = "analyze_failed"
        state["final_answer"] = "معرفتش أفهم نقطة البداية ولا الوصول. ممكن توضّح أكتر؟"
    elif not state.get("origin"):
        state["error"] = "missing_origin"
        state["final_answer"] = "ماذكرتش هتبدأ منين. ممكن تقولي نقطة البداية؟"
    elif not state.get("destination"):
        state["error"] = "missing_destination"
        state["final_answer"] = "ماذكرتش رايح فين. ممكن تقولي الوجهة؟"

    return state
