"""
models/theorem_state.py
------------------------
Plain data structures describing:
  - a Theorem's identity and the parameters it needs (ParameterSpec)
  - a single ProofStep (equation + explanation + numeric values)
  - the overall TheoremState the controller manages at runtime

None of these classes import PyQt or perform any real math. They are the
shared "vocabulary" the GUI, controller, and (future) theorem/graphics
modules all speak, so keeping this file dependency-free is important:
whoever implements the real math/graphics modules should be able to
import this module without pulling in the entire GUI stack.

Replace-later note
-------------------
`SAMPLE_THEOREMS` at the bottom of this file is DUMMY DATA used only so
the UI shell is runnable end-to-end before the real theorem/proof engine
exists. The real engine should build equivalent `Theorem` objects (or
call into ApplicationController with the same shapes) instead of
importing SAMPLE_THEOREMS directly.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Any


class ParameterType(Enum):
    """Supported kinds of parameter inputs the ParameterPanel can render."""
    LENGTH = auto()   # positive real number (e.g. side length, radius)
    ANGLE = auto()    # degrees, 0-360 (or theorem-specific bounds)
    RATIO = auto()    # positive real number, used for similarity ratios
    INTEGER = auto()  # discrete integer (e.g. array size, grid width)
    TEXT = auto()     # comma-separated array string, formula, etc.
    CHOICE = auto()   # selectable option from choices


@dataclass
class ParameterSpec:
    """Describes a single input field the ParameterPanel should render."""
    key: str                       # internal id, e.g. "side_a"
    label: str                     # display label, e.g. "Side A"
    param_type: ParameterType
    default: Any = 0.0
    min_value: float = 0.0001
    max_value: float = 100000.0
    suffix: str = ""                # e.g. "cm", "°"
    choices: List[str] = field(default_factory=list)


@dataclass
class ProofStep:
    """A single step of a theorem's step-by-step animated proof."""
    index: int                      # 1-based step number
    equation: str                   # e.g. "a\u00b2 + b\u00b2 = c\u00b2"
    explanation: str                # human-readable description
    values: Optional[dict] = None   # e.g. {"a": 3, "b": 4, "c": 5}
    render_data: Optional[Any] = None
    pseudocode_line: Optional[int] = None
    metrics: Optional[dict] = None


@dataclass
class Theorem:
    """Static definition of a selectable theorem."""
    key: str                        # internal id, e.g. "pythagorean"
    display_name: str               # e.g. "Pythagorean Theorem"
    short_description: str
    parameters: List[ParameterSpec] = field(default_factory=list)
    steps: List[ProofStep] = field(default_factory=list)
    final_result_template: str = ""  # e.g. "c = {c:.2f}"


@dataclass
class AnimationState:
    """Runtime animation state tracked by the controller."""
    is_playing: bool = False
    current_step_index: int = 0     # 0-based index into Theorem.steps
    speed_multiplier: float = 1.0   # 0.25x - 3.0x, drives a QTimer interval


@dataclass
class TheoremRuntimeState:
    """Full runtime state the ApplicationController owns and mutates."""
    selected_theorem_key: Optional[str] = None
    parameter_values: dict = field(default_factory=dict)
    animation: AnimationState = field(default_factory=AnimationState)
    final_result: Optional[str] = None
    is_valid: bool = False
    validation_message: str = ""


# ----------------------------------------------------------------------
# DUMMY / SAMPLE DATA
# ----------------------------------------------------------------------
# This lets the UI shell run and display believable content before the
# real theorem/proof engine (SymPy/NumPy based) is implemented.
# TODO(theorem-team): replace with real generated ProofStep sequences.
# ----------------------------------------------------------------------

def _pythagorean() -> Theorem:
    return Theorem(
        key="pythagorean",
        display_name="Pythagorean Theorem",
        short_description="Relationship between the legs and hypotenuse of a right triangle.",
        parameters=[
            ParameterSpec("side_a", "Side A", ParameterType.LENGTH, default=3.0, suffix="cm"),
            ParameterSpec("side_b", "Side B", ParameterType.LENGTH, default=4.0, suffix="cm"),
        ],
        steps=[
            ProofStep(1, "a, b \u2192 right triangle",
                      "Construct a right triangle with legs a and b meeting at a right angle.",
                      {"a": 3, "b": 4}),
            ProofStep(2, "Square(a), Square(b)",
                      "Construct squares on each of the two legs of the triangle.",
                      {"a": 3, "b": 4}),
            ProofStep(3, "a\u00b2 + b\u00b2 = c\u00b2",
                      "The two squares constructed on the perpendicular sides are rearranged "
                      "to demonstrate their relationship with the square on the hypotenuse.",
                      {"a": 3, "b": 4}),
            ProofStep(4, "c = \u221a(a\u00b2 + b\u00b2)",
                      "Solve for the hypotenuse length using the derived relationship.",
                      {"a": 3, "b": 4, "c": 5}),
        ],
        final_result_template="c = {c:.2f} cm",
    )


def _circle_area() -> Theorem:
    return Theorem(
        key="circle_area",
        display_name="Circle Area",
        short_description="Derivation of a circle's area from radius via inscribed polygons.",
        parameters=[
            ParameterSpec("radius", "Radius", ParameterType.LENGTH, default=5.0, suffix="cm"),
        ],
        steps=[
            ProofStep(1, "r \u2192 circle",
                      "Draw a circle of radius r centered at the origin.",
                      {"r": 5}),
            ProofStep(2, "circle \u2192 n-gon slices",
                      "Inscribe a regular polygon and slice it into congruent triangular wedges.",
                      {"r": 5}),
            ProofStep(3, "wedges \u2192 rearranged strip",
                      "Unroll and rearrange the wedges into an approximate parallelogram.",
                      {"r": 5}),
            ProofStep(4, "A = \u03c0r\u00b2",
                      "As the number of wedges increases, the shape approaches a rectangle "
                      "with base \u03c0r and height r, giving the area formula.",
                      {"r": 5}),
        ],
        final_result_template="A = {area:.2f} cm\u00b2",
    )


def _similar_triangles() -> Theorem:
    return Theorem(
        key="similar_triangles",
        display_name="Similar Triangles",
        short_description="Proportional side relationships between similar triangles.",
        parameters=[
            ParameterSpec("side_a", "Side A", ParameterType.LENGTH, default=6.0, suffix="cm"),
            ParameterSpec("side_b", "Side B", ParameterType.LENGTH, default=8.0, suffix="cm"),
            ParameterSpec("ratio", "Scale Ratio", ParameterType.RATIO, default=1.5, suffix="\u00d7"),
        ],
        steps=[
            ProofStep(1, "\u25b3ABC",
                      "Construct the original triangle ABC.",
                      {"a": 6, "b": 8}),
            ProofStep(2, "\u25b3A'B'C' = k \u00b7 \u25b3ABC",
                      "Construct a second triangle scaled by ratio k with matching angles.",
                      {"k": 1.5}),
            ProofStep(3, "a'/a = b'/b = k",
                      "Overlay both triangles to show corresponding sides remain proportional.",
                      {"k": 1.5}),
        ],
        final_result_template="Scale factor k = {k:.2f}",
    )


def _law_of_cosines() -> Theorem:
    return Theorem(
        key="law_of_cosines",
        display_name="Law of Cosines",
        short_description="Generalized Pythagorean relationship for any triangle.",
        parameters=[
            ParameterSpec("side_a", "Side A", ParameterType.LENGTH, default=7.0, suffix="cm"),
            ParameterSpec("side_b", "Side B", ParameterType.LENGTH, default=5.0, suffix="cm"),
            ParameterSpec("angle_c", "Angle C", ParameterType.ANGLE, default=60.0, suffix="\u00b0"),
        ],
        steps=[
            ProofStep(1, "\u25b3ABC, \u2220C",
                      "Construct triangle ABC with the included angle C between sides a and b.",
                      {"a": 7, "b": 5, "C": 60}),
            ProofStep(2, "drop altitude h",
                      "Drop a perpendicular from vertex B to side b, splitting it into segments.",
                      {"a": 7, "b": 5, "C": 60}),
            ProofStep(3, "c\u00b2 = a\u00b2 + b\u00b2 \u2212 2ab\u00b7cos(C)",
                      "Apply the Pythagorean theorem to the two resulting right triangles and "
                      "combine to derive the law of cosines.",
                      {"a": 7, "b": 5, "C": 60}),
        ],
        final_result_template="c = {c:.2f} cm",
    )


SAMPLE_THEOREMS: List[Theorem] = [
    _pythagorean(),
    _circle_area(),
    _similar_triangles(),
    _law_of_cosines(),
]

SAMPLE_THEOREMS_BY_KEY = {t.key: t for t in SAMPLE_THEOREMS}
