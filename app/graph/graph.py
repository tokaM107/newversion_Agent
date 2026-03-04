from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import analyze, geocode, decision, route, response


def _route_after_geocode(state: AgentState) -> str:
    """Combined decision: completeness first, then route to ask_user or route node."""
    completeness = decision.check_completeness(state)
    if completeness == "ask_user":
        return "ask_user"
    return "route"


def _route_after_engine(state: AgentState) -> str:
    """After the routing engine, decide partial or full response."""
    if state.get("error"):
        return "full_response"  # show error as final_answer
    scope = decision.check_answer_scope(state)
    return "filter_response" if scope == "partial" else "full_response"


def build_graph():
    graph = StateGraph(AgentState)

    # ── Nodes ──────────────────────────────────────────────
    graph.add_node("analyze",         analyze.analyze_node)          # LLM_extract
    graph.add_node("geocode",         geocode.geocode_node)          # resolve coords
    graph.add_node("ask_user",        decision.ask_user_node)        # return question
    graph.add_node("route",           route.route_node)              # call routing API
    graph.add_node("filter_response", response.filter_response_node) # LLM filters output
    graph.add_node("full_response",   response.full_response_node)   # return everything

    # ── Edges ──────────────────────────────────────────────
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "geocode")

    # After geocode → check completeness
    graph.add_conditional_edges(
        "geocode",
        _route_after_geocode,
        {
            "ask_user": "ask_user",
            "route":    "route",
        },
    )

    # After route → check scope for response type
    graph.add_conditional_edges(
        "route",
        _route_after_engine,
        {
            "filter_response": "filter_response",
            "full_response":   "full_response",
        },
    )

    graph.add_edge("ask_user", END)
    graph.add_edge("filter_response", END)
    graph.add_edge("full_response", END)

    return graph.compile()
