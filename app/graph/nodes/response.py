# response.py
"""Graph nodes for formatting the routing engine output."""

from app.services.filter_serv import llm_filter_response
from app.graph.state import AgentState
import json


def filter_response_node(state: AgentState) -> AgentState:
    """LLM filters the route response to only the info the user asked for."""
    route_resp = state.get("route_response")
    if not route_resp:
        state["final_answer"] = "مفيش نتائج من محرك الرحلات."
        return state

    query = state.get("query", "")
    requested = state.get("requested_info", ["all"])

    print(f"[FILTER] Filtering route response for: {requested}")
    filtered = llm_filter_response(query, route_resp, requested)

    state["final_answer"] = filtered
    print(f"[FILTER] Done → {filtered[:120]}...")
    return state


def full_response_node(state: AgentState) -> AgentState:
    """Return the full route response as readable Arabic text using text_summary."""
    route_resp = state.get("route_response")
    if not route_resp:
        state["final_answer"] = "مفيش نتائج من محرك الرحلات."
        return state

    journeys = route_resp.get("journeys", [])
    if not journeys:
        state["final_answer"] = "مفيش رحلات متاحة للمسار ده."
        return state

    print(f"[FULL_RESPONSE] Formatting {len(journeys)} journeys")

    lines = []
    for j in journeys:
        idx = j.get("id", "")
        summary = j.get("summary", {})
        text = j.get("text_summary", "")
        cost = summary.get("cost", "?")
        time_min = summary.get("total_time_minutes", "?")
        walk_m = summary.get("walking_distance_meters", "?")
        transfers = summary.get("transfers", 0)
        modes = ", ".join(summary.get("modes", []))

        lines.append(
            f"🚏 رحلة {idx}:\n"
            f"   {text}\n"
            f"   ⏱ الوقت: {time_min} دقيقة | 💰 التكلفة: {cost} جنيه | "
            f"🚶 مشي: {walk_m} متر | 🔄 تحويلات: {transfers} | 🚌 وسيلة: {modes}"
        )

    state["final_answer"] = "\n\n".join(lines)
    return state
