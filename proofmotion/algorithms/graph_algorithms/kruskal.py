"""
algorithms/graph_algorithms/kruskal.py
--------------------------------------
Kruskal's Minimum Spanning Tree algorithm trace generator.

Core idea: Select the cheapest edges across the entire graph in ascending order,
adding each edge unless it connects two vertices already in the same component
(which would form a cycle).
"""

from typing import Dict, List, Any
from core.step_model import VisualizationStep, RenderData
from algorithms.graph_algorithms.graphs import get_graph_preset


class DisjointSet:
    """Disjoint Set Union (DSU) / Union-Find with path compression."""
    def __init__(self, elements):
        self.parent = {x: x for x in elements}
        self.rank = {x: 0 for x in elements}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # Already in same component (cycle!)
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1
        return True


def kruskal_trace(graph_name: str = "Network Backbone", custom_edges: str = "") -> List[VisualizationStep]:
    """Generates an intuitive, pedagogical step-by-step trace of Kruskal's algorithm."""
    g = get_graph_preset(graph_name, custom_text=custom_edges)
    nodes = g["nodes"]
    edges = g["edges"]
    node_ids = [n["id"] for n in nodes]

    # 1. Sort all edges globally in ascending order of weight
    sorted_edges = sorted(edges, key=lambda e: (e["weight"], e["u"], e["v"]))
    dsu = DisjointSet(node_ids)

    selected_edges = set()   # set of (min(u,v), max(u,v))
    rejected_edges = set()   # set of (min(u,v), max(u,v))
    total_weight = 0

    steps: List[VisualizationStep] = []
    step_idx = 1

    def make_snapshot(active_edge=None, active_state="active", status_text="", comparison_text="",
                      remaining_edges=None):
        node_payloads = []
        for n in nodes:
            nid = n["id"]
            # Color nodes by their connected component
            node_payloads.append({
                "id": nid,
                "x": n["x"],
                "y": n["y"],
                "state": "visited" if any(nid in (min(u, v), max(u, v)) for (u, v) in selected_edges) else "unvisited",
                "label": nid,
            })

        edge_payloads = []
        for e in edges:
            u, v, w = e["u"], e["v"], e["weight"]
            pair = (min(u, v), max(u, v))
            if pair in selected_edges:
                estate = "selected"  # Emerald Green in MST
            elif pair in rejected_edges:
                estate = "rejected"  # Red dashed rejected
            elif active_edge and pair == (min(active_edge["u"], active_edge["v"]), max(active_edge["u"], active_edge["v"])):
                estate = active_state # Purple or Red
            else:
                estate = "idle"

            edge_payloads.append({
                "u": u,
                "v": v,
                "weight": w,
                "state": estate,
            })

        chips = []
        for e in sorted_edges:
            p = (min(e["u"], e["v"]), max(e["u"], e["v"]))
            if p in selected_edges:
                chips.append(f"✓ {e['u']}-{e['v']}:{e['weight']}")
            elif p in rejected_edges:
                chips.append(f"✗ {e['u']}-{e['v']}:{e['weight']}")
            elif active_edge and p == (min(active_edge["u"], active_edge["v"]), max(active_edge["u"], active_edge["v"])):
                chips.append(f"★ {e['u']}-{e['v']}:{e['weight']}")
            else:
                chips.append(f"{e['u']}-{e['v']}:{e['weight']}")

        gd = {
            "type": "kruskal",
            "title": "Kruskal's Algorithm (Minimum Spanning Tree)",
            "status_text": status_text,
            "comparison_text": comparison_text,
            "structure_label": "Global Edges Sorted by Weight (Ascending Order)",
            "chips": chips,
            "nodes": node_payloads,
            "edges": edge_payloads,
            "total_weight": total_weight,
        }
        return RenderData(mode="graph", graph_data=gd)

    # ------------------------------------------------------------------
    # Step 0: Conceptual Introduction
    # ------------------------------------------------------------------
    sorted_str = " < ".join([f"{e['u']}-{e['v']}:{e['weight']}" for e in sorted_edges])
    intro_explanation = (
        "Core Idea: Select the cheapest edges across the entire graph while avoiding cycles.\n\n"
        "How Kruskal's Algorithm works:\n"
        "1. Sort all graph edges in ascending order of weight.\n"
        "2. Select the edge with the smallest weight.\n"
        "3. Check whether adding the edge creates a cycle (using Disjoint Set Union / Union-Find).\n"
        "4. If it does not create a cycle, include it in the MST.\n"
        "5. If it creates a cycle, skip it.\n"
        "6. Continue until exactly V - 1 edges have been selected, where V is the number of vertices.\n\n"
        "Important condition: An edge should only be selected if it connects two different components!"
    )
    steps.append(VisualizationStep(
        index=step_idx,
        title="Introduction — Kruskal's Algorithm for Minimum Spanning Trees",
        equation=f"Global Sorted Edges: {sorted_str}",
        explanation=intro_explanation,
        values={"mst_weight": 0, "edges_count": 0, "graph_name": graph_name},
        render_data=make_snapshot(
            status_text=f"Kruskal's Algorithm: Ready to scan {len(sorted_edges)} edges in ascending order.",
            comparison_text=f"Graph: {graph_name} ({len(nodes)} vertices, {len(edges)} edges).",
            remaining_edges=sorted_edges,
        ),
        metrics={"Selected Edges": 0, "Total Weight": 0, "Target Edges": len(nodes) - 1}
    ))
    step_idx += 1

    # Main Kruskal's Loop: inspect sorted edges one by one
    iteration = 1
    for edge in sorted_edges:
        if len(selected_edges) == len(nodes) - 1:
            break  # Tree is complete! Exactly V - 1 edges

        u, v, w = edge["u"], edge["v"], edge["weight"]
        pair = (min(u, v), max(u, v))
        comp_u = dsu.find(u)
        comp_v = dsu.find(v)

        if comp_u != comp_v:
            # ACCEPT EDGE
            dsu.union(u, v)
            selected_edges.add(pair)
            total_weight += w

            steps.append(VisualizationStep(
                index=step_idx,
                title=f"Step {iteration}: ACCEPT Edge {u}-{v} [Weight {w}] — Connects Separate Components",
                equation=f"Edge {u}-{v} with weight {w} was selected  |  Total MST Weight = {total_weight}",
                explanation=(
                    f"1. Decision: Edge {u}-{v} with weight {w} was selected because it is the smallest remaining edge and does not form a cycle.\n"
                    f"2. Component Check: Vertex '{u}' and vertex '{v}' belong to different components ({comp_u} vs {comp_v}).\n"
                    f"3. Outcome: Safely merged without creating any closed loops ({len(selected_edges)} of {len(nodes) - 1} target edges chosen)."
                ),
                values={"decision": "ACCEPT", "edge": f"{u}-{v}", "weight": w, "total_weight": total_weight},
                render_data=make_snapshot(
                    active_edge=edge,
                    active_state="selected",
                    status_text=f"ACCEPTED Edge {u}-{v} (weight {w}). Merged components {comp_u} and {comp_v}.",
                    comparison_text=f"Progress: {len(selected_edges)} of {len(nodes) - 1} edges chosen. Total weight: {total_weight}.",
                ),
                metrics={"Selected Edges": len(selected_edges), "Total Weight": total_weight, "Target Edges": len(nodes) - 1}
            ))
            step_idx += 1
        else:
            # REJECT EDGE (CYCLE DETECTED)
            rejected_edges.add(pair)

            steps.append(VisualizationStep(
                index=step_idx,
                title=f"Step {iteration}: REJECT Edge {u}-{v} [Weight {w}] — Would Create a Cycle!",
                equation=f"Edge {u}-{v} REJECTED: Both vertices already in Component {comp_u} (Forms Cycle)",
                explanation=(
                    f"1. Decision: Edge {u}-{v} with weight {w} was REJECTED because adding it would form a cycle!\n"
                    f"2. Cycle Detection: Both vertex '{u}' and vertex '{v}' are already in Component {comp_u}.\n"
                    f"3. Why avoid cycles? A Spanning Tree must be acyclic (zero cycles). Therefore, this edge is permanently skipped."
                ),
                values={"decision": "REJECT", "edge": f"{u}-{v}", "weight": w, "reason": "cycle"},
                render_data=make_snapshot(
                    active_edge=edge,
                    active_state="rejected",
                    status_text=f"REJECTED Edge {u}-{v} (weight {w})! Both vertices already in component {comp_u}.",
                    comparison_text="Skipped to prevent cycle. Tree must remain acyclic.",
                ),
                metrics={"Selected Edges": len(selected_edges), "Total Weight": total_weight, "Target Edges": len(nodes) - 1}
            ))
            step_idx += 1

        iteration += 1

    # ------------------------------------------------------------------
    # Final Step: MST Complete
    # ------------------------------------------------------------------
    edge_list_str = ", ".join([f"{u}-{v}" for (u, v) in sorted(list(selected_edges))])
    steps.append(VisualizationStep(
        index=step_idx,
        title="Minimum Spanning Tree Complete via Kruskal's Algorithm!",
        equation=f"MST Completed: Exactly {len(selected_edges)} Edges  |  Total Weight = {total_weight}",
        explanation=(
            f"All {len(nodes)} vertices have been united into a single spanning tree!\n\n"
            f"• Total MST Weight: {total_weight}\n"
            f"• Number of Edges: Exactly V - 1 = {len(selected_edges)} edges\n"
            f"• Selected Edges: {edge_list_str}\n"
            f"• Rejected Cycle Edges: {len(rejected_edges)} skipped\n"
            f"• Notice: Prim's algorithm and Kruskal's algorithm may choose edges in different orders, but both always find the EXACT same minimal total weight of {total_weight}!"
        ),
        values={"final_weight": total_weight, "selected_edges": list(selected_edges)},
        render_data=make_snapshot(
            active_edge=None,
            status_text=f"Minimum Spanning Tree Complete! Total Weight = {total_weight}.",
            comparison_text=f"Selected {len(selected_edges)} edges. Skipped {len(rejected_edges)} cycle edges.",
        ),
        metrics={"Selected Edges": len(selected_edges), "Total Weight": total_weight, "Target Edges": len(nodes) - 1}
    ))

    return steps
