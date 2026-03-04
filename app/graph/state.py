from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict, total=False):
    query: str

    origin: Optional[str]
    destination: Optional[str]

    origin_geo: Optional[Dict[str, float]]
    destination_geo: Optional[Dict[str, float]]
    
    route_response: Optional[Dict[str, Any]]

    final_answer: Optional[str]
    formatted: Optional[str]
    error: Optional[str]

    walking_cutoff: Optional[float]
    max_transfers: Optional[int]
    restricted_modes: Optional[List[str]]
    top_k: Optional[int]

    find_route_args: Optional[Dict[str, Any]]

    requested_info: Optional[List[str]]  # e.g. ["price"], ["time", "transport_name"], or ["all"]
    scope: Optional[str]  # "partial" or "full" — set by check_answer_scope

    