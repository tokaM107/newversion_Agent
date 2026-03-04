# route.py
"""Graph node that calls the routing API."""

import time

from app.services.routing_serv import call_routing_api
from app.graph.state import AgentState


def route_node(state: AgentState) -> AgentState:
    """Call the routing engine API using find_route_args from state."""

    args = state.get("find_route_args", {})
    if not args or args.get("start_lat") is None or args.get("end_lat") is None:
        state["error"] = "route_missing_coords"
        state["final_answer"] = "مفيش إحداثيات كافية لطلب الرحلة."
        return state

    print(f"[ROUTE] Calling routing API...")
    start = time.time()

    result = call_routing_api(
        start_lat=args["start_lat"],
        start_lon=args["start_lon"],
        end_lat=args["end_lat"],
        end_lon=args["end_lon"],
        walking_cutoff=int(args.get("walking_cutoff", 1200)),
        max_transfers=int(args.get("max_transfers", 3)),
        restricted_modes=args.get("restricted_modes"),
        top_k=int(args.get("top_k", 5)),
    )

    elapsed = time.time() - start
    print(f"[ROUTE] API responded in {elapsed:.1f}s")

    if result.get("error"):
        state["error"] = result["error"]
        state["final_answer"] = "حصل مشكلة في محرك الرحلات. جرّب تاني."
        print(f"[ROUTE] Error: {result}")
    else:
        state["route_response"] = result
        num = result.get("num_journeys", 0)
        print(f"[ROUTE] Got {num} journeys")

    return state
