"""Full pipeline test: analyze → geocode → decision → route → response."""

import sys, os, json

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from app.graph.nodes.analyze import analyze_node
from app.graph.nodes.geocode import geocode_node
from app.graph.nodes.decision import check_completeness, check_answer_scope, ask_user_node
from app.graph.nodes.route import route_node
from app.graph.nodes.response import filter_response_node, full_response_node


def run_pipeline(query: str):
    state = {"query": query}

    print("=" * 60)
    print(f"QUERY: {query}")
    print("=" * 60)

    # Step 1 – Analyze (LLM_extract)
    state = analyze_node(state)
    print("\n--- State after ANALYZE ---")
    print(json.dumps({k: state[k] for k in ["origin", "destination", "requested_info",
                      "walking_cutoff", "max_transfers", "restricted_modes", "top_k"]
                      if k in state}, ensure_ascii=False, indent=2, default=str))

    # Step 2 – Geocode
    state = geocode_node(state)

    # Step 3 – check_completeness
    completeness = check_completeness(state)
    print(f"\n>>> check_completeness → {completeness}")

    if completeness == "ask_user":
        state = ask_user_node(state)
        print(f"\n💬 AGENT SAYS: {state.get('final_answer')}")
        return state

    # Step 4 – Route (call routing API)
    state = route_node(state)

    if state.get("error"):
        print(f"\n❌ ROUTE ERROR: {state.get('error')}")
        print(f"💬 AGENT SAYS: {state.get('final_answer')}")
        return state

    # Step 5 – check_answer_scope → filter or full
    scope = check_answer_scope(state)
    print(f"\n>>> check_answer_scope → {scope}")

    if scope == "partial":
        state = filter_response_node(state)
    else:
        state = full_response_node(state)

    print(f"\n{'=' * 60}")
    print(f"💬 FINAL ANSWER:")
    print(state.get("final_answer", "No answer"))
    print(f"{'=' * 60}")
    return state


# ── Test: full query with both endpoints ──
print("\n\n🔹 TEST: Full pipeline")
# run_pipeline("عايز اروح محطة مصر لحد سيدي جابر من غير ما اركب ترام")

run_pipeline("ممكن اركب ايه من محرم بك امشي اقل مسافة لحد محطة الرمل؟")
