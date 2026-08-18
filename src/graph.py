"""Identity and skill graph traversal engine for ScrollSense Phase 3."""

from __future__ import annotations

from typing import Any, Dict, List, Set

from src.loaders import load_identity_graph


def select_seed_nodes(interest_state: Dict[str, Any], graph_node_ids: Set[str]) -> List[Dict[str, Any]]:
    """Select seed nodes from high-confidence InterestState dimensions."""
    seeds: Dict[str, float] = {}

    # 1. Professional identity dimensions (weight >= 0.5)
    for ident, w in interest_state.get("professional_identity", {}).items():
        if w >= 0.5 and ident in graph_node_ids:
            seeds[ident] = max(seeds.get(ident, 0.0), float(w))

    # 2. Career stage dimensions (weight >= 0.5)
    for stage, w in interest_state.get("career_stage", {}).items():
        if w >= 0.5 and stage in graph_node_ids:
            seeds[stage] = max(seeds.get(stage, 0.0), float(w))

    # 3. Domain dimensions (weight >= 0.5)
    for dom, w in interest_state.get("domains", {}).items():
        if w >= 0.5 and dom in graph_node_ids:
            seeds[dom] = max(seeds.get(dom, 0.0), float(w))

    # Fallback if no strong seed found (e.g. single weak meme like R1)
    if not seeds:
        for ident, w in interest_state.get("professional_identity", {}).items():
            if ident in graph_node_ids:
                seeds[ident] = float(w)
        for dom, w in interest_state.get("domains", {}).items():
            if dom in graph_node_ids:
                seeds[dom] = max(seeds.get(dom, 0.0), float(w))

    # Return sorted seeds
    sorted_seeds = sorted(seeds.items(), key=lambda x: x[1], reverse=True)
    return [{"node": k, "weight": round(v, 3)} for k, v in sorted_seeds]


def traverse_identity_graph(interest_state: Dict[str, Any]) -> Dict[str, Any]:
    """Perform deterministic one-hop traversal from seed nodes across identity graph."""
    graph_data = load_identity_graph()
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    graph_node_ids = {n["id"] for n in nodes if "id" in n}
    seeds = select_seed_nodes(interest_state, graph_node_ids)

    activations: Dict[str, Dict[str, Any]] = {}

    # Map edges by source node
    edge_map: Dict[str, List[Dict[str, Any]]] = {}
    for e in edges:
        src = e.get("from")
        if src:
            edge_map.setdefault(src, []).append(e)

    for seed_entry in seeds:
        seed_node = seed_entry["node"]
        seed_weight = seed_entry["weight"]

        for edge in edge_map.get(seed_node, []):
            target = edge.get("to")
            edge_weight = float(edge.get("weight", 1.0))
            if not target:
                continue

            act_delta = seed_weight * edge_weight
            if target not in activations or activations[target]["activation"] < act_delta:
                activations[target] = {
                    "node": target,
                    "activation": round(act_delta, 3),
                    "via": seed_node,
                    "relation": edge.get("relation", ""),
                }

    sorted_activated = sorted(
        activations.values(), key=lambda x: x["activation"], reverse=True
    )

    return {
        "seed_nodes": seeds,
        "activated_nodes": sorted_activated,
    }
