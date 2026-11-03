"""
algorithms/graph_algorithms/prim.py
-----------------------------------
Prim's Minimum Spanning Tree algorithm trace generator.

Core idea: Grow one tree starting from a single vertex, repeatedly picking
the cheapest available edge connecting the tree to an unvisited vertex.
"""

from typing import Dict, List, Any
from core.step_model import VisualizationStep, RenderData
from algorithms.graph_algorithms.graphs import get_graph_preset


def prim_trace(graph_name: str = "Network Backbone", start_node: str = "A", custom_edges: str = "") -> List[VisualizationStep]:
    """Generates an intuitive, pedagogical step-by-step trace of Prim's algorithm."""
    g = get_graph_preset(graph_name, custom_text=custom_edges)
    nodes = g["nodes"]
    edges = g["edges"]

    # Validate start node
    valid_ids = [n["id"] for n in nodes]
    if start_node not in valid_ids:
        start_node = valid_ids[0] if valid_ids else "A"

    steps: List[VisualizationStep] = []
    step_idx = 1

    # Snapshot helper for RenderData
    def make_snapshot(visited_set, selected_edges_set, active_edge=None, candidate_edges=None,
                      status_text="", comparison_text="", structure_label="Available Cut Edges (Connecting to Outside)",
                      chips=None, total_weight=0):
        c_edges = candidate_edges or []
        node_payloads = []
        for n in nodes:
            nid = n["id"]
            if nid in visited_set:
                st = "visited"
            elif any(nid in (ce["u"], ce["v"]) for ce in c_edges):
                st = "frontier"
            else:
                st = "unvisited"
            node_payloads.append({
                "id": nid,
                "x": n["x"],
                "y": n["y"],
                "state": st,
                "label": nid,
            })

        edge_payloads = []
        for e in edges:
            u, v, w = e["u"], e["v"], e["weight"]
            pair = (min(u, v), max(u, v))
            if pair in selected_edges_set:
                estate = "selected"  # Emerald Green in MST
            elif active_edge and pair == (min(active_edge["u"], active_edge["v"]), max(active_edge["u"], active_edge["v"])):
                estate = "active"    # Purple highlight currently evaluated
            elif any(pair == (min(ce["u"], ce["v"]), max(ce["u"], ce["v"])) for ce in c_edges):
                estate = "candidate" # Amber dash connecting to unvisited
            elif u in visited_set and v in visited_set:
                estate = "idle"      # Inside tree, not chosen
            else:
                estate = "unvisited" # Outside tree

            edge_payloads.append({
                "u": u,
                "v": v,
                "weight": w,
                "state": estate,
            })

        gd = {
            "type": "prim",
            "title": "Prim's Algorithm (Minimum Spanning Tree)",
            "status_text": status_text,
            "comparison_text": comparison_text,
            "structure_label": structure_label,
            "chips": chips or [],
            "nodes": node_payloads,
            "edges": edge_payloads,
            "total_weight": total_weight,
        }
        return RenderData(mode="graph", graph_data=gd)

    # ------------------------------------------------------------------
    # Step 0: Conceptual Introduction
    # ------------------------------------------------------------------
    intro_explanation = (
        "Core Idea: Grow one tree from a starting vertex by repeatedly adding the cheapest edge that connects to an unvisited vertex.\n\n"
        "How Prim's Algorithm works:\n"
        "1. Select any vertex as the starting vertex.\n"
        "2. Look at all edges connecting a vertex already in the MST to a vertex outside it.\n"
        "3. Select the edge with the minimum weight.\n"
        "4. Add that edge and the new vertex to the MST.\n"
        "5. Repeat until all vertices have been included.\n\n"
        "Important condition: Never select an edge connecting two vertices already in the MST, as this would create a cycle!"
    )
    steps.append(VisualizationStep(
        index=step_idx,
        title="Introduction — Prim's Algorithm for Minimum Spanning Trees",
        equation="Goal: Connect all vertices with minimum total edge weight and zero cycles",
        explanation=intro_explanation,
        values={"mst_weight": 0, "edges_count": 0, "graph_name": graph_name},
        render_data=make_snapshot(
            set(), set(),
            status_text=f"Prim's Algorithm: Ready to grow MST on {graph_name} ({len(nodes)} vertices, {len(edges)} edges).",
            comparison_text=f"Starting at vertex '{start_node}'.",
            chips=["Select start vertex to begin"],
            total_weight=0,
        ),
        metrics={"Vertices in MST": 0, "Total Weight": 0, "Target Edges": len(nodes) - 1}
    ))
    step_idx += 1

    # Initialize at start_node
    visited = {start_node}
    selected_edges = set()  # set of (min(u,v), max(u,v))
    total_weight = 0

    def get_cut_edges():
        cut = []
        for e in edges:
            u, v, w = e["u"], e["v"], e["weight"]
            u_in = u in visited
            v_in = v in visited
            if (u_in and not v_in) or (v_in and not u_in):
                cut.append(e)
        cut.sort(key=lambda x: (x["weight"], x["u"], x["v"]))
        return cut

    cut_edges = get_cut_edges()
    chips = [f"{e['u']}-{e['v']}:{e['weight']}" for e in cut_edges]
    cut_edges_desc = ', '.join([f"Edge {e['u']}-{e['v']} (weight {e['weight']})" for e in cut_edges])

    steps.append(VisualizationStep(
        index=step_idx,
        title=f"Step 1: Start Prim's Algorithm at Vertex '{start_node}'",
        equation=f"MST Vertices: {{{start_node}}}  |  Candidate Cut Edges: {', '.join(chips)}",
        explanation=(
            f"1. What are we doing? We begin our Minimum Spanning Tree at vertex '{start_node}'.\n"
            f"2. Why start here? Prim's algorithm can start from ANY vertex and will always find the exact same minimum spanning tree total weight.\n"
            f"3. Candidate Edges: The available edges leading to unvisited vertices are {cut_edges_desc}.\n"
            f"4. What happens next? We will select the cheapest available connecting edge."
        ),
        values={"start": start_node, "cut_edges": len(cut_edges)},
        render_data=make_snapshot(
            visited, selected_edges, candidate_edges=cut_edges,
            status_text=f"Started at vertex '{start_node}'. {len(cut_edges)} edge(s) lead to unvisited vertices.",
            comparison_text="Always select the minimum-weight connecting edge next.",
            chips=chips,
            total_weight=0,
        ),
        metrics={"Vertices in MST": len(visited), "Total Weight": total_weight, "Target Edges": len(nodes) - 1}
    ))
    step_idx += 1

    # Main Prim's loop: exactly |V| - 1 iterations
    step_counter = 2
    while len(visited) < len(nodes):
        cut_edges = get_cut_edges()
        if not cut_edges:
            break

        best_edge = cut_edges[0]
        u, v, w = best_edge["u"], best_edge["v"], best_edge["weight"]
        new_node = v if u in visited else u
        from_node = u if u in visited else v
        pair = (min(u, v), max(u, v))

        chips = [f"{e['u']}-{e['v']}:{e['weight']}" for e in cut_edges]
        chips[0] = f"★ {chips[0]} [MIN]"
        avail_str = ', '.join([f"{e['u']}-{e['v']}:{e['weight']}" for e in cut_edges])
        cut_edges_desc = ', '.join([f"Edge {e['u']}-{e['v']} (weight {e['weight']})" for e in cut_edges])
        visited_nodes_str = str(sorted(list(visited)))

        # Sub-step A: Explain the decision to choose the minimum-weight cut edge
        steps.append(VisualizationStep(
            index=step_idx,
            title=f"Step {step_counter}A: Evaluate Connecting Edges — Minimum is Edge {u}-{v} (weight {w})",
            equation=f"Available Edges: {avail_str}  →  Cheapest: {u}-{v} (weight {w})",
            explanation=(
                f"1. What are we trying to do? Find the cheapest edge connecting vertices already in our tree {visited_nodes_str} to an unvisited vertex.\n"
                f"2. Candidate Edges: Comparing weights: {cut_edges_desc}.\n"
                f"3. Why select Edge {u}-{v}? It has the smallest weight ({w}) among all edges crossing to unvisited vertices.\n"
                f"4. What happens next? We will add Edge {u}-{v} and vertex '{new_node}' to the Minimum Spanning Tree."
            ),
            values={"best_edge": f"{u}-{v}", "weight": w},
            render_data=make_snapshot(
                visited, selected_edges, active_edge=best_edge, candidate_edges=cut_edges,
                status_text=f"Inspecting candidate edges: Edge {u}-{v} with weight {w} is the minimum.",
                comparison_text=f"Connecting vertex '{new_node}' will add +{w} to total MST weight.",
                chips=chips,
                total_weight=total_weight,
            ),
            metrics={"Vertices in MST": len(visited), "Total Weight": total_weight, "Target Edges": len(nodes) - 1}
        ))
        step_idx += 1

        # Sub-step B: Officially add the edge and new vertex to MST
        selected_edges.add(pair)
        visited.add(new_node)
        total_weight += w

        remaining_cut = get_cut_edges()
        new_chips = [f"{e['u']}-{e['v']}:{e['weight']}" for e in remaining_cut]

        steps.append(VisualizationStep(
            index=step_idx,
            title=f"Step {step_counter}B: Add Edge {u}-{v} and Vertex '{new_node}' to MST",
            equation=f"Edge {u}-{v} with weight {w} was selected  |  Total MST Weight = {total_weight}",
            explanation=(
                f"1. Decision: Edge {u}-{v} with weight {w} was selected because it is the minimum-weight edge connecting the current MST to an unvisited vertex.\n"
                f"2. Tree Growth: Vertex '{new_node}' is now added to the Minimum Spanning Tree.\n"
                f"3. Progress: {len(selected_edges)} of {len(nodes) - 1} target edges selected (Total MST Weight = {total_weight})."
            ),
            values={"added_vertex": new_node, "added_edge": f"{u}-{v}", "total_weight": total_weight},
            render_data=make_snapshot(
                visited, selected_edges, active_edge=None, candidate_edges=remaining_cut,
                status_text=f"Added Edge {u}-{v} (weight {w}) and Vertex '{new_node}'. Total weight: {total_weight}.",
                comparison_text=f"Progress: {len(selected_edges)} of {len(nodes) - 1} edges selected.",
                chips=new_chips,
                total_weight=total_weight,
            ),
            metrics={"Vertices in MST": len(visited), "Total Weight": total_weight, "Target Edges": len(nodes) - 1}
        ))
        step_idx += 1
        step_counter += 1

    # ------------------------------------------------------------------
    # Final Step: MST Complete
    # ------------------------------------------------------------------
    edge_list_str = ", ".join([f"{u}-{v}" for (u, v) in sorted(list(selected_edges))])
    steps.append(VisualizationStep(
        index=step_idx,
        title="Minimum Spanning Tree Complete via Prim's Algorithm!",
        equation=f"MST Completed: Exactly {len(selected_edges)} Edges  |  Total Weight = {total_weight}",
        explanation=(
            f"All {len(nodes)} vertices have been successfully connected into a single spanning tree!\n\n"
            f"• Total MST Weight: {total_weight}\n"
            f"• Number of Edges: Exactly V - 1 = {len(selected_edges)} edges\n"
            f"• Selected Edges: {edge_list_str}\n"
            f"• Condition Verified: Every vertex is reached with zero cycles, achieving the lowest possible total network cost."
        ),
        values={"final_weight": total_weight, "selected_edges": list(selected_edges)},
        render_data=make_snapshot(
            visited, selected_edges, active_edge=None, candidate_edges=[],
            status_text=f"Minimum Spanning Tree Complete! Total Weight = {total_weight}.",
            comparison_text=f"Connected all {len(nodes)} vertices using exactly {len(selected_edges)} edges without cycles.",
            chips=[f"Total Weight = {total_weight}"],
            total_weight=total_weight,
        ),
        metrics={"Vertices in MST": len(visited), "Total Weight": total_weight, "Target Edges": len(nodes) - 1}
    ))

    return steps
