# decision.py
"""Decision node – routes the graph based on state completeness and scope."""

from app.graph.state import AgentState


def check_completeness(state: AgentState) -> str:
    """Return 'ask_user' if any required coordinate is missing, else 'ready'.

    This is used as a conditional edge after geocode.
    """
    args = state.get("find_route_args", {})

    has_start = args.get("start_lat") is not None and args.get("start_lon") is not None
    has_end   = args.get("end_lat")   is not None and args.get("end_lon")   is not None

    if not has_start or not has_end:
        print(f"[DECISION] Missing coords → ask_user  (start={has_start}, end={has_end})")
        return "ask_user"

    print("[DECISION] All coords present → ready")
    return "ready"


def check_answer_scope(state: AgentState) -> str:
    """Return 'partial' or 'full' based on what info the user asked for.

    partial = user wants specific info (price, time, transport_name, etc.)
    full    = user wants the complete route (requested_info contains 'all')

    This is used as a conditional edge after check_completeness → ready.
    """
    requested = state.get("requested_info", ["all"])

    if "all" in requested:
        label = "full"
    else:
        label = "partial"

    state["scope"] = label
    print(f"[SCOPE] requested_info={requested} → {label}")
    return label


def ask_user_node(state: AgentState) -> AgentState:
    """Terminal node that returns the follow-up question already set in state."""
    # final_answer was already populated by analyze or geocode
    if not state.get("final_answer"):
        state["final_answer"] = "محتاج معلومات أكتر. ممكن توضّح نقطة البداية والوجهة؟"
    print(f"[ASK_USER] → {state['final_answer']}")
    return state
