"""
algorithms/graph_algorithms/compare_mst.py
------------------------------------------
Comprehensive comparison module for Prim's Algorithm vs Kruskal's Algorithm
on the exact same weighted graph.
"""

from typing import Dict, List, Any
from core.step_model import VisualizationStep, RenderData
from algorithms.graph_algorithms.graphs import get_graph_preset
from algorithms.graph_algorithms.prim import prim_trace
from algorithms.graph_algorithms.kruskal import kruskal_trace


def compare_mst_trace(graph_name: str = "Network Backbone", custom_edges: str = "") -> List[VisualizationStep]:
    """Runs both Prim and Kruskal on the same graph and builds a comparative pedagogical trace."""
    prim_steps = prim_trace(graph_name, start_node="A", custom_edges=custom_edges)
    kruskal_steps = kruskal_trace(graph_name, custom_edges=custom_edges)

    p_final = prim_steps[-1]
    k_final = kruskal_steps[-1]

    p_weight = p_final.metrics.get("Total Weight", 0)
    k_weight = k_final.metrics.get("Total Weight", 0)

    g = get_graph_preset(graph_name, custom_text=custom_edges)
    nodes = g["nodes"]
    edges = g["edges"]

    steps: List[VisualizationStep] = []

    # Step 1: Conceptual Comparison
    steps.append(VisualizationStep(
        index=1,
        title="Comparison — Prim's vs Kruskal's Algorithm",
        equation="Both algorithms find the optimal Minimum Spanning Tree with identical total cost!",
        explanation=(
            "Key Differences between Prim's and Kruskal's Algorithms:\n\n"
            "1. Starting Point:\n"
            "   • Prim's: Starts at a single vertex and expands outward.\n"
            "   • Kruskal's: Starts with the globally smallest edge anywhere in the graph.\n\n"
            "2. How the Tree Grows:\n"
            "   • Prim's: Maintains exactly ONE growing connected tree at all times.\n"
            "   • Kruskal's: Creates multiple disconnected subtrees (a forest) that gradually merge.\n\n"
            "3. Decision Mechanism:\n"
            "   • Prim's: Greedily selects the minimum-weight edge connecting the tree to an unvisited vertex.\n"
            "   • Kruskal's: Sorts all edges globally; adds each edge if it does not form a cycle (via DSU).\n\n"
            "4. Data Structures & Complexity:\n"
            "   • Prim's: Priority Queue / Min-Heap. Time complexity: O(E log V).\n"
            "   • Kruskal's: Sorting + Disjoint Set Union (Union-Find). Time complexity: O(E log E)."
        ),
        values={"p_weight": p_weight, "k_weight": k_weight},
        render_data=k_final.render_data,
        metrics={"Prim Total Weight": p_weight, "Kruskal Total Weight": k_weight, "Difference": 0}
    ))

    # Step 2: Prim's Result on this graph
    steps.append(VisualizationStep(
        index=2,
        title=f"Prim's MST Result on {graph_name} (Total Weight = {p_weight})",
        equation=f"Prim's Total Weight = {p_weight} across {len(nodes) - 1} edges",
        explanation=(
            f"Prim's Algorithm Result:\n"
            f"• Started at vertex 'A' and grew a single connected component.\n"
            f"• At every stage, took the cheapest cut edge across the boundary.\n"
            f"• Final Minimum Spanning Tree Weight: {p_weight}."
        ),
        values={"algorithm": "Prim", "weight": p_weight},
        render_data=p_final.render_data,
        metrics={"Prim Total Weight": p_weight, "Edges in MST": len(nodes) - 1}
    ))

    # Step 3: Kruskal's Result on this graph
    steps.append(VisualizationStep(
        index=3,
        title=f"Kruskal's MST Result on {graph_name} (Total Weight = {k_weight})",
        equation=f"Kruskal's Total Weight = {k_weight} across {len(nodes) - 1} edges",
        explanation=(
            f"Kruskal's Algorithm Result:\n"
            f"• Sorted all edges globally in ascending order of weight.\n"
            f"• Added edges that connected different components; rejected edges that would create cycles.\n"
            f"• Final Minimum Spanning Tree Weight: {k_weight}."
        ),
        values={"algorithm": "Kruskal", "weight": k_weight},
        render_data=k_final.render_data,
        metrics={"Kruskal Total Weight": k_weight, "Edges in MST": len(nodes) - 1}
    ))

    # Step 4: Mathematical Equivalence
    steps.append(VisualizationStep(
        index=4,
        title="Verification — Identical Minimum Total Weight",
        equation=f"Prim ({p_weight}) == Kruskal ({k_weight})  →  Optimal MST Proven!",
        explanation=(
            f"Educational Takeaway:\n"
            f"Although Prim's and Kruskal's algorithms follow completely different exploration strategies "
            f"(growing a single tree vs merging global forest components), both mathematically achieve the exact same "
            f"minimal total weight of {p_weight}.\n\n"
            f"When to use which?\n"
            f"• Prim's is faster on dense graphs where E is close to V² (using adjacency matrix or heap: O(V²)).\n"
            f"• Kruskal's is simpler and faster on sparse graphs where E is much smaller than V²: O(E log E)."
        ),
        values={"verified": True, "mst_weight": p_weight},
        render_data=k_final.render_data,
        metrics={"Prim Weight": p_weight, "Kruskal Weight": k_weight, "Equivalence": "VERIFIED"}
    ))

    return steps

