"""
core/step_model.py
-------------------
Unified visualization step model and graphic primitive definitions
used across Theorems, Algorithms, CGIP Transformations, Rasterization,
and Clipping.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Point2D:
    x: float
    y: float
    label: str = ""
    color: str = "#EAF0F6"
    radius: float = 4.0


@dataclass
class Line2D:
    x1: float
    y1: float
    x2: float
    y2: float
    color: str = "#5B8DEF"
    width: float = 2.0
    dashed: bool = False
    label: str = ""


@dataclass
class Polygon2D:
    points: List[Tuple[float, float]]
    fill_color: str = "rgba(78, 199, 176, 0.25)"
    stroke_color: str = "#4EC7B0"
    stroke_width: float = 2.0
    label: str = ""


@dataclass
class Arc2D:
    cx: float
    cy: float
    radius: float
    start_angle_deg: float
    span_angle_deg: float
    color: str = "#D8A94E"
    label: str = ""


@dataclass
class Text2D:
    x: float
    y: float
    text: str
    color: str = "#EAF0F6"
    font_size: int = 11
    bold: bool = False


@dataclass
class RenderData:
    """Container for geometric primitives to draw in the 2D viewport."""
    mode: str = "geometry"  # 'geometry', 'bars', 'pixel_grid', 'clipping', 'curves'
    points: List[Point2D] = field(default_factory=list)
    lines: List[Line2D] = field(default_factory=list)
    polygons: List[Polygon2D] = field(default_factory=list)
    arcs: List[Arc2D] = field(default_factory=list)
    texts: List[Text2D] = field(default_factory=list)
    
    # Specific mode payloads:
    bars: Optional[List[Dict[str, Any]]] = None           # for sorting
    sort_event: Optional[Any] = None                    # semantic event for sorting animation playground
    search_data: Optional[Dict[str, Any]] = None        # for linear/binary search tiles
    pixel_grid: Optional[Dict[str, Any]] = None         # for rasterization
    clipping_data: Optional[Dict[str, Any]] = None      # for Cohen-Sutherland
    curve_data: Optional[Dict[str, Any]] = None         # for Bézier / B-spline / Hermite
    matrix_info: Optional[Dict[str, Any]] = None        # for transformations
    
    # View framing hint (xmin, ymin, xmax, ymax) in world coordinates
    view_bounds: Optional[Tuple[float, float, float, float]] = None


@dataclass
class VisualizationStep:
    """Comprehensive representation of a single step in any visualization."""
    index: int                          # 1-based step index
    title: str = ""
    equation: str = ""                  # Math formula, code, or relation
    explanation: str = ""               # Plain text narrative explaining WHY
    values: Dict[str, Any] = field(default_factory=dict)
    render_data: Optional[RenderData] = None
    pseudocode_line: Optional[int] = None
    pseudocode: Optional[List[str]] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
