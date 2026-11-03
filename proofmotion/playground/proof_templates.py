"""
playground/proof_templates.py
-----------------------------
Prebuilt mathematical proof templates for Proof Builder.
Provides students and educators with starting foundations for classic geometric
theorems:
  - Pythagorean Theorem (a² + b² = c²)
  - Triangle Angle Sum (∠A + ∠B + ∠C = 180°)
  - Thales's Theorem (Angle in Semicircle = 90°)
  - Exterior Angle Theorem (∠ext = ∠A + ∠B)
  - Triangle Area Formula (Area = ½ · b · h)
  - Blank / Starter Geometry Setup
"""

from typing import Dict, List
from playground.proof_builder_model import (
    BuilderProof, BuilderProofStep, BuilderShape, ShapeType
)


def get_template_catalog() -> Dict[str, BuilderProof]:
    """Returns all available starter proof templates."""
    return {
        "pythagorean": create_pythagorean_template(),
        "triangle_angle_sum": create_triangle_angle_sum_template(),
        "thales": create_thales_template(),
        "exterior_angle": create_exterior_angle_template(),
        "triangle_area": create_triangle_area_template(),
        "blank": create_blank_template(),
    }


def create_pythagorean_template() -> BuilderProof:
    """Bhaskara / Euclid geometric dissection proof of Pythagorean Theorem."""
    proof = BuilderProof(
        title="Pythagorean Theorem",
        description="In any right-angled triangle, the area of the square on the hypotenuse equals the sum of the areas of the squares on the other two sides: a² + b² = c²."
    )

    # Coordinates: Right angle at C(0, 0), B(4, 0), A(0, 3)
    # Leg a = 4, Leg b = 3, Hypotenuse c = 5

    # --- Step 1: Base Right Triangle ---
    step1 = BuilderProofStep(
        index=1,
        title="Step 1: Construct Right-Angled Triangle ΔABC",
        equation="c = √(a² + b²) = √(4² + 3²) = 5.0",
        explanation="1. Goal: Draw right triangle ΔABC with legs a = 4.0 and b = 3.0.\n"
                    "2. Why: Establish the fundamental right-angled triangle where ∠C = 90°.\n"
                    "3. Calculation: Using the Euclidean distance metric, hypotenuse c = √(4² + 3²) = 5.0.\n"
                    "4. Result: Vertices A(0, 3), B(4, 0), and right-angled vertex C(0, 0) form ΔABC.",
        shapes=[
            # Triangle polygon
            BuilderShape(
                shape_type=ShapeType.POLYGON.value,
                name="ΔABC",
                color="#5B8DEF",
                fill_color="rgba(91, 141, 239, 0.25)",
                stroke_width=2.5,
                polygon_points=[(0.0, 0.0), (4.0, 0.0), (0.0, 3.0)]
            ),
            # Vertices
            BuilderShape(shape_type=ShapeType.POINT.value, name="C(0,0)", color="#EAF0F6", coords=[0.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B(4,0)", color="#EAF0F6", coords=[4.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A(0,3)", color="#EAF0F6", coords=[0.0, 3.0, 4.5]),
            # Right angle symbol
            BuilderShape(
                shape_type=ShapeType.ANGLE.value,
                name="90°",
                color="#D8A94E",
                is_right_angle=True,
                coords=[0.0, 0.0, 0.6, 0.0, 90.0]
            ),
            # Side labels
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Leg a", text="a = 4.0", color="#5B8DEF", coords=[2.0, -0.45], font_size=12, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Leg b", text="b = 3.0", color="#5B8DEF", coords=[-0.85, 1.5], font_size=12, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Hypotenuse c", text="c = 5.0", color="#2F9E78", coords=[2.3, 1.8], font_size=12, bold=True),
        ]
    )

    # --- Step 2: Erect Square on Leg a ---
    step2 = BuilderProofStep(
        index=2,
        title="Step 2: Erect Square of Area a² on Leg BC",
        equation="Area(Square a) = a² = 4² = 16.0",
        explanation="1. Goal: Construct a geometric square along leg BC of side length 4.\n"
                    "2. Why: Visually illustrates the mathematical term a² as a physical two-dimensional area.\n"
                    "3. Calculation: Side length = 4.0 ⟹ Area = 4.0 × 4.0 = 16.0.\n"
                    "4. Result: Square BCDE of area 16 is constructed downward from side BC.",
        shapes=[
            # Base triangle
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.25)", stroke_width=2.5, polygon_points=[(0.0, 0.0), (4.0, 0.0), (0.0, 3.0)]),
            # Square on leg a (downward: (0,0) -> (4,0) -> (4,-4) -> (0,-4))
            BuilderShape(
                shape_type=ShapeType.POLYGON.value,
                name="Square a²",
                color="#6C5CE7",
                fill_color="rgba(108, 92, 231, 0.35)",
                stroke_width=2.2,
                polygon_points=[(0.0, 0.0), (4.0, 0.0), (4.0, -4.0), (0.0, -4.0)]
            ),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C(0,0)", color="#EAF0F6", coords=[0.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B(4,0)", color="#EAF0F6", coords=[4.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A(0,3)", color="#EAF0F6", coords=[0.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="90°", color="#D8A94E", is_right_angle=True, coords=[0.0, 0.0, 0.6, 0.0, 90.0]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Area a² Label", text="Area = a² = 16", color="#6C5CE7", coords=[2.0, -2.0], font_size=13, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Leg b", text="b = 3.0", color="#5B8DEF", coords=[-0.85, 1.5], font_size=12, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Hypotenuse c", text="c = 5.0", color="#2F9E78", coords=[2.3, 1.8], font_size=12, bold=True),
        ]
    )

    # --- Step 3: Erect Square on Leg b ---
    step3 = BuilderProofStep(
        index=3,
        title="Step 3: Erect Square of Area b² on Leg AC",
        equation="Area(Square b) = b² = 3² = 9.0",
        explanation="1. Goal: Construct a geometric square along leg AC of side length 3.\n"
                    "2. Why: Visually illustrates the mathematical term b² as a physical two-dimensional area.\n"
                    "3. Calculation: Side length = 3.0 ⟹ Area = 3.0 × 3.0 = 9.0.\n"
                    "4. Result: Combined area of both leg squares is 16.0 + 9.0 = 25.0.",
        shapes=[
            # Base triangle
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.25)", stroke_width=2.5, polygon_points=[(0.0, 0.0), (4.0, 0.0), (0.0, 3.0)]),
            # Square on leg a
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="Square a²", color="#6C5CE7", fill_color="rgba(108, 92, 231, 0.35)", stroke_width=2.2, polygon_points=[(0.0, 0.0), (4.0, 0.0), (4.0, -4.0), (0.0, -4.0)]),
            # Square on leg b (to the left: (0,0) -> (0,3) -> (-3,3) -> (-3,0))
            BuilderShape(
                shape_type=ShapeType.POLYGON.value,
                name="Square b²",
                color="#526CCB",
                fill_color="rgba(82, 108, 203, 0.35)",
                stroke_width=2.2,
                polygon_points=[(0.0, 0.0), (0.0, 3.0), (-3.0, 3.0), (-3.0, 0.0)]
            ),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C(0,0)", color="#EAF0F6", coords=[0.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B(4,0)", color="#EAF0F6", coords=[4.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A(0,3)", color="#EAF0F6", coords=[0.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="90°", color="#D8A94E", is_right_angle=True, coords=[0.0, 0.0, 0.6, 0.0, 90.0]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Area a² Label", text="a² = 16", color="#6C5CE7", coords=[2.0, -2.0], font_size=13, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Area b² Label", text="b² = 9", color="#526CCB", coords=[-1.5, 1.5], font_size=13, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Hypotenuse c", text="c = 5.0", color="#2F9E78", coords=[2.3, 1.8], font_size=12, bold=True),
        ]
    )

    # --- Step 4: Square on Hypotenuse c & Verification ---
    # Hypotenuse vector from A(0, 3) to B(4, 0) is (4, -3). Normal vector is (3, 4).
    # Square on hypotenuse outward: (0,3) -> (4,0) -> (4+3, 0+4)=(7,4) -> (0+3, 3+4)=(3,7)
    step4 = BuilderProofStep(
        index=4,
        title="Step 4: Erect Square on Hypotenuse & Verify a² + b² = c²",
        equation="a² + b² = 16 + 9 = 25 = c² (5²)",
        explanation="1. Goal: Erect the square on hypotenuse AB and verify total area equality.\n"
                    "2. Why: The Pythagorean theorem establishes that the sum of leg square areas equals the hypotenuse square area.\n"
                    "3. Verification: Area(a²) + Area(b²) = 16 + 9 = 25. Hypotenuse square area = 5² = 25.\n"
                    "4. Conclusion: a² + b² = c² holds exactly! Proof complete.",
        shapes=[
            # Base triangle
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.25)", stroke_width=2.5, polygon_points=[(0.0, 0.0), (4.0, 0.0), (0.0, 3.0)]),
            # Square on leg a
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="Square a²", color="#6C5CE7", fill_color="rgba(108, 92, 231, 0.35)", stroke_width=2.2, polygon_points=[(0.0, 0.0), (4.0, 0.0), (4.0, -4.0), (0.0, -4.0)]),
            # Square on leg b
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="Square b²", color="#526CCB", fill_color="rgba(82, 108, 203, 0.35)", stroke_width=2.2, polygon_points=[(0.0, 0.0), (0.0, 3.0), (-3.0, 3.0), (-3.0, 0.0)]),
            # Square on hypotenuse c (outward: (4,0) -> (7,4) -> (3,7) -> (0,3))
            BuilderShape(
                shape_type=ShapeType.POLYGON.value,
                name="Square c²",
                color="#2F9E78",
                fill_color="rgba(47, 158, 120, 0.35)",
                stroke_width=2.5,
                polygon_points=[(4.0, 0.0), (7.0, 4.0), (3.0, 7.0), (0.0, 3.0)]
            ),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C(0,0)", color="#EAF0F6", coords=[0.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B(4,0)", color="#EAF0F6", coords=[4.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A(0,3)", color="#EAF0F6", coords=[0.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="90°", color="#D8A94E", is_right_angle=True, coords=[0.0, 0.0, 0.6, 0.0, 90.0]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Area a²", text="a² = 16", color="#6C5CE7", coords=[2.0, -2.0], font_size=13, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Area b²", text="b² = 9", color="#526CCB", coords=[-1.5, 1.5], font_size=13, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Area c²", text="c² = 25", color="#2F9E78", coords=[3.5, 3.5], font_size=14, bold=True),
        ]
    )

    proof.steps = [step1, step2, step3, step4]
    return proof


def create_triangle_angle_sum_template() -> BuilderProof:
    """Proof that interior angles of any triangle sum to 180°."""
    proof = BuilderProof(
        title="Triangle Angle Sum Theorem",
        description="The sum of the three interior angles of any planar triangle is always 180 degrees (a straight line): ∠A + ∠B + ∠C = 180°."
    )

    # Triangle ABC: A(-3, 0), B(4, 0), C(0, 3.5)
    # --- Step 1: Base Triangle with Angles ---
    step1 = BuilderProofStep(
        index=1,
        title="Step 1: Given Arbitrary Triangle ΔABC",
        equation="∠A + ∠B + ∠C = ?",
        explanation="1. Goal: Consider an arbitrary planar triangle with interior angles ∠A, ∠B, and ∠C.\n"
                    "2. Why: We want to prove that regardless of triangle proportions, the sum is invariant.\n"
                    "3. Result: Three vertices A(-3, 0), B(4, 0), and C(0, 3.5) with interior angle arcs.",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.22)", stroke_width=2.5, polygon_points=[(-3.0, 0.0), (4.0, 0.0), (0.0, 3.5)]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-3.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[4.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[0.0, 3.5, 4.5]),
            # Interior Angle Arcs
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠A", color="#F59E0B", coords=[-3.0, 0.0, 0.9, 0.0, 49.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠B", color="#EC4899", coords=[4.0, 0.0, 0.9, 139.0, 41.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠C", color="#6C5CE7", coords=[0.0, 3.5, 0.9, 229.0, 90.0]),
        ]
    )

    # --- Step 2: Parallel Line L Through C ---
    step2 = BuilderProofStep(
        index=2,
        title="Step 2: Construct Parallel Line L Through Vertex C",
        equation="Line L ∥ Side AB",
        explanation="1. Goal: Draw an auxiliary straight line L passing through vertex C parallel to base AB.\n"
                    "2. Why: Euclid's parallel postulate guarantees a unique parallel line through C.\n"
                    "3. Result: Line L forms adjacent angles on either side of vertex C.",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.22)", stroke_width=2.5, polygon_points=[(-3.0, 0.0), (4.0, 0.0), (0.0, 3.5)]),
            # Auxiliary parallel line L: from (-5, 3.5) to (6, 3.5)
            BuilderShape(shape_type=ShapeType.LINE.value, name="Line L ∥ AB", color="#38BDF8", stroke_width=2.2, dashed=True, coords=[-5.0, 3.5, 6.0, 3.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-3.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[4.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[0.0, 3.5, 4.5]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠A", color="#F59E0B", coords=[-3.0, 0.0, 0.9, 0.0, 49.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠B", color="#EC4899", coords=[4.0, 0.0, 0.9, 139.0, 41.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠C", color="#6C5CE7", coords=[0.0, 3.5, 0.9, 229.0, 90.0]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Line L Tag", text="Line L (Parallel to AB)", color="#38BDF8", coords=[2.5, 3.8], font_size=11, bold=True),
        ]
    )

    # --- Step 3: Alternate Interior Angles ---
    step3 = BuilderProofStep(
        index=3,
        title="Step 3: Alternate Interior Angles Equivalence",
        equation="∠1 = ∠A  and  ∠2 = ∠B  (Alternate Interior Angles)",
        explanation="1. Goal: Apply transversal angle properties between parallel lines L and AB.\n"
                    "2. Why: Side AC acts as a transversal, so angle ∠1 on the left equals ∠A.\n"
                    "3. Similarly: Side BC acts as a transversal, so angle ∠2 on the right equals ∠B.\n"
                    "4. Result: Angles ∠A and ∠B are mirrored directly at vertex C on line L.",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.22)", stroke_width=2.5, polygon_points=[(-3.0, 0.0), (4.0, 0.0), (0.0, 3.5)]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Line L ∥ AB", color="#38BDF8", stroke_width=2.2, dashed=True, coords=[-5.0, 3.5, 6.0, 3.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-3.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[4.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[0.0, 3.5, 4.5]),
            # Interior angles
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠A", color="#F59E0B", coords=[-3.0, 0.0, 0.9, 0.0, 49.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠B", color="#EC4899", coords=[4.0, 0.0, 0.9, 139.0, 41.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠C", color="#6C5CE7", coords=[0.0, 3.5, 0.9, 229.0, 90.0]),
            # Alternate angles at C:
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠1 (=∠A)", color="#F59E0B", coords=[0.0, 3.5, 1.0, 180.0, 49.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠2 (=∠B)", color="#EC4899", coords=[0.0, 3.5, 1.0, 319.0, 41.0]),
        ]
    )

    # --- Step 4: Straight Angle Summation ---
    step4 = BuilderProofStep(
        index=4,
        title="Step 4: Straight Line Angle Sum Proves ∠A + ∠B + ∠C = 180°",
        equation="∠1 + ∠C + ∠2 = 180° ⟹ ∠A + ∠B + ∠C = 180°",
        explanation="1. Goal: Sum the three contiguous angles along straight line L at vertex C.\n"
                    "2. Why: Angles forming a straight line sum to 180°: ∠1 + ∠C + ∠2 = 180°.\n"
                    "3. Substitution: Since ∠1 = ∠A and ∠2 = ∠B, we substitute: ∠A + ∠C + ∠B = 180°.\n"
                    "4. Conclusion: The sum of interior angles in any triangle is always 180°. Q.E.D.!",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.22)", stroke_width=2.5, polygon_points=[(-3.0, 0.0), (4.0, 0.0), (0.0, 3.5)]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Line L ∥ AB", color="#38BDF8", stroke_width=2.2, dashed=True, coords=[-5.0, 3.5, 6.0, 3.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-3.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[4.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[0.0, 3.5, 4.5]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠A", color="#F59E0B", coords=[-3.0, 0.0, 0.9, 0.0, 49.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠B", color="#EC4899", coords=[4.0, 0.0, 0.9, 139.0, 41.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠C", color="#6C5CE7", coords=[0.0, 3.5, 0.9, 229.0, 90.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠1", color="#F59E0B", coords=[0.0, 3.5, 1.0, 180.0, 49.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠2", color="#EC4899", coords=[0.0, 3.5, 1.0, 319.0, 41.0]),
            # Full 180° arc banner
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Straight Line Sum", text="∠1 + ∠C + ∠2 = 180° (Straight Angle)", color="#2F9E78", coords=[-0.5, 5.0], font_size=13, bold=True),
        ]
    )

    proof.steps = [step1, step2, step3, step4]
    return proof


def create_thales_template() -> BuilderProof:
    """Thales's Theorem: If A, B, C are points on a circle where AB is a diameter, ∠ACB = 90°."""
    proof = BuilderProof(
        title="Thales's Theorem",
        description="Any angle inscribed in a semicircle is a right angle (90°)."
    )

    # Circle center (0, 0), radius 3.5. A(-3.5, 0), B(3.5, 0), C(1.5, 3.16)
    step1 = BuilderProofStep(
        index=1,
        title="Step 1: Circle with Diameter AB and Inscribed Point C",
        equation="Diameter AB with Radius r = 3.5",
        explanation="1. Goal: Draw circle with center O(0, 0) and diameter segment AB.\n"
                    "2. Point C: Place any point C along the upper circumference.\n"
                    "3. Question: What is the angle ∠ACB subtended by diameter AB?",
        shapes=[
            BuilderShape(shape_type=ShapeType.CIRCLE.value, name="Circle O", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.06)", stroke_width=2.0, coords=[0.0, 0.0, 3.5]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Diameter AB", color="#EAF0F6", stroke_width=2.2, coords=[-3.5, 0.0, 3.5, 0.0]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Chord AC", color="#5B8DEF", stroke_width=2.0, coords=[-3.5, 0.0, 1.5, 3.16]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Chord BC", color="#5B8DEF", stroke_width=2.0, coords=[3.5, 0.0, 1.5, 3.16]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="O(0,0)", color="#D8A94E", coords=[0.0, 0.0, 4.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-3.5, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[3.5, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[1.5, 3.16, 4.5]),
        ]
    )

    step2 = BuilderProofStep(
        index=2,
        title="Step 2: Draw Radius OC to Form Two Isosceles Triangles",
        equation="OA = OB = OC = r ⟹ ΔAOC & ΔBOC are Isosceles",
        explanation="1. Goal: Connect center O to vertex C with radius segment OC.\n"
                    "2. Why: Since OA, OB, and OC are all radii of the circle, OA = OB = OC = r.\n"
                    "3. Isosceles Property: ΔAOC has equal base angles α, and ΔBOC has equal base angles β.",
        shapes=[
            BuilderShape(shape_type=ShapeType.CIRCLE.value, name="Circle O", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.06)", stroke_width=2.0, coords=[0.0, 0.0, 3.5]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Diameter AB", color="#EAF0F6", stroke_width=2.2, coords=[-3.5, 0.0, 3.5, 0.0]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Chord AC", color="#5B8DEF", stroke_width=2.0, coords=[-3.5, 0.0, 1.5, 3.16]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Chord BC", color="#5B8DEF", stroke_width=2.0, coords=[3.5, 0.0, 1.5, 3.16]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Radius OC", color="#F59E0B", stroke_width=2.2, dashed=True, coords=[0.0, 0.0, 1.5, 3.16]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="O", color="#D8A94E", coords=[0.0, 0.0, 4.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-3.5, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[3.5, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[1.5, 3.16, 4.5]),
            # Base angles α and β
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="α", color="#38BDF8", coords=[-3.5, 0.0, 0.8, 0.0, 32.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="α", color="#38BDF8", coords=[1.5, 3.16, 0.8, 212.0, 32.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="β", color="#EC4899", coords=[3.5, 0.0, 0.8, 122.0, 58.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="β", color="#EC4899", coords=[1.5, 3.16, 0.8, 244.0, 58.0]),
        ]
    )

    step3 = BuilderProofStep(
        index=3,
        title="Step 3: Sum of Angles Proves Inscribed Angle ∠ACB = 90°",
        equation="2α + 2β = 180° ⟹ α + β = 90° ⟹ ∠ACB = 90°",
        explanation="1. Goal: Sum all angles in triangle ΔABC: α + (α + β) + β = 180°.\n"
                    "2. Simplification: 2α + 2β = 180° ⟹ 2(α + β) = 180° ⟹ α + β = 90°.\n"
                    "3. Conclusion: The total angle at vertex C is α + β = 90°. The inscribed angle in a semicircle is always a right angle!",
        shapes=[
            BuilderShape(shape_type=ShapeType.CIRCLE.value, name="Circle O", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.06)", stroke_width=2.0, coords=[0.0, 0.0, 3.5]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Diameter AB", color="#EAF0F6", stroke_width=2.2, coords=[-3.5, 0.0, 3.5, 0.0]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Chord AC", color="#5B8DEF", stroke_width=2.0, coords=[-3.5, 0.0, 1.5, 3.16]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Chord BC", color="#5B8DEF", stroke_width=2.0, coords=[3.5, 0.0, 1.5, 3.16]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Radius OC", color="#F59E0B", stroke_width=2.2, dashed=True, coords=[0.0, 0.0, 1.5, 3.16]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="O", color="#D8A94E", coords=[0.0, 0.0, 4.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-3.5, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[3.5, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[1.5, 3.16, 4.5]),
            # Right angle symbol at C!
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="90°", color="#2F9E78", is_right_angle=True, coords=[1.5, 3.16, 0.7, 212.0, 90.0]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="QED", text="∠ACB = α + β = 90° (Q.E.D.)", color="#2F9E78", coords=[-0.8, -1.2], font_size=13, bold=True),
        ]
    )

    proof.steps = [step1, step2, step3]
    return proof


def create_exterior_angle_template() -> BuilderProof:
    """Exterior Angle Theorem: Exterior angle of triangle equals sum of two opposite interior angles."""
    proof = BuilderProof(
        title="Exterior Angle Theorem",
        description="The measure of an exterior angle of a triangle is equal to the sum of the measures of its two remote interior angles: ∠ACD = ∠A + ∠B."
    )

    # Triangle ABC: A(-2, 3), B(-3, 0), C(2, 0), extended to D(5, 0)
    step1 = BuilderProofStep(
        index=1,
        title="Step 1: Triangle ΔABC with Extended Base Ray CD",
        equation="Interior: ∠A, ∠B, ∠ACB; Exterior: ∠ACD",
        explanation="1. Goal: Draw triangle ΔABC and extend base side BC past vertex C to point D.\n"
                    "2. Angles: ∠A and ∠B are the remote interior angles. ∠ACD is the exterior angle.\n"
                    "3. Objective: Relate exterior angle ∠ACD to interior angles ∠A and ∠B.",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.22)", stroke_width=2.5, polygon_points=[(-3.0, 0.0), (2.0, 0.0), (-2.0, 3.0)]),
            # Extended ray from C(2,0) to D(5,0)
            BuilderShape(shape_type=ShapeType.LINE.value, name="Ray CD", color="#EAF0F6", stroke_width=2.2, coords=[2.0, 0.0, 5.0, 0.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[-3.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[2.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-2.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="D", color="#EAF0F6", coords=[5.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠A", color="#F59E0B", coords=[-2.0, 3.0, 0.8, 250.0, 35.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠B", color="#38BDF8", coords=[-3.0, 0.0, 0.8, 0.0, 71.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠ACB", color="#6C5CE7", coords=[2.0, 0.0, 0.8, 143.0, 37.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠ACD (ext)", color="#EC4899", coords=[2.0, 0.0, 0.9, 0.0, 143.0]),
        ]
    )

    step2 = BuilderProofStep(
        index=2,
        title="Step 2: Linear Pair at Vertex C",
        equation="∠ACB + ∠ACD = 180° (Supplementary)",
        explanation="1. Goal: Notice that adjacent angles ∠ACB and ∠ACD form a straight line on ray BD.\n"
                    "2. Linear Pair Postulate: Two adjacent angles on a straight line always sum to 180°.\n"
                    "3. Equation: ∠ACB + ∠ACD = 180°.",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.22)", stroke_width=2.5, polygon_points=[(-3.0, 0.0), (2.0, 0.0), (-2.0, 3.0)]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Ray CD", color="#EAF0F6", stroke_width=2.2, coords=[2.0, 0.0, 5.0, 0.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[-3.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[2.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-2.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="D", color="#EAF0F6", coords=[5.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠ACB", color="#6C5CE7", coords=[2.0, 0.0, 0.8, 143.0, 37.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠ACD", color="#EC4899", coords=[2.0, 0.0, 0.9, 0.0, 143.0]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Supplementary Note", text="∠ACB + ∠ACD = 180°", color="#EC4899", coords=[1.0, 2.0], font_size=12, bold=True),
        ]
    )

    step3 = BuilderProofStep(
        index=3,
        title="Step 3: Equate Angle Sums & Prove ∠ACD = ∠A + ∠B",
        equation="∠A + ∠B + ∠ACB = 180° = ∠ACB + ∠ACD ⟹ ∠ACD = ∠A + ∠B",
        explanation="1. Angle Sum: In ΔABC, ∠A + ∠B + ∠ACB = 180°.\n"
                    "2. Linear Pair: ∠ACD + ∠ACB = 180°.\n"
                    "3. Equating both: ∠A + ∠B + ∠ACB = ∠ACD + ∠ACB.\n"
                    "4. Subtracting ∠ACB: Exterior angle ∠ACD = ∠A + ∠B. Q.E.D.!",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.22)", stroke_width=2.5, polygon_points=[(-3.0, 0.0), (2.0, 0.0), (-2.0, 3.0)]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Ray CD", color="#EAF0F6", stroke_width=2.2, coords=[2.0, 0.0, 5.0, 0.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[-3.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[2.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-2.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="D", color="#EAF0F6", coords=[5.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠A", color="#F59E0B", coords=[-2.0, 3.0, 0.8, 250.0, 35.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠B", color="#38BDF8", coords=[-3.0, 0.0, 0.8, 0.0, 71.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="∠ACD = ∠A + ∠B", color="#2F9E78", coords=[2.0, 0.0, 1.1, 0.0, 143.0]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Conclusion", text="∠ACD = ∠A + ∠B (Q.E.D.)", color="#2F9E78", coords=[-1.0, -1.0], font_size=13, bold=True),
        ]
    )

    proof.steps = [step1, step2, step3]
    return proof


def create_triangle_area_template() -> BuilderProof:
    """Proof that Area(Triangle) = ½ · base · height."""
    proof = BuilderProof(
        title="Area of a Triangle",
        description="Every triangle has an area equal to exactly half of the parallelogram formed with the same base and height: Area = ½ · b · h."
    )

    # Triangle ABC: base along x axis from (0,0) to (5,0), height 3 at C(2, 3)
    step1 = BuilderProofStep(
        index=1,
        title="Step 1: Triangle with Base b and Perpendicular Altitude h",
        equation="Base b = 5.0, Height h = 3.0",
        explanation="1. Goal: Given triangle ΔABC with base AB = 5.0 and altitude h = 3.0 dropped from vertex C.\n"
                    "2. Objective: Derive the formula for its enclosed two-dimensional surface area.",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.25)", stroke_width=2.5, polygon_points=[(0.0, 0.0), (5.0, 0.0), (2.0, 3.0)]),
            # Altitude line from (2, 3) to (2, 0)
            BuilderShape(shape_type=ShapeType.LINE.value, name="Altitude h", color="#F59E0B", stroke_width=2.0, dashed=True, coords=[2.0, 3.0, 2.0, 0.0]),
            BuilderShape(shape_type=ShapeType.ANGLE.value, name="90°", color="#F59E0B", is_right_angle=True, coords=[2.0, 0.0, 0.45, 0.0, 90.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A(0,0)", color="#EAF0F6", coords=[0.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B(5,0)", color="#EAF0F6", coords=[5.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C(2,3)", color="#EAF0F6", coords=[2.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Base b", text="Base b = 5.0", color="#5B8DEF", coords=[2.5, -0.4], font_size=12, bold=True),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Height h", text="h = 3.0", color="#F59E0B", coords=[2.15, 1.5], font_size=12, bold=True),
        ]
    )

    step2 = BuilderProofStep(
        index=2,
        title="Step 2: Duplicate ΔABC to Form a Parallelogram",
        equation="Parallelogram = 2 × ΔABC",
        explanation="1. Goal: Rotate an identical copy of ΔABC by 180° and attach it along side BC.\n"
                    "2. Why: The two congruent triangles assemble into parallelogram AB'CA.\n"
                    "3. Vertices: Parallelogram vertices are (0,0), (5,0), (7,3), and (2,3).",
        shapes=[
            # Original triangle
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.30)", stroke_width=2.5, polygon_points=[(0.0, 0.0), (5.0, 0.0), (2.0, 3.0)]),
            # Duplicate triangle forming parallelogram: (5,0) -> (7,3) -> (2,3)
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="Copy Δ", color="#2F9E78", fill_color="rgba(47, 158, 120, 0.30)", stroke_width=2.5, polygon_points=[(5.0, 0.0), (7.0, 3.0), (2.0, 3.0)]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Altitude h", color="#F59E0B", stroke_width=2.0, dashed=True, coords=[2.0, 3.0, 2.0, 0.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A(0,0)", color="#EAF0F6", coords=[0.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B(5,0)", color="#EAF0F6", coords=[5.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C(2,3)", color="#EAF0F6", coords=[2.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="D(7,3)", color="#EAF0F6", coords=[7.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Parallelogram", text="Parallelogram = 2 × ΔABC", color="#2F9E78", coords=[3.5, 3.5], font_size=12, bold=True),
        ]
    )

    step3 = BuilderProofStep(
        index=3,
        title="Step 3: Area of Triangle is Half the Parallelogram",
        equation="Area(Parallelogram) = b · h = 15.0 ⟹ Area(ΔABC) = ½ · b · h = 7.5",
        explanation="1. Area of Parallelogram: Base × Height = 5.0 × 3.0 = 15.0.\n"
                    "2. Since the parallelogram is composed of two identical triangles:\n"
                    "   Area(ΔABC) = ½ × Area(Parallelogram) = ½ · b · h = 7.5.\n"
                    "3. Conclusion: The formula Area = ½ · b · h is proven for all triangles!",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#5B8DEF", fill_color="rgba(91, 141, 239, 0.35)", stroke_width=2.5, polygon_points=[(0.0, 0.0), (5.0, 0.0), (2.0, 3.0)]),
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="Copy Δ", color="#2F9E78", fill_color="rgba(47, 158, 120, 0.20)", stroke_width=2.0, dashed=True, polygon_points=[(5.0, 0.0), (7.0, 3.0), (2.0, 3.0)]),
            BuilderShape(shape_type=ShapeType.LINE.value, name="Altitude h", color="#F59E0B", stroke_width=2.0, dashed=True, coords=[2.0, 3.0, 2.0, 0.0]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A(0,0)", color="#EAF0F6", coords=[0.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B(5,0)", color="#EAF0F6", coords=[5.0, 0.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C(2,3)", color="#EAF0F6", coords=[2.0, 3.0, 4.5]),
            BuilderShape(shape_type=ShapeType.TEXT.value, name="Area Formula", text="Area(Δ) = ½ · base · height = 7.5 (Q.E.D.)", color="#5B8DEF", coords=[1.0, -1.0], font_size=13, bold=True),
        ]
    )

    proof.steps = [step1, step2, step3]
    return proof


def create_blank_template() -> BuilderProof:
    """Clean starter template with coordinate system and starter triangle."""
    proof = BuilderProof(
        title="Custom Theorem Proof",
        description="Construct your custom geometric theorem proof step-by-step."
    )
    step1 = BuilderProofStep(
        index=1,
        title="Step 1: Initial Construction",
        equation="",
        explanation="1. Goal: Place geometric shapes, points, lines, and angles to begin your proof.\n"
                    "2. Tip: Use the toolbar to drop points, draw lines or polygons, and annotate angles.",
        shapes=[
            BuilderShape(shape_type=ShapeType.POLYGON.value, name="ΔABC", color="#6C5CE7", fill_color="rgba(108, 92, 231, 0.22)", stroke_width=2.2, polygon_points=[(-2.5, -1.0), (2.5, -1.0), (0.0, 2.5)]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="A", color="#EAF0F6", coords=[-2.5, -1.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="B", color="#EAF0F6", coords=[2.5, -1.0, 4.5]),
            BuilderShape(shape_type=ShapeType.POINT.value, name="C", color="#EAF0F6", coords=[0.0, 2.5, 4.5]),
        ]
    )
    proof.steps = [step1]
    return proof

