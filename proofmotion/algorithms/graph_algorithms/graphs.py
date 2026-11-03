"""
algorithms/graph_algorithms/graphs.py
-------------------------------------
Weighted graphs, layout geometries, and presets for Prim's and Kruskal's
Minimum Spanning Tree algorithm visualizations.
"""

import math
from typing import Dict, List, Tuple, Any, Optional

# Standard presets with carefully spaced 2D coordinates (-3.5 to +3.5)
# ensuring zero label or node overlap on the canvas.

PRESET_GRAPHS: Dict[str, Dict[str, Any]] = {
    "Network Backbone": {
        "description": "A 6-node redundant network linking servers across regions.",
        "nodes": [
            {"id": "A", "x": -3.2, "y": 1.2, "label": "A"},
            {"id": "B", "x": -1.0, "y": 2.4, "label": "B"},
            {"id": "C", "x": 1.4, "y": 2.4, "label": "C"},
            {"id": "D", "x": 3.2, "y": 1.0, "label": "D"},
            {"id": "E", "x": -2.0, "y": -1.8, "label": "E"},
            {"id": "F", "x": 1.6, "y": -1.8, "label": "F"},
        ],
        "edges": [
            {"u": "A", "v": "B", "weight": 4},
            {"u": "A", "v": "E", "weight": 3},
            {"u": "B", "v": "C", "weight": 2},
            {"u": "B", "v": "E", "weight": 5},
            {"u": "B", "v": "F", "weight": 6},
            {"u": "C", "v": "D", "weight": 3},
            {"u": "C", "v": "F", "weight": 1},
            {"u": "D", "v": "F", "weight": 4},
            {"u": "E", "v": "F", "weight": 7},
        ],
    },
    "Metro Transit": {
        "description": "A 7-station transit system connecting urban sectors.",
        "nodes": [
            {"id": "Central", "x": 0.0, "y": 0.0, "label": "Central"},
            {"id": "North", "x": 0.0, "y": 2.6, "label": "North"},
            {"id": "South", "x": 0.0, "y": -2.6, "label": "South"},
            {"id": "East", "x": 3.0, "y": 0.0, "label": "East"},
            {"id": "West", "x": -3.0, "y": 0.0, "label": "West"},
            {"id": "Airport", "x": 2.4, "y": 2.0, "label": "Airport"},
            {"id": "Harbor", "x": -2.4, "y": -2.0, "label": "Harbor"},
        ],
        "edges": [
            {"u": "Central", "v": "North", "weight": 3},
            {"u": "Central", "v": "South", "weight": 4},
            {"u": "Central", "v": "East", "weight": 2},
            {"u": "Central", "v": "West", "weight": 3},
            {"u": "North", "v": "Airport", "weight": 2},
            {"u": "East", "v": "Airport", "weight": 4},
            {"u": "South", "v": "Harbor", "weight": 3},
            {"u": "West", "v": "Harbor", "weight": 5},
            {"u": "North", "v": "West", "weight": 6},
        ],
    },
    "Simple Diamond": {
        "description": "A classic 5-node planar graph for clear step-by-step tracing.",
        "nodes": [
            {"id": "A", "x": -3.0, "y": 0.0, "label": "A"},
            {"id": "B", "x": 0.0, "y": 2.2, "label": "B"},
            {"id": "C", "x": 0.0, "y": -2.2, "label": "C"},
            {"id": "D", "x": 3.0, "y": 0.0, "label": "D"},
            {"id": "E", "x": 0.0, "y": 0.0, "label": "E"},
        ],
        "edges": [
            {"u": "A", "v": "B", "weight": 2},
            {"u": "A", "v": "C", "weight": 4},
            {"u": "A", "v": "E", "weight": 3},
            {"u": "B", "v": "D", "weight": 5},
            {"u": "B", "v": "E", "weight": 1},
            {"u": "C", "v": "D", "weight": 6},
            {"u": "C", "v": "E", "weight": 2},
            {"u": "E", "v": "D", "weight": 4},
        ],
    },
}


def parse_custom_graph(edges_text: str) -> Dict[str, Any]:
    """
    Parses comma-separated edge definitions like:
    'A-B:4, A-E:3, B-C:2, C-D:3, C-F:1, D-F:4, B-E:5, B-F:6, E-F:7'
    and positions vertices on a clean circle with non-overlapping coordinates.
    """
    tokens = [t.strip() for t in edges_text.replace(";", ",").split(",") if t.strip()]
    raw_edges = []
    seen_vertices = []

    for tok in tokens:
        # Expected formats: u-v:w or u-v-w or u,v,w
        parts = tok.replace(":", "-").split("-")
        if len(parts) >= 3:
            u, v = parts[0].strip(), parts[1].strip()
            try:
                w = int(parts[2].strip())
            except ValueError:
                w = 1
            if u and v and u != v:
                raw_edges.append({"u": u, "v": v, "weight": max(1, w)})
                if u not in seen_vertices:
                    seen_vertices.append(u)
                if v not in seen_vertices:
                    seen_vertices.append(v)

    if not seen_vertices or not raw_edges:
        return get_graph_preset("Network Backbone")

    # Arrange vertices symmetrically along an ellipse/circle
    n = len(seen_vertices)
    nodes = []
    radius_x = 3.0
    radius_y = 2.4
    for i, vid in enumerate(seen_vertices):
        angle = 2.0 * math.pi * i / n - math.pi / 2.0  # start at top
        nodes.append({
            "id": vid,
            "x": round(radius_x * math.cos(angle), 2),
            "y": round(radius_y * math.sin(angle), 2),
            "label": vid,
        })

    return {
        "description": f"Custom Graph with {n} vertices and {len(raw_edges)} edges.",
        "nodes": nodes,
        "edges": raw_edges,
    }


def get_graph_preset(name: str, custom_text: str = "") -> Dict[str, Any]:
    """Retrieve deep-copied preset structure or parse custom edges."""
    if name == "Custom Graph" and custom_text.strip():
        return parse_custom_graph(custom_text)
    preset = PRESET_GRAPHS.get(name) or PRESET_GRAPHS["Network Backbone"]
    return {
        "description": preset["description"],
        "nodes": [dict(n) for n in preset["nodes"]],
        "edges": [dict(e) for e in preset["edges"]],
    }
