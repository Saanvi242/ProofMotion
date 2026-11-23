"""
core/practical_content.py
-------------------------
Repository of practical examples, real-world engineering applications,
and lightweight interactive knowledge checks for all ProofMotion lessons.

Bridges theoretical proofs and algorithmic mechanics with authentic industrial,
software, and scientific applications across all 8 project curriculum areas.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class RealWorldApplication:
    title: str
    description: str
    contexts: List[str]
    tag: str = "Software Systems"


@dataclass
class PracticalExample:
    scenario: str
    description: str
    visualization_connection: str


@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_index: int
    explanation: str


@dataclass
class TopicPracticalData:
    topic_key: str
    display_name: str
    category: str
    summary: str
    practical_example: PracticalExample
    real_world_applications: List[RealWorldApplication]
    knowledge_check: List[QuizQuestion] = field(default_factory=list)


# ======================================================================
# COMPREHENSIVE REPOSITORY FOR ALL PROOFMOTION TOPICS
# ======================================================================

PRACTICAL_KNOWLEDGE_BASE: Dict[str, TopicPracticalData] = {
    # ------------------------------------------------------------------
    # 1. MATHEMATICAL THEOREMS
    # ------------------------------------------------------------------
    "pythagorean": TopicPracticalData(
        topic_key="pythagorean",
        display_name="Pythagorean Theorem",
        category="Mathematical Theorems",
        summary="Relates the three sides of a right triangle: a² + b² = c².",
        practical_example=PracticalExample(
            scenario="Screen Resolution Diagonal & Sports Field Measurements",
            description=(
                "When a display is marketed as '27-inch', that measurement is the diagonal hypotenuse "
                "across its rectangular panel. Knowing a 16:9 monitor has a width of 23.5 inches and height of 13.2 inches, "
                "engineers apply a² + b² = c² to manufacture casing and monitor mounts with millimeter accuracy."
            ),
            visualization_connection=(
                "In the ProofMotion canvas, adjusting legs side_a and side_b continuously recalculates the square areas "
                "built upon each leg. The geometric rearrangement visually verifies that area(a²) + area(b²) matches area(c²)."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Collision Detection in Game Physics Engines",
                description=(
                    "Physics engines (like PhysX and Havok) determine whether two circular or spherical game characters "
                    "collide by computing the Euclidean distance between their center points using the Pythagorean theorem."
                ),
                contexts=[
                    "Circular hitboxes in 2D platformers and battle royales.",
                    "Optimized squared-distance testing: avoids expensive sqrt() calls via (Δx² + Δy² ≤ (r₁ + r₂)²).",
                    "Particle systems simulating rain, sparks, and explosion debris bounds.",
                ],
                tag="Game Physics",
            ),
            RealWorldApplication(
                title="GPS Trilateration & Navigation",
                description=(
                    "Global Positioning System (GPS) receivers compute your precise position on Earth by measuring "
                    "the straight-line transit distance to four or more satellites using 3D Pythagorean distance equations."
                ),
                contexts=[
                    "Mobile turn-by-turn navigation (Google Maps, Apple Maps).",
                    "Autonomous drone waypoint navigation and geofencing.",
                    "Earthquake epicenter localization by seismological sensor networks.",
                ],
                tag="Geospatial Navigation",
            ),
            RealWorldApplication(
                title="Vector Normalization in Shaders & Computer Graphics",
                description=(
                    "GPU vertex and fragment shaders compute vector magnitudes via ||v|| = √(x² + y² + z²). Normalizing "
                    "surface normals to unit vectors (magnitude 1.0) is the foundational requirement for realistic lighting."
                ),
                contexts=[
                    "Blinn-Phong and PBR (Physically-Based Rendering) lighting models.",
                    "Reflection and refraction ray calculations in real-time ray tracing.",
                    "Skeletal rigging bone length constraints in 3D character animation.",
                ],
                tag="Computer Graphics",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why do physics engines check (Δx² + Δy² ≤ (r₁ + r₂)²) rather than √(Δx² + Δy²) ≤ (r₁ + r₂)?",
                options=[
                    "Square roots are approximated and produce wrong numbers",
                    "Avoiding square root calls saves substantial CPU/GPU cycles on millions of particle tests",
                    "The Pythagorean theorem only holds when values are squared",
                    "Radii cannot be compared directly without trigonometry",
                ],
                correct_index=1,
                explanation="Computing square roots is computationally expensive in hot game loops. Comparing squared distance directly yields identical boolean collision decisions with pure multiplications and additions.",
            ),
            QuizQuestion(
                question="What fundamental property of Euclidean 2D space does the Pythagorean theorem establish?",
                options=[
                    "The sum of angles in a triangle is 360°",
                    "The shortest distance between two points (x₁, y₁) and (x₂, y₂) is √((x₂ - x₁)² + (y₂ - y₁)²)",
                    "Lines in the plane never intersect",
                    "All polygons can be clipped using 4-bit outcodes",
                ],
                correct_index=1,
                explanation="The standard Euclidean metric (L2 norm) that defines straight-line distance across coordinate geometry is directly derived from the Pythagorean theorem.",
            ),
            QuizQuestion(
                question="In 3D graphics and physics engines, how is the Euclidean distance between two points (x1, y1, z1) and (x2, y2, z2) computed?",
                options=[
                    "d = √((x2 - x1)² + (y2 - y1)² + (z2 - z1)²)",
                    "d = (x2 - x1) + (y2 - y1) + (z2 - z1)",
                    "d = √((x2 - x1) + (y2 - y1) + (z2 - z1))",
                    "d = (x2 - x1)² + (y2 - y1)² + (z2 - z1)²",
                ],
                correct_index=0,
                explanation="The 3D distance formula is the direct extension of the Pythagorean theorem across three orthogonal coordinate axes.",
            ),
        ],
    ),

    "circle_area": TopicPracticalData(
        topic_key="circle_area",
        display_name="Circle Geometry & Area",
        category="Mathematical Theorems",
        summary="Explores the relationship between radius, circumference (2πr), and area (πr²).",
        practical_example=PracticalExample(
            scenario="5G Cellular Base Station Coverage & Pizza Value Comparison",
            description=(
                "A cellular network provider placing a 5G small cell must know how much ground area is covered. "
                "Because area scales with the square of the radius (πr²), doubling transmission radius quadruples the covered land area. "
                "The same math reveals why one 18-inch pizza offers more food area than two 12-inch pizzas."
            ),
            visualization_connection=(
                "In ProofMotion, varying the radius slider visualizes both the circular boundary and radial sector dissections, "
                "demonstrating how unwrapping circular sectors approaches a rectangle of width πr and height r."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Geographic Information Systems (GIS) Radial Buffering",
                description=(
                    "Spatial databases (like PostGIS and Esri ArcGIS) generate radial buffer polygons around geographic coordinates "
                    "to evaluate environmental impact zones, school district zones, or delivery availability radiuses."
                ),
                contexts=[
                    "Querying all delivery addresses within 5 km of an urban logistics warehouse.",
                    "Calculating hazardous chemical fallout zones during industrial containment incidents.",
                    "Noise pollution contour modeling around airport flight paths.",
                ],
                tag="Spatial Databases",
            ),
            RealWorldApplication(
                title="Pipeline & Pipe Flow Hydraulic Capacity",
                description=(
                    "Civil and mechanical engineers calculate hydraulic volumetric throughput in water, oil, and gas pipelines. "
                    "Cross-sectional area A = πr² dictates maximum flow rate for a given fluid velocity."
                ),
                contexts=[
                    "Municipal water distribution and stormwater drainage sizing.",
                    "Semiconductor cooling loop heat-dissipation pipes.",
                    "Aerospace fuel injection nozzle calibration.",
                ],
                tag="Engineering & Fluid Dynamics",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="If a municipal water pipe's radius is doubled from 10 cm to 20 cm, how does its cross-sectional area change?",
                options=[
                    "It doubles (increases by 2×)",
                    "It triples (increases by 3×)",
                    "It quadruples (increases by 4×, since A ∝ r²)",
                    "It increases by π (approximately 3.14×)",
                ],
                correct_index=2,
                explanation="Because area depends on r², doubling the radius scales the area by 2² = 4 times, allowing 4× the volumetric flow capacity.",
            ),
            QuizQuestion(
                question="How does the sector dissection method visually prove that the area of a circle equals πr²?",
                options=[
                    "By folding the circle into a single right triangle of hypotenuse r",
                    "By slicing the circle into sectors that reassemble into a shape approaching a rectangle of base πr and height r",
                    "By rotating the circle around its diameter into a sphere",
                    "By measuring the diameter with a discrete pixel grid",
                ],
                correct_index=1,
                explanation="As the number of sectors approaches infinity, the shape approaches a rectangle with base equal to half the circumference (πr) and height r, yielding Area = πr × r = πr².",
            ),
            QuizQuestion(
                question="In GIS spatial buffering, what geometric boundary is formed by the set of all points within distance R from a single center point?",
                options=[
                    "A bounding box with width equal to radius",
                    "A planar circle of radius R enclosing an area of πR²",
                    "A convex hull connecting neighboring coordinates",
                    "A Voronoi polygon cell",
                ],
                correct_index=1,
                explanation="A radial buffer generates all points within Euclidean distance R from the epicenter, forming a circular region of area πR².",
            ),
        ],
    ),

    "similar_triangles": TopicPracticalData(
        topic_key="similar_triangles",
        display_name="Similar Triangles",
        category="Mathematical Theorems",
        summary="Proves and demonstrates geometric scaling where corresponding angles are equal and side ratios are proportional.",
        practical_example=PracticalExample(
            scenario="Estimating Tree & Monument Heights from Ground Shadows",
            description=(
                "Forestry surveyors and civil engineers estimate the height of inaccessible towers or giant redwood trees "
                "without climbing them. By placing a 2-meter vertical stick in the ground and measuring both the stick's shadow "
                "and the tower's shadow, equal solar angles yield identical triangle ratios: Height_tower = Shadow_tower × (Height_stick / Shadow_stick)."
            ),
            visualization_connection=(
                "ProofMotion renders two connected triangles under parameter scaling factor k, showing that even as vertices move, "
                "side ratios a₁/a₂ = b₁/b₂ = c₁/c₂ remain strictly constant."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Perspective Camera Projection in 3D Graphics",
                description=(
                    "All 3D game engines (Unreal Engine, Unity) and GPU projection matrices convert 3D coordinates (X, Y, Z) "
                    "into 2D screen pixels (x, y) using similar triangles formed between the virtual camera focal point, the image plane, and the 3D scene point."
                ),
                contexts=[
                    "Screen projection formula: x_screen = focal_length × (X_world / Z_depth).",
                    "Pinhole camera models in computer vision and robotics.",
                    "Autonomous vehicle stereoscopic cameras estimating vehicle distance.",
                ],
                tag="3D Computer Graphics",
            ),
            RealWorldApplication(
                title="Optical Rangefinding & Photography Focal Depth",
                description=(
                    "Camera autofocus sensors and optical rangefinders measure distance by comparing the displacement "
                    "of light rays passing through dual lens elements using proportional triangle geometry."
                ),
                contexts=[
                    "Phase-detection autofocus (PDAF) in smartphone cameras.",
                    "Surveyor theodolites and laser triangulation sensors.",
                    "Depth-of-field circle of confusion calculations in CGI rendering.",
                ],
                tag="Optics & Computer Vision",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="In 3D computer graphics, how do similar triangles explain why distant objects appear smaller?",
                options=[
                    "Distant objects lose RGB color saturation",
                    "Projected screen coordinate x_screen is proportional to X/Z; as depth Z increases, x_screen shrinks",
                    "Graphics drivers clip all polygons located past 100 meters",
                    "Focal length decreases when camera moves forward",
                ],
                correct_index=1,
                explanation="By similar triangles with the camera center, x_screen / focal_length = X_world / Z_depth. Dividing by larger Z depths directly scales projected coordinates down.",
            ),
            QuizQuestion(
                question="Which geometric criterion is sufficient to establish that two Euclidean triangles are similar?",
                options=[
                    "They have identical perimeter lengths",
                    "Two pairs of corresponding interior angles are equal (AA criterion)",
                    "Both triangles contain at least one right angle regardless of other angles",
                    "Their areas are exactly equal",
                ],
                correct_index=1,
                explanation="The Angle-Angle (AA) criterion guarantees that the triangles share identical interior angles, meaning all corresponding side lengths are strictly proportional.",
            ),
            QuizQuestion(
                question="In a pinhole camera model, if a 2-meter tall object is 10 meters away and the focal length is 0.05 meters, what is the projected image height on the sensor?",
                options=[
                    "0.01 meters (10 mm)",
                    "0.10 meters (100 mm)",
                    "0.40 meters (400 mm)",
                    "1.00 meters (1000 mm)",
                ],
                correct_index=0,
                explanation="By similar triangles: Image Height / Focal Length = Object Height / Distance. Image Height = (2 m / 10 m) × 0.05 m = 0.01 m (10 mm).",
            ),
        ],
    ),

    "law_of_cosines": TopicPracticalData(
        topic_key="law_of_cosines",
        display_name="Law of Cosines",
        category="Mathematical Theorems",
        summary="Generalizes the Pythagorean theorem to any arbitrary triangle: c² = a² + b² - 2ab·cos(γ).",
        practical_example=PracticalExample(
            scenario="Aviation Navigation Across Crosswinds",
            description=(
                "An aircraft heading East at 500 km/h encounters a 100 km/h crosswind blowing at a 45° angle. "
                "Because the aircraft airspeed vector and wind vector form a non-right triangle, flight management computers "
                "use the Law of Cosines to compute the exact ground speed and drift compensation angle to stay on course."
            ),
            visualization_connection=(
                "ProofMotion allows adjusting sides a, b and interior angle γ. The dynamic diagram highlights the correction term "
                "-2ab·cos(γ), showing how acute angles reduce side c below the right-triangle hypotenuse while obtuse angles expand it."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Robotic Arm Kinematics & Motion Planning",
                description=(
                    "Industrial robotic arms (such as welding and assembly robots) use inverse kinematics to reach an object in 3D space. "
                    "The Law of Cosines computes the exact motor elbow angle required given the known upper arm and forearm link lengths."
                ),
                contexts=[
                    "Automated manufacturing assembly lines (KUKA, ABB, Fanuc robots).",
                    "Robotic surgical systems (da Vinci surgical robotic joint controllers).",
                    "Bipedal humanoid robot knee and ankle balancing algorithms.",
                ],
                tag="Robotics & Control",
            ),
            RealWorldApplication(
                title="Geodesy, Surveying & Flight Path Triangulation",
                description=(
                    "Land surveyors calculate the distance between two inaccessible mountain peaks by standing at a third known vantage point, "
                    "measuring distances to both peaks with laser rangefinders, and measuring the angle between them using a theodolite."
                ),
                contexts=[
                    "Satellite orbital orientation and attitude determination.",
                    "Continental tectonic plate displacement monitoring via GPS arrays.",
                    "Acoustic sensor array localization in naval submarine defense.",
                ],
                tag="Surveying & Geodesy",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="When the included angle γ in the Law of Cosines equals 90°, what happens to the formula c² = a² + b² - 2ab·cos(γ)?",
                options=[
                    "It becomes undefined because of division by zero",
                    "It simplifies exactly to the Pythagorean theorem c² = a² + b² because cos(90°) = 0",
                    "It calculates the perimeter instead of side c",
                    "The triangle collapses into a single line segment",
                ],
                correct_index=1,
                explanation="Because cos(90°) = 0, the term -2ab(0) drops out, confirming that the Pythagorean theorem is simply a special case of the Law of Cosines for right triangles.",
            ),
            QuizQuestion(
                question="In vector mathematics and graphics shaders, how is the dot product of two vectors related to the Law of Cosines?",
                options=[
                    "The dot product u · v equals ||u|| ||v|| cos(θ), directly mirroring the -2ab cos(θ) term in the Law of Cosines",
                    "The dot product only applies to parallel vectors",
                    "The dot product produces the cross product normal",
                    "The Law of Cosines cannot be expressed with vectors",
                ],
                correct_index=0,
                explanation="Expanding the squared norm ||u - v||² = ||u||² + ||v||² - 2(u · v) demonstrates that the vector dot product u · v = ||u|| ||v|| cos(θ) is the vector algebraic equivalent of the Law of Cosines.",
            ),
            QuizQuestion(
                question="In robotic kinematics, why is the Law of Cosines indispensable for two-link planar inverse kinematics?",
                options=[
                    "It calculates the motor voltage directly",
                    "It computes the required elbow joint angle given target coordinates and fixed link lengths",
                    "It ensures the robot does not exceed its maximum payload",
                    "It eliminates the need for trigonometric calculations",
                ],
                correct_index=1,
                explanation="Knowing the two rigid arm lengths a and b and the Euclidean distance c to the target, the Law of Cosines directly computes the interior elbow angle required to place the tool.",
            ),
        ],
    ),

    # ------------------------------------------------------------------
    # 2. SORTING ALGORITHMS
    # ------------------------------------------------------------------
    "bubble_sort": TopicPracticalData(
        topic_key="bubble_sort",
        display_name="Bubble Sort",
        category="Sorting Algorithms",
        summary="Repeatedly steps through the list, compares adjacent elements, and swaps them if out of order.",
        practical_example=PracticalExample(
            scenario="Arranging Student Test Papers by Mark",
            description=(
                "Imagine a teacher holding a small stack of 8 graded papers. Walking through the stack, they compare pairs "
                "of adjacent papers and swap them whenever the first is higher than the second. By the end of the first pass, "
                "the highest mark has 'bubbled' to the very bottom."
            ),
            visualization_connection=(
                "ProofMotion animates adjacent bar comparisons with comparison brackets and color-coded swaps. "
                "The sorted partition locks in at the right end of the array after each outer pass."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Embedded Microcontrollers & Sensor Calibration",
                description=(
                    "On tiny microcontrollers with very limited ROM and RAM (such as an 8-bit AVR or PIC chip with 256 bytes of memory), "
                    "Bubble Sort's zero-overhead in-place code footprint (just two loops and one swap variable) makes it ideal for sorting tiny sensor calibration buffers."
                ),
                contexts=[
                    "Discarding minimum and maximum outlier readings from analog temperature sensors.",
                    "Sorting small priority queues in ultra-low-power IoT nodes.",
                    "Deterministic execution verification in safety-critical firmware.",
                ],
                tag="Embedded Systems",
            ),
            RealWorldApplication(
                title="Detecting Already-Sorted Data Streams",
                description=(
                    "When an algorithm processes a stream of records that is almost always already sorted (with occasional minor swaps), "
                    "Bubble Sort with an early-exit flag checks and completes in linear O(n) time and single-pass latency."
                ),
                contexts=[
                    "Verifying sorting order integrity in real-time communication packet queues.",
                    "Compiler optimizations validating that basic blocks are ordered by execution frequency.",
                ],
                tag="Systems Programming",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Under what condition does an optimized Bubble Sort achieve its best-case O(n) time complexity?",
                options=[
                    "When the input array is sorted in reverse order",
                    "When the input array is already completely sorted and an early-termination flag detects zero swaps on pass 1",
                    "When the array contains exclusively negative numbers",
                    "When executed on multi-core GPU shader processors",
                ],
                correct_index=1,
                explanation="With a boolean swap flag, if the first pass traverses all n-1 adjacent pairs without making a single swap, the algorithm safely terminates immediately after O(n) comparisons.",
            ),
            QuizQuestion(
                question="What is the maximum number of element comparisons performed by Bubble Sort on an array of n items in the worst case?",
                options=[
                    "n log n",
                    "n(n - 1) / 2",
                    "n",
                    "2ⁿ",
                ],
                correct_index=1,
                explanation="In the worst case (reverse sorted array), Bubble Sort performs (n - 1) + (n - 2) + ... + 1 = n(n - 1)/2 comparisons, which is O(n²).",
            ),
            QuizQuestion(
                question="Why is standard Bubble Sort classified as a stable sorting algorithm?",
                options=[
                    "It uses no additional memory beyond the array",
                    "It only swaps adjacent elements when one is strictly greater, preserving the relative order of duplicate keys",
                    "It guarantees O(n log n) execution time",
                    "It divides the array recursively",
                ],
                correct_index=1,
                explanation="Because adjacent elements are only swapped when A[j] > A[j+1] (strict inequality), equal elements never pass each other, preserving their initial relative order.",
            ),
        ],
    ),

    "selection_sort": TopicPracticalData(
        topic_key="selection_sort",
        display_name="Selection Sort",
        category="Sorting Algorithms",
        summary="Divides the list into sorted and unsorted parts, repeatedly finding the minimum element to append to the sorted prefix.",
        practical_example=PracticalExample(
            scenario="Selecting Cheapest Flight Deals to Display on Top",
            description=(
                "A travel website finds the cheapest flight among 50 options and pins it to position #1, then finds the next cheapest "
                "among the remaining 49 and pins it to position #2. This avoids unnecessary swapping until the absolute minimum is confirmed."
            ),
            visualization_connection=(
                "ProofMotion displays an active 'current minimum' search pointer scanning across the unsorted region. "
                "Once the pass ends, a single swap places the true minimum into its final sorted slot on the left."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Wear-Leveling on EEPROM & Flash Memory",
                description=(
                    "Flash memory and EEPROMs have physical limits on write cycles (often 10,000 to 100,000 writes before memory cell degradation). "
                    "Selection sort performs at most O(n) write operations (exactly n - 1 swaps in the worst case), compared to O(n²) writes in Bubble Sort."
                ),
                contexts=[
                    "Automotive Engine Control Unit (ECU) parameter logging.",
                    "Smart electricity meters updating cumulative consumption records.",
                    "Aerospace flight data recorder black boxes.",
                ],
                tag="Hardware & Memory Systems",
            ),
            RealWorldApplication(
                title="Top-K Leaderboard Extraction",
                description=(
                    "When a gaming server only needs to display the top 3 highest scores out of 100 players, running just 3 passes "
                    "of Selection Sort extracts the top 3 items in O(k·n) time without needing to sort the remaining 97 elements."
                ),
                contexts=[
                    "Online game match result highlights.",
                    "E-commerce product ranking showing top-3 price cuts.",
                ],
                tag="Data Analysis",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why is Selection Sort advantageous when writing data to Flash/EEPROM storage devices?",
                options=[
                    "It has an O(n log n) comparison speed",
                    "It makes at most O(n) memory writes/swaps, minimizing physical wear on memory cells",
                    "It consumes O(n) auxiliary RAM to cache data blocks",
                    "It automatically encrypts records during swapping",
                ],
                correct_index=1,
                explanation="Even though Selection Sort does O(n²) comparisons, it executes at most n - 1 swaps total, preserving the endurance life of flash memory cells.",
            ),
            QuizQuestion(
                question="What is the time complexity of Selection Sort in the best-case scenario (when the input array is already sorted)?",
                options=[
                    "O(n)",
                    "O(n log n)",
                    "O(n²)",
                    "O(1)",
                ],
                correct_index=2,
                explanation="Unlike Bubble Sort or Insertion Sort, Selection Sort always scans the entire unsorted suffix to identify the minimum element, requiring exactly n(n - 1)/2 comparisons regardless of initial order.",
            ),
            QuizQuestion(
                question="How many total element write/swap operations does standard Selection Sort perform at most on an array of n items?",
                options=[
                    "O(n²)",
                    "At most n - 1 swaps (O(n))",
                    "Zero swaps",
                    "n log n swaps",
                ],
                correct_index=1,
                explanation="Selection Sort performs at most one swap per outer loop pass, giving a maximum of n - 1 swaps across the entire sort. This minimal write property is advantageous on write-sensitive hardware.",
            ),
        ],
    ),

    "insertion_sort": TopicPracticalData(
        topic_key="insertion_sort",
        display_name="Insertion Sort",
        category="Sorting Algorithms",
        summary="Builds the final sorted array one item at a time by inserting each element into its proper position among prior items.",
        practical_example=PracticalExample(
            scenario="Sorting Playing Cards in Your Hand",
            description=(
                "When dealt cards one by one in card games like Poker or Bridge, players keep their hand sorted. "
                "As each new card arrives, you glance backwards through your cards, shift larger cards to the right, "
                "and slide the new card directly into its correct numerical slot."
            ),
            visualization_connection=(
                "ProofMotion lifts the active key element, slides preceding larger bars one slot to the right, "
                "and drops the key into its sorted slot, clearly illustrating the growing sorted prefix."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Hybrid Production Sorters: Python Timsort & C++ std::sort",
                description=(
                    "The production sort implementations in Python (Timsort), Java (Dual-Pivot Quicksort), and C++ (Introsort) "
                    "switch directly to Insertion Sort for sub-arrays of size ≤ 16 to 32 elements."
                ),
                contexts=[
                    "High CPU cache locality and near-zero function call overhead on small arrays.",
                    "Adaptive linear O(n) speed on partially pre-sorted chunks.",
                    "V8 JavaScript engine optimizing small JSON property lists.",
                ],
                tag="Standard Libraries & Compilers",
            ),
            RealWorldApplication(
                title="Online Real-Time Event & Transaction Ingestion",
                description=(
                    "Financial order books and sensor feeds receive transactions that usually arrive in chronological order "
                    "with minor network latency jitter. Insertion Sort continuously integrates arriving elements in near O(1) time."
                ),
                contexts=[
                    "High-frequency stock exchange limit-order book price-level queues.",
                    "Audio sample packet resequencing in VoIP and video streaming (WebRTC).",
                    "Log aggregator timestamp sequencing.",
                ],
                tag="Real-Time Streaming",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why do advanced sorting algorithms like Timsort switch to Insertion Sort for small slices (n ≤ 32)?",
                options=[
                    "Insertion Sort requires no comparisons",
                    "Low constant factors, lack of recursion overhead, and high CPU cache locality make it faster than Quicksort on tiny sets",
                    "Insertion Sort runs in O(log n) time on small sets",
                    "Timsort only supports Insertion Sort",
                ],
                correct_index=1,
                explanation="Quicksort and Mergesort have recursive call and partitioning overhead. For small sizes (n ≤ 32), Insertion Sort's tight inner loop runs straight in CPU L1 cache with minimal overhead.",
            ),
            QuizQuestion(
                question="What is the time complexity of Insertion Sort when given an array that is already completely sorted?",
                options=[
                    "O(n)",
                    "O(n²)",
                    "O(n log n)",
                    "O(1)",
                ],
                correct_index=0,
                explanation="For an already sorted array, each element is compared only once with its immediate predecessor and placed without shifting, taking exactly n - 1 comparisons (O(n) time).",
            ),
            QuizQuestion(
                question="How does Insertion Sort process an array as it executes?",
                options=[
                    "It partitions elements around a pivot value",
                    "It incrementally builds a sorted prefix by taking the next item and shifting larger preceding items to the right",
                    "It repeatedly finds the global minimum and swaps it to the front",
                    "It converts the array into a binary max-heap",
                ],
                correct_index=1,
                explanation="At step i, elements A[0...i-1] are already sorted. Element A[i] is inserted into its correct position within that prefix by shifting elements greater than it one position right.",
            ),
        ],
    ),

    "merge_sort": TopicPracticalData(
        topic_key="merge_sort",
        display_name="Merge Sort",
        category="Sorting Algorithms",
        summary="Divide-and-conquer algorithm that recursively splits arrays in half, sorts each half, and merges the sorted sub-lists.",
        practical_example=PracticalExample(
            scenario="Combining Ranked Scores from Two Exam Centers",
            description=(
                "If School A and School B have already sorted their 500 students by rank, creating one unified 1,000-student ranking "
                "does not require re-sorting everyone from scratch. Comparing only the two top remaining students and picking the higher "
                "merges both rosters in a single clean pass."
            ),
            visualization_connection=(
                "ProofMotion highlights recursive divide boundaries with colored groupings, followed by bottom-up merge steps "
                "where two sorted sub-arrays are joined element by element into temporary buffers."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="External Sorting in Databases (PostgreSQL, SQLite)",
                description=(
                    "When database queries sort billions of rows (e.g. ORDER BY) that exceed available server RAM, "
                    "the database engine writes sorted chunks to disk and uses multi-way external Merge Sort to produce the final result."
                ),
                contexts=[
                    "PostgreSQL work_mem disk spill merges.",
                    "Big data MapReduce and Apache Spark shuffle sort phases.",
                    "High-volume data warehouse ETL batch jobs.",
                ],
                tag="Database Engines",
            ),
            RealWorldApplication(
                title="Stable Sorting of Complex Records & Linked Lists",
                description=(
                    "Merge Sort is naturally stable—it never alters the relative order of elements with equal keys. "
                    "This is essential in e-commerce when sorting products by 'Price' without scrambling a prior 'Customer Rating' sort."
                ),
                contexts=[
                    "E-commerce multi-column table sorting.",
                    "Linked list sorting in O(n log n) time without requiring random-access array indexing.",
                ],
                tag="Web & Application Systems",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why is Merge Sort chosen for external sorting of multi-gigabyte files that do not fit in RAM?",
                options=[
                    "It has an O(n) worst-case time complexity",
                    "It reads and writes large continuous streams sequentially, maximizing hard disk and SSD sequential transfer speeds",
                    "It requires zero temporary storage space",
                    "It only works on magnetic tapes",
                ],
                correct_index=1,
                explanation="Disks and SSDs read sequential blocks far faster than random seeks. Merge Sort reads and merges sequential streams from disk files with minimal seek latency.",
            ),
            QuizQuestion(
                question="What is the worst-case and average-case time complexity of standard Merge Sort?",
                options=[
                    "O(n) worst-case, O(n log n) average-case",
                    "O(n log n) in all cases (worst, average, and best)",
                    "O(n²) worst-case, O(n log n) average-case",
                    "O(log n) in all cases",
                ],
                correct_index=1,
                explanation="Merge Sort recursively divides the list into halves (log n levels) and performs linear-time merging (O(n)) at each level, guaranteeing O(n log n) comparisons in all cases.",
            ),
            QuizQuestion(
                question="What is the auxiliary space complexity required by standard array-based Merge Sort?",
                options=[
                    "O(1) in-place memory",
                    "O(n) auxiliary space for temporary merge buffers",
                    "O(n²) memory",
                    "O(log n) total space",
                ],
                correct_index=1,
                explanation="Standard array merging requires an auxiliary array of size n to store merged elements before copying them back to the original array, giving O(n) auxiliary space complexity.",
            ),
        ],
    ),

    "quick_sort": TopicPracticalData(
        topic_key="quick_sort",
        display_name="Quick Sort",
        category="Sorting Algorithms",
        summary="Selects a 'pivot' element and partitions array into elements smaller than pivot and elements greater, sorting recursively.",
        practical_example=PracticalExample(
            scenario="Organizing Books by Surname Using a Reference Letter",
            description=(
                "A librarian organizing a pile of books picks one book starting with 'M' as the pivot. All books starting with A–L "
                "are placed in one pile on the left, and N–Z on the right. The 'M' book is now in its exact final resting place, "
                "and the two smaller piles are independently organized the same way."
            ),
            visualization_connection=(
                "ProofMotion visually marks the pivot bar with a distinct highlight. Partition scanning pointers (i, j) swap "
                "elements across the pivot, placing the pivot into its permanent position before recursing on sub-partitions."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Systems Programming & C/C++ Standard Libraries",
                description=(
                    "The C standard library function `qsort()` and C++ `std::sort` (Introsort) use QuickSort as their core engine "
                    "due to exceptional in-place memory cache locality and low overhead."
                ),
                contexts=[
                    "Operating system kernel process and thread priority tables.",
                    "V8 JavaScript engine array sorting algorithms.",
                    "Game engine geometry depth sorting for transparency rendering.",
                ],
                tag="Systems Architecture",
            ),
            RealWorldApplication(
                title="Order-Statistic Selection (Quickselect)",
                description=(
                    "QuickSort's partitioning logic is adapted into Quickselect (Hoare's selection algorithm) to find the median "
                    "or the k-th smallest element in an unsorted array in guaranteed O(n) average time."
                ),
                contexts=[
                    "Real-time median filtering in digital signal and audio processing.",
                    "Percentile calculation (e.g. p95 and p99 latency metrics) in cloud observability platforms.",
                ],
                tag="Data Science & Observability",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why is QuickSort typically faster in practice than MergeSort for in-memory integer sorting?",
                options=[
                    "QuickSort has an O(log n) worst-case time complexity",
                    "QuickSort sorts in-place with excellent CPU cache locality, avoiding the auxiliary array allocations of MergeSort",
                    "QuickSort does not perform any comparisons",
                    "QuickSort runs exclusively on GPU tensor cores",
                ],
                correct_index=1,
                explanation="Because QuickSort operates in-place without allocating temporary buffers, memory references stay tight inside CPU L1/L2 caches, resulting in lower constant factors.",
            ),
            QuizQuestion(
                question="Under what condition does a naive QuickSort (always picking the first or last element as pivot) degrade to O(n²) time?",
                options=[
                    "When the array contains distinct random numbers",
                    "When the array is already sorted or reverse-sorted, causing completely unbalanced partitions",
                    "When the array size is a power of 2",
                    "When run on a 64-bit operating system",
                ],
                correct_index=1,
                explanation="If the pivot consistently splits the array into sizes 0 and n - 1, the recursion depth becomes n rather than log n, resulting in n passes of O(n) work (O(n²) total time).",
            ),
            QuizQuestion(
                question="What common strategy do production implementations (e.g. Introsort) use to prevent QuickSort worst-case degradation?",
                options=[
                    "Median-of-three pivot selection and falling back to Heapsort if recursion depth exceeds 2 log n",
                    "Always replacing the array with a linked list",
                    "Padding the array with zeroes",
                    "Using linear search instead of partitioning",
                ],
                correct_index=0,
                explanation="Median-of-three avoids bad pivots on sorted data, and introspective switching to Heapsort guarantees O(n log n) worst-case time complexity.",
            ),
        ],
    ),

    # ------------------------------------------------------------------
    # 3. SEARCHING ALGORITHMS
    # ------------------------------------------------------------------
    "linear_search": TopicPracticalData(
        topic_key="linear_search",
        display_name="Linear Search",
        category="Searching Algorithms",
        summary="Sequentially checks each element of the collection in order until a match is found or the list ends.",
        practical_example=PracticalExample(
            scenario="Scanning an Unsorted Receipt Folder for a Specific Store",
            description=(
                "When looking for a grocery receipt in an unsorted shoebox of household bills, you have no choice but to examine "
                "each receipt one by one from front to back until you find the supermarket logo or reach the bottom."
            ),
            visualization_connection=(
                "ProofMotion displays an active search head advancing one item at a time, highlighting visited non-matching items "
                "in slate and the matched target in vivid green."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Short Unsorted Arrays & Cache-Line Scans",
                description=(
                    "For collections of 8 to 16 elements, Linear Search is faster than Binary Search because it avoids branch mispredictions "
                    "and reads contiguous CPU cache lines sequentially via SIMD vector instructions."
                ),
                contexts=[
                    "Hash table collision bucket resolution in separate chaining.",
                    "HTTP header lookups in low-latency reverse proxies (Nginx, Envoy).",
                    "Small hardware register configuration bitfield validation.",
                ],
                tag="Computer Architecture",
            ),
            RealWorldApplication(
                title="Sequential Sensor & Streaming Log Ingestion",
                description=(
                    "When scanning incoming network packets or raw log files where data cannot be pre-indexed or sorted, "
                    "linear scanning identifies anomalies, delimiters, and target tokens on the fly."
                ),
                contexts=[
                    "Network intrusion detection systems (Snort, Suricata) packet pattern scanning.",
                    "Log monitoring systems filtering for 'FATAL' error markers in unstructured text.",
                ],
                tag="Cybersecurity & Telemetry",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="When is Linear Search preferred over sorting the data and using Binary Search?",
                options=[
                    "When the dataset has 10 million elements",
                    "When an unsorted list is searched only once or twice, making the O(n log n) sorting cost not worth paying",
                    "When we require O(1) guaranteed lookup time",
                    "When the data is stored in a balanced binary search tree",
                ],
                correct_index=1,
                explanation="Sorting takes O(n log n). If you only search once, an O(n) linear scan is far faster than the upfront cost of sorting.",
            ),
            QuizQuestion(
                question="What is the worst-case and average-case number of comparisons for Linear Search on an array of n items?",
                options=[
                    "O(log n) comparisons",
                    "n comparisons in the worst case, and approximately n/2 comparisons on average",
                    "1 comparison in all cases",
                    "n² comparisons",
                ],
                correct_index=1,
                explanation="If the target is at the final index or absent, Linear Search tests all n elements. For random uniform distribution, it searches an average of (n + 1)/2 elements.",
            ),
            QuizQuestion(
                question="What is the auxiliary space complexity of standard iterative Linear Search?",
                options=[
                    "O(1) auxiliary space",
                    "O(n) space",
                    "O(log n) stack space",
                    "O(n²) space",
                ],
                correct_index=0,
                explanation="Iterative linear search requires only a single loop index pointer, operating strictly in-place with O(1) auxiliary memory.",
            ),
        ],
    ),

    "binary_search": TopicPracticalData(
        topic_key="binary_search",
        display_name="Binary Search",
        category="Searching Algorithms",
        summary="Finds a target in a sorted collection by repeatedly comparing with the middle element and halving the search interval.",
        practical_example=PracticalExample(
            scenario="Looking Up a Word in a Printed Dictionary",
            description=(
                "When looking for the word 'Motion' in a 1,000-page dictionary, you open to the exact middle. Seeing 'Luggage', "
                "you immediately discard the first 500 pages and open to the middle of the second half. Repeating this halves the remaining pages every time."
            ),
            visualization_connection=(
                "ProofMotion maintains 'low', 'mid', and 'high' boundary markers. At each step, the inactive half of the array "
                "is visually dimmed out, illustrating logarithmic O(log n) reduction."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Database B-Tree Index Navigation",
                description=(
                    "Relational databases (MySQL InnoDB, PostgreSQL, Oracle) organize billions of rows into B-Tree index pages. "
                    "Locating the target key within each 16 KB index page is performed using binary search in microsecond time."
                ),
                contexts=[
                    "Primary key user lookups (SELECT * FROM users WHERE id = 48291).",
                    "Range queries checking start and end timestamps in financial transactions.",
                    "Key-value stores (RocksDB, LevelDB) SSTable block indexing.",
                ],
                tag="Database Systems",
            ),
            RealWorldApplication(
                title="Git Bisect Regression Debugging",
                description=(
                    "Software engineers track down bugs introduced in large codebases using `git bisect`. "
                    "It binary searches commit histories across thousands of commits to find the exact breaking change in only ~10 test runs."
                ),
                contexts=[
                    "Locating regression bugs across 10,000 git commits in ~14 test builds.",
                    "Automated CI/CD performance degradation culprit identification.",
                ],
                tag="Software Engineering Tools",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="If a database table has 1,048,576 (2²⁰) sorted customer IDs, what is the maximum number of comparisons Binary Search requires?",
                options=[
                    "1,048,576 comparisons",
                    "524,288 comparisons",
                    "Only 20 comparisons (log₂(2²⁰) = 20)",
                    "1,024 comparisons",
                ],
                correct_index=2,
                explanation="Because Binary Search divides the search space in half at each step, searching 2²⁰ elements takes at most 20 comparisons.",
            ),
            QuizQuestion(
                question="What essential prerequisite must an array satisfy before Binary Search can be applied?",
                options=[
                    "The array elements must all be positive numbers",
                    "The array must be strictly sorted in monotonic order",
                    "The array must have an odd number of elements",
                    "The array must be stored on a solid-state disk",
                ],
                correct_index=1,
                explanation="Binary Search relies on sorted order to discard half of the remaining search space after each comparison. On unsorted data, discarding a half could miss the target.",
            ),
            QuizQuestion(
                question="In languages with fixed-size 32-bit integers, why is mid = low + (high - low) // 2 preferred over mid = (low + high) // 2?",
                options=[
                    "It calculates the result faster on GPUs",
                    "It prevents arithmetic integer overflow when (low + high) exceeds 2³¹ - 1",
                    "It works on negative array indices",
                    "It rounds down to floating-point infinity",
                ],
                correct_index=1,
                explanation="If low and high are large positive integers, their sum can exceed 2³¹ - 1 and overflow into a negative integer, causing an invalid index exception. The subtraction form is numerically safe.",
            ),
        ],
    ),

    # ------------------------------------------------------------------
    # 4. GRAPH ALGORITHMS
    # ------------------------------------------------------------------
    "prim_mst": TopicPracticalData(
        topic_key="prim_mst",
        display_name="Prim's MST Algorithm",
        category="Graph Algorithms",
        summary="Grows a Minimum Spanning Tree from an arbitrary root vertex, greedily adding the cheapest edge connecting tree to non-tree vertices.",
        practical_example=PracticalExample(
            scenario="Laying Campus Fiber-Optic Cables Between Buildings",
            description=(
                "A university wants to connect 10 campus buildings with high-speed fiber internet. Digging trenches costs money per meter. "
                "Starting from the central data center, engineers repeatedly connect whichever nearby building requires the shortest trench, "
                "guaranteeing full campus connectivity at minimum total infrastructure expense."
            ),
            visualization_connection=(
                "ProofMotion displays the growing MST vertex cut with purple vertex badges, highlighting candidate boundary edges "
                "and greedily locking in the minimum weight edge at each step."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Telecommunications & Electrical Grid Distribution",
                description=(
                    "Power transmission companies plan high-voltage electrical grid layouts connecting substations. "
                    "Prim's algorithm computes the minimum total copper/aluminum cabling required with zero redundant closed loops."
                ),
                contexts=[
                    "Regional power distribution grid interconnects.",
                    "Municipal water supply pipeline networks.",
                    "Very Large Scale Integration (VLSI) chip clock-tree routing.",
                ],
                tag="Civil & Electrical Infrastructure",
            ),
            RealWorldApplication(
                title="Machine Learning Spectral Clustering & Image Segmentation",
                description=(
                    "In computer vision, image pixels or data clusters are treated as nodes in a graph with edge weights representing color/feature similarity. "
                    "Cutting high-weight edges in an MST segments an image into distinct foreground objects."
                ),
                contexts=[
                    "Medical MRI scan tissue boundary segmentation.",
                    "Autonomous vehicle road lane and obstacle clustering.",
                ],
                tag="Computer Vision & AI",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What topological guarantee does a Minimum Spanning Tree (MST) provide for a network of V vertices?",
                options=[
                    "It creates a fully-connected mesh with V·(V-1)/2 edges",
                    "It connects all V vertices using exactly V - 1 edges with the minimum possible total weight and zero cycles",
                    "It calculates the fastest route between every pair of nodes",
                    "It guarantees that every vertex has an even degree",
                ],
                correct_index=1,
                explanation="An MST on V vertices always consists of exactly V - 1 edges, forms no cycles, and minimizes the sum of all edge weights.",
            ),
            QuizQuestion(
                question="How does Prim's algorithm grow the Minimum Spanning Tree from an initial seed vertex?",
                options=[
                    "By sorting all edges globally and adding them if they do not create a cycle",
                    "By continuously selecting the minimum-weight edge connecting any vertex already in the tree to a vertex outside the tree",
                    "By repeatedly removing the maximum-weight edge from cycles",
                    "By executing breadth-first search from the vertex with highest degree",
                ],
                correct_index=1,
                explanation="Prim's algorithm maintains a single connected tree component, greedily expanding it at each step with the lightest cut-edge crossing the boundary between visited and unvisited vertices.",
            ),
            QuizQuestion(
                question="For a connected, undirected graph with V vertices and E edges, how many edges does the resulting Minimum Spanning Tree contain?",
                options=[
                    "V edges",
                    "V - 1 edges",
                    "E / 2 edges",
                    "V(V - 1) / 2 edges",
                ],
                correct_index=1,
                explanation="A tree spanning V vertices without cycles must contain exactly V - 1 edges. Fewer edges would leave the graph disconnected; more edges would introduce a cycle.",
            ),
        ],
    ),

    "kruskal_mst": TopicPracticalData(
        topic_key="kruskal_mst",
        display_name="Kruskal's MST Algorithm",
        category="Graph Algorithms",
        summary="Greedily adds edges in global ascending weight order across the entire graph, using Union-Find to prevent cycles.",
        practical_example=PracticalExample(
            scenario="Connecting Island Archipelago Communities with Bridges",
            description=(
                "A regional government connects an island archipelago with undersea cables. They sort all potential bridges by cost. "
                "They build the cheapest bridge first, then the next cheapest, skipping any proposed bridge that connects two islands "
                "already joined by existing connections."
            ),
            visualization_connection=(
                "ProofMotion displays the global sorted edge queue. When an edge is evaluated, Disjoint Set Union (DSU) checks "
                "whether both endpoints belong to the same component, rejecting cycle-forming edges with a red warning."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Ethernet Network Spanning Tree Protocol (STP / IEEE 802.1D)",
                description=(
                    "Corporate office computer networks have redundant network cables to survive hardware failure. "
                    "Ethernet switches run the Spanning Tree Protocol to automatically disable redundant loop connections, preventing catastrophic broadcast storms."
                ),
                contexts=[
                    "Enterprise Cisco and Juniper network switch configuration.",
                    "Data center leaf-spine topology management.",
                    "Wireless ad-hoc mesh routing protocols.",
                ],
                tag="Computer Networking",
            ),
            RealWorldApplication(
                title="Bioinformatics Phylogenetic Tree Construction",
                description=(
                    "Geneticists reconstruct evolutionary trees connecting biological species based on DNA sequence similarity matrices. "
                    "Kruskal's algorithm clusters the most closely related organisms first."
                ),
                contexts=[
                    "Viral lineage tracking (e.g. influenza and coronavirus variant mutation maps).",
                    "Species taxonomy evolutionary classification.",
                ],
                tag="Bioinformatics & Genomics",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What data structure enables Kruskal's algorithm to check whether an edge forms a cycle in nearly O(1) time?",
                options=[
                    "Priority Queue",
                    "Disjoint Set Union (Union-Find) with path compression and union-by-rank",
                    "Hash Map",
                    "Adjacency Matrix",
                ],
                correct_index=1,
                explanation="The Disjoint Set Union (DSU) data structure with path compression answers 'find' and 'union' queries in O(α(V)) nearly constant time.",
            ),
            QuizQuestion(
                question="In what initial order does Kruskal's algorithm process the edges of a graph?",
                options=[
                    "In non-decreasing order of edge weight (from smallest to largest)",
                    "In reverse topological order",
                    "In order of vertex degree",
                    "Randomly until V - 1 edges are picked",
                ],
                correct_index=0,
                explanation="Kruskal's algorithm begins by sorting all edges by weight in ascending order, ensuring that lighter edges are always considered before heavier edges.",
            ),
            QuizQuestion(
                question="If an edge (u, v) is considered by Kruskal's algorithm and find(u) == find(v), what action is taken?",
                options=[
                    "The edge is added to the MST",
                    "The edge is discarded because adding it would create a cycle within the existing component",
                    "The algorithm terminates immediately",
                    "The edge weight is doubled",
                ],
                correct_index=1,
                explanation="If find(u) == find(v), vertices u and v already belong to the same connected component. Adding the edge would create a redundant cycle, so it is safely discarded.",
            ),
        ],
    ),

    # ------------------------------------------------------------------
    # 5. TREE ALGORITHMS
    # ------------------------------------------------------------------
    "bst_intro": TopicPracticalData(
        topic_key="bst_intro",
        display_name="Binary Search Tree Fundamentals",
        category="Tree Data Structures",
        summary="Hierarchical data structure where each node satisfies the BST invariant: Left < Node < Right.",
        practical_example=PracticalExample(
            scenario="Student Directory Database Sorted by ID",
            description=(
                "An administration system stores enrolled students by roll number. Using a BST, searching for student #42 takes just "
                "a few branch decisions (Left or Right) rather than scanning through thousands of student records one by one."
            ),
            visualization_connection=(
                "ProofMotion renders the 2D tree hierarchy with animated node highlights, demonstrating how branches divide the key space."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Compiler Symbol Tables & Scope Management",
                description=(
                    "Programming language compilers (GCC, Clang) track declared variables, functions, and data types "
                    "within lexical scopes using balanced tree structures for rapid identifier resolution."
                ),
                contexts=[
                    "Resolving variable names during syntax parsing.",
                    "Type checker validation of method signatures.",
                ],
                tag="Compilers & Runtimes",
            ),
            RealWorldApplication(
                title="In-Memory Associative Containers (std::map, TreeMap)",
                description=(
                    "Standard libraries in C++ (`std::map`, `std::set`) and Java (`TreeMap`, `TreeSet`) implement sorted associative "
                    "containers using self-balancing BST variants (Red-Black trees) providing guaranteed O(log n) operations."
                ),
                contexts=[
                    "Maintaining ordered price lists in e-commerce applications.",
                    "Routing tables in operating system networking stacks.",
                ],
                tag="Standard Libraries",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What invariant must every node X in a Binary Search Tree satisfy?",
                options=[
                    "The tree must have an even number of leaves",
                    "All keys in X's left subtree must be smaller than X, and all keys in X's right subtree must be greater than X",
                    "All leaf nodes must be at the same depth",
                    "The root key must equal the total number of nodes",
                ],
                correct_index=1,
                explanation="The defining BST property is that for every node, every value in its left subtree is strictly less, and every value in its right subtree is strictly greater.",
            ),
            QuizQuestion(
                question="What traversal sequence on a Binary Search Tree outputs its keys in strictly ascending sorted order?",
                options=[
                    "Pre-order traversal (Root-Left-Right)",
                    "In-order traversal (Left-Root-Right)",
                    "Post-order traversal (Left-Right-Root)",
                    "Level-order traversal (Breadth-First)",
                ],
                correct_index=1,
                explanation="Because all keys in the left subtree are smaller than the node, and all keys in the right subtree are greater, in-order traversal (Left, then Node, then Right) yields strictly ascending order.",
            ),
            QuizQuestion(
                question="In the worst-case scenario (e.g. inserting already-sorted keys into an unconstrained BST), what is the shape and search complexity of the tree?",
                options=[
                    "A complete binary tree with O(log n) search time",
                    "A degenerate linear chain (like a linked list) with O(n) search time",
                    "A balanced B-tree with O(1) search time",
                    "A cyclic graph",
                ],
                correct_index=1,
                explanation="When keys arrive in sorted order, every new node is inserted as the right child of its predecessor, collapsing the tree into a linked list of height n with O(n) worst-case search complexity.",
            ),
        ],
    ),

    "bst_insert": TopicPracticalData(
        topic_key="bst_insert",
        display_name="BST Insertion",
        category="Tree Data Structures",
        summary="Navigates from root following BST ordering rules and attaches the new element at the appropriate leaf position.",
        practical_example=PracticalExample(
            scenario="Adding a New Contact to an Alphabetical Phone Directory",
            description=(
                "When adding a new contact 'Miller', the system compares it against the root 'Harris' (goes right), then 'Parker' (goes left), "
                "and slots 'Miller' neatly into the open spot between them."
            ),
            visualization_connection=(
                "ProofMotion traces the insertion path from the root downward with flashing navigation arrows, creating the new node at the destination."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Dynamic Database Index Record Insertions",
                description=(
                    "When users register new accounts or place orders, database engines dynamically insert new index keys "
                    "into B-Tree/BST index structures while preserving order without having to rebuild the entire index."
                ),
                contexts=[
                    "E-commerce user registrations and order logging.",
                    "Real-time sensor telemetry indexing in time-series databases.",
                ],
                tag="Database Engines",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="In an unbalanced Binary Search Tree, what is the worst-case time complexity of inserting n already-sorted numbers?",
                options=[
                    "O(1)",
                    "O(log n)",
                    "O(n) per insertion, leading to O(n²) total (the tree degenerates into a linear linked list)",
                    "O(n log n)",
                ],
                correct_index=2,
                explanation="Inserting already-sorted data into an unbalancing BST creates a skewed degenerate chain of nodes where each insertion takes O(n) steps.",
            ),
            QuizQuestion(
                question="Where does a newly inserted node always attach in a standard Binary Search Tree?",
                options=[
                    "As the new root node, pushing the old root down",
                    "As a leaf node attached to an existing parent whose appropriate child pointer was null",
                    "At the middle level of the tree",
                    "Replacing the node with the closest key value",
                ],
                correct_index=1,
                explanation="Standard BST insertion navigates from the root down comparing keys until finding a null child pointer at a leaf boundary, where the new node is attached.",
            ),
            QuizQuestion(
                question="What is the average time complexity to insert a key into a randomly generated BST with n nodes?",
                options=[
                    "O(1)",
                    "O(log n)",
                    "O(n)",
                    "O(n log n)",
                ],
                correct_index=1,
                explanation="With random insertions, the tree height averages O(log n). Finding the insertion leaf takes time proportional to height, resulting in O(log n) average time complexity.",
            ),
        ],
    ),

    "bst_search": TopicPracticalData(
        topic_key="bst_search",
        display_name="BST Search",
        category="Tree Data Structures",
        summary="Searches for a key in O(h) time by comparing with current node and branching left or right.",
        practical_example=PracticalExample(
            scenario="Looking Up a Customer Account Balance by Account Number",
            description=(
                "Banking systems locate customer account #51280 by querying their account index tree, eliminating half the remaining candidate accounts at every branch."
            ),
            visualization_connection=(
                "ProofMotion highlights the active comparison at each node, turning the found target green or reporting absent keys."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="DNS Domain Name IP Resolution Caches",
                description=(
                    "DNS server resolvers cache domain-to-IP mappings in hierarchical tree structures to resolve URLs like 'google.com' in sub-millisecond time."
                ),
                contexts=[
                    "Internet Service Provider recursive DNS resolvers.",
                    "Operating system local hosts caching.",
                ],
                tag="Networking",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What is the average search time complexity in a balanced Binary Search Tree containing n keys?",
                options=[
                    "O(n)",
                    "O(log n)",
                    "O(n²)",
                    "O(1)",
                ],
                correct_index=1,
                explanation="In a balanced tree of n nodes, the height is approximately log₂(n), so searching requires at most O(log n) comparisons.",
            ),
            QuizQuestion(
                question="When searching for key K at current node X in a BST, which branch is taken if K < X.key?",
                options=[
                    "Search terminates immediately",
                    "Recursively search the left subtree",
                    "Recursively search the right subtree",
                    "Examine both subtrees in parallel",
                ],
                correct_index=1,
                explanation="By the BST property, all keys strictly smaller than X.key reside exclusively in X's left subtree. The right subtree can be completely pruned.",
            ),
            QuizQuestion(
                question="What is the best-case time complexity of searching in any Binary Search Tree?",
                options=[
                    "O(log n)",
                    "O(1) when the target key is located directly at the root node",
                    "O(n)",
                    "O(n²)",
                ],
                correct_index=1,
                explanation="If the search target matches the key stored at the root node, the algorithm terminates on the very first comparison in O(1) time.",
            ),
        ],
    ),

    "bst_delete": TopicPracticalData(
        topic_key="bst_delete",
        display_name="BST Deletion",
        category="Tree Data Structures",
        summary="Handles three cases: deleting a leaf, deleting a node with 1 child, and deleting a node with 2 children (inorder successor replacement).",
        practical_example=PracticalExample(
            scenario="Cancelling an Active Subscription in a Sorted Customer Roster",
            description=(
                "When an intermediate account node is removed, the system promotes the customer with the next closest ID (inorder successor) "
                "to take the empty seat so that tree ordering remains intact."
            ),
            visualization_connection=(
                "ProofMotion illustrates all three cases, highlighting the inorder successor extraction and splice operations when removing two-child nodes."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Task Scheduler Cancellation in Operating Systems",
                description=(
                    "The Linux Completely Fair Scheduler (CFS) uses Red-Black trees to track runnable tasks by virtual runtime. "
                    "When a task terminates or yields, its node is deleted from the execution tree."
                ),
                contexts=[
                    "Linux CFS kernel scheduler.",
                    "Real-time audio processing job queues.",
                ],
                tag="Operating Systems",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="When deleting a BST node that has two children, which node is typically promoted to replace it?",
                options=[
                    "The root of the entire tree",
                    "Its inorder successor (smallest node in its right subtree) or inorder predecessor",
                    "A random leaf node",
                    "Its parent node",
                ],
                correct_index=1,
                explanation="Replacing the node with its inorder successor (or predecessor) guarantees that all left descendants remain smaller and all right descendants remain larger.",
            ),
            QuizQuestion(
                question="How is a leaf node (a node with zero children) deleted from a Binary Search Tree?",
                options=[
                    "By swapping it with the root node",
                    "By simply setting its parent pointer to null and freeing its memory",
                    "By promoting its left sibling",
                    "By rebuilding the entire tree",
                ],
                correct_index=1,
                explanation="Because a leaf node has no subtrees attached to it, its removal has no dependencies. The parent's reference to it is simply set to null.",
            ),
            QuizQuestion(
                question="If a node to be deleted has exactly one child, how is the deletion performed?",
                options=[
                    "The node is replaced by its single child directly (bypassing the node)",
                    "The deletion is illegal in a BST",
                    "All descendant nodes must be recursively deleted",
                    "The node key is set to zero",
                ],
                correct_index=0,
                explanation="When a node has one child, the node's parent updates its child link to point directly to the deleted node's child, cleanly splicing the node out of the tree.",
            ),
        ],
    ),

    "tree_inorder": TopicPracticalData(
        topic_key="tree_inorder",
        display_name="Inorder Traversal (Left, Node, Right)",
        category="Tree Traversals",
        summary="Visits Left Subtree → Root Node → Right Subtree. In a BST, produces strictly sorted ascending order.",
        practical_example=PracticalExample(
            scenario="Generating an Alphabetical Grade Report from an Exam Tree",
            description=(
                "When a school needs to print an alphabetical roster of student rankings, traversing their student BST "
                "via Inorder automatically outputs every single student name in alphabetical order without sorting."
            ),
            visualization_connection=(
                "ProofMotion animates traversal visits in lockstep with an output tape, showing sorted numbers emerging one by one."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Flattening Database Indexes & Sorted Dumps",
                description=(
                    "Database backup tools (like `mysqldump` and `pg_dump`) stream sorted records to disk by executing an inorder traversal over index trees."
                ),
                contexts=[
                    "Database exports and range scans (BETWEEN val1 AND val2).",
                    "Evaluating arithmetic expressions represented as binary trees.",
                ],
                tag="Database & Query Engines",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What is the result of performing an Inorder traversal on a valid Binary Search Tree?",
                options=[
                    "The nodes are printed in reverse chronological insertion order",
                    "All keys are visited in strictly ascending sorted order",
                    "The leaves are visited before the root",
                    "The height of the tree is halved",
                ],
                correct_index=1,
                explanation="Because Left < Node < Right, visiting Left then Node then Right recursively outputs all keys in ascending order.",
            ),
            QuizQuestion(
                question="What is the exact sequence of steps in a recursive in-order traversal of subtree T?",
                options=[
                    "Visit Root, traverse Left subtree, traverse Right subtree",
                    "Traverse Left subtree, visit Root, traverse Right subtree",
                    "Traverse Left subtree, traverse Right subtree, visit Root",
                    "Visit Root, traverse Right subtree, traverse Left subtree",
                ],
                correct_index=1,
                explanation="In-order traversal recursively visits the Left subtree first, processes the Root node second, and recursively visits the Right subtree third (L-N-R).",
            ),
            QuizQuestion(
                question="What is the maximum auxiliary call stack depth of in-order traversal on a balanced binary tree of n nodes?",
                options=[
                    "O(1)",
                    "O(log n) proportional to tree height",
                    "O(n)",
                    "O(n log n)",
                ],
                correct_index=1,
                explanation="The recursive call stack depth is determined by the height of the tree. In a balanced tree of n nodes, the height is floor(log2(n)), requiring O(log n) auxiliary stack space.",
            ),
        ],
    ),

    "tree_preorder": TopicPracticalData(
        topic_key="tree_preorder",
        display_name="Preorder Traversal (Node, Left, Right)",
        category="Tree Traversals",
        summary="Visits Root Node → Left Subtree → Right Subtree. Widely used for copying, cloning, and serialization.",
        practical_example=PracticalExample(
            scenario="Cloning & Saving a File Directory Hierarchy",
            description=(
                "To save a document folder structure to disk, you must record the parent folder before creating the subfolders and files inside it."
            ),
            visualization_connection=(
                "ProofMotion illustrates the root-first visitation pattern, building the serialized linear sequence step by step."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Tree Serialization & Deep Copying in Compilers",
                description=(
                    "Compilers and game engines serialize Abstract Syntax Trees (ASTs) or scene graphs to disk using preorder traversal "
                    "so that reconstructor parsers can deserialize nodes top-down."
                ),
                contexts=[
                    "Scene graph serialization in Unity and Unreal Engine.",
                    "JSON/XML parser document serialization.",
                ],
                tag="Compilers & File Formats",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why is Preorder traversal ideal for serializing a tree structure to a file?",
                options=[
                    "It calculates leaf checksums first",
                    "The root is stored before its children, allowing the tree to be reconstructed identically upon deserialization",
                    "It encrypts the payload automatically",
                    "It avoids visiting right-hand subtrees",
                ],
                correct_index=1,
                explanation="Preorder stores parent nodes before their children, which allows reading files sequentially to reconstruct identical parent-child links.",
            ),
            QuizQuestion(
                question="What is the visit order of Pre-order traversal for any subtree?",
                options=[
                    "Root node first, then Left subtree, then Right subtree (N-L-R)",
                    "Left subtree first, then Root, then Right subtree",
                    "Left subtree first, then Right subtree, then Root",
                    "Right subtree first, then Root, then Left subtree",
                ],
                correct_index=0,
                explanation="Pre-order traversal visits the node itself before exploring its child branches, allowing parent nodes to be cloned, processed, or serialized before their children.",
            ),
            QuizQuestion(
                question="When parsing a prefix mathematical expression (Polish notation) represented as an expression tree, which traversal reconstructs the prefix string?",
                options=[
                    "In-order traversal",
                    "Pre-order traversal",
                    "Post-order traversal",
                    "Level-order traversal",
                ],
                correct_index=1,
                explanation="Pre-order traversal visits the operator root before its left and right operands, outputting expressions in prefix form such as `+ a b`.",
            ),
        ],
    ),

    "tree_postorder": TopicPracticalData(
        topic_key="tree_postorder",
        display_name="Postorder Traversal (Left, Right, Node)",
        category="Tree Traversals",
        summary="Visits Left Subtree → Right Subtree → Root Node. Essential for bottom-up computation and memory deallocation.",
        practical_example=PracticalExample(
            scenario="Calculating Folder Disk Usage in an Operating System",
            description=(
                "To find the total megabytes used by your 'Documents' folder, your operating system must first sum up all individual files "
                "in every subfolder before computing the final parent folder total size."
            ),
            visualization_connection=(
                "ProofMotion shows child nodes evaluated before their parent, illustrating bottom-up dependency resolution."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Memory Deallocation & Garbage Collection",
                description=(
                    "In C and C++, safely freeing a dynamically allocated tree requires deleting all child pointers before freeing the parent node memory."
                ),
                contexts=[
                    "Recursive tree destruction in C++ destructors.",
                    "Evaluating Reverse Polish Notation (RPN) mathematical expressions.",
                ],
                tag="Systems Programming",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why must an operating system delete a tree using Postorder traversal in manual-memory languages like C++?",
                options=[
                    "Deleting the root first would orphan children, causing memory leaks because child pointers would be lost",
                    "It is the only traversal that runs in O(n) time",
                    "It prevents stack overflow",
                    "It automatically rebalances the tree",
                ],
                correct_index=0,
                explanation="In postorder traversal, child nodes are freed before their parent, ensuring child pointers remain valid until their memory is safely reclaimed.",
            ),
            QuizQuestion(
                question="What is the step sequence for a Post-order tree walk?",
                options=[
                    "Traverse Left subtree, traverse Right subtree, then visit Root node (L-R-N)",
                    "Visit Root node, then Left subtree, then Right subtree",
                    "Traverse Left subtree, visit Root, then Right subtree",
                    "Traverse Right subtree, visit Root, then Left subtree",
                ],
                correct_index=0,
                explanation="Post-order traversal visits both child subtrees before processing the root node, ensuring bottom-up evaluation.",
            ),
            QuizQuestion(
                question="Why is post-order traversal used when evaluating syntax trees or calculating directory disk usage?",
                options=[
                    "Because parent results depend on already having the computed results of both child branches",
                    "Because it uses less memory than pre-order traversal",
                    "Because it visits the root node first",
                    "Because it avoids using recursion",
                ],
                correct_index=0,
                explanation="To calculate total directory size, an operating system must first sum the sizes of all files and subdirectories within a folder before finalizing the parent folder's total.",
            ),
        ],
    ),

    "tree_level_order": TopicPracticalData(
        topic_key="tree_level_order",
        display_name="Level Order Traversal (BFS)",
        category="Tree Traversals",
        summary="Breadth-First Search visiting nodes level by level from top to bottom, left to right using a FIFO queue.",
        practical_example=PracticalExample(
            scenario="Organizational Corporate Hierarchy Chart",
            description=(
                "Printing an employee directory starting with the CEO (Level 0), followed by all Vice Presidents (Level 1), "
                "then all Department Managers (Level 2), and finally staff members."
            ),
            visualization_connection=(
                "ProofMotion displays an interactive FIFO queue, showing nodes enqueued horizontally level by level."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Web Browser DOM Layout & Web Crawling",
                description=(
                    "Web browser rendering engines (Chromium Blink, WebKit) calculate CSS layouts and render HTML elements "
                    "level by level to construct parent containers before painting inner child elements."
                ),
                contexts=[
                    "Browser DOM tree box-model layout computation.",
                    "Search engine web crawlers (Googlebot) crawling web link graphs breadth-first.",
                ],
                tag="Web Engines & Crawlers",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Which data structure is required to implement a Level Order (Breadth-First) traversal of a tree?",
                options=[
                    "Stack (LIFO)",
                    "Queue (FIFO)",
                    "Binary Heap",
                    "Hash Set",
                ],
                correct_index=1,
                explanation="A First-In-First-Out (FIFO) queue guarantees that all child nodes at depth d are enqueued and processed before any nodes at depth d + 1.",
            ),
            QuizQuestion(
                question="In what sequence does level-order traversal visit nodes in a binary tree?",
                options=[
                    "Bottom-to-top from deepest leaf to root",
                    "Level-by-level from top to bottom, visiting nodes left-to-right on each horizontal level",
                    "Along the leftmost spine first",
                    "According to ascending key values",
                ],
                correct_index=1,
                explanation="Level-order traversal processes all nodes at depth d before advancing to any node at depth d + 1, exploring the tree uniformly in horizontal breadth.",
            ),
            QuizQuestion(
                question="In a complete binary tree with n nodes, what is the maximum number of nodes stored simultaneously in the BFS queue?",
                options=[
                    "1 node",
                    "Approximately n / 2 nodes (the maximum width at the leaf level)",
                    "log n nodes",
                    "n² nodes",
                ],
                correct_index=1,
                explanation="In a complete binary tree, the lowest level contains roughly half (ceil(n/2)) of all nodes in the tree, requiring O(n) memory in the queue at peak width.",
            ),
        ],
    ),

    # ------------------------------------------------------------------
    # 6. 2D TRANSFORMATIONS
    # ------------------------------------------------------------------
    "trans_translation": TopicPracticalData(
        topic_key="trans_translation",
        display_name="2D Translation",
        category="2D Transformations",
        summary="Moves every point of a shape by a constant offset vector (dx, dy) without changing its shape or orientation.",
        practical_example=PracticalExample(
            scenario="Moving a Character Across a Video Game Screen",
            description=(
                "When a player presses the 'D' key in a 2D platformer game like Mario, the game engine translates the character's "
                "sprite position: x_new = x_old + dx. Every pixel of the character moves identically."
            ),
            visualization_connection=(
                "ProofMotion shows the original geometry with a dashed silhouette, animating displacement vectors along the X and Y axes."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Camera Panning & Viewport Scrolling in Apps",
                description=(
                    "Design software (Figma, Adobe Photoshop) and map apps (Google Maps) translate the entire rendered canvas "
                    "when you drag to pan, applying offset matrices to every vector path."
                ),
                contexts=[
                    "Figma vector canvas smooth panning.",
                    "Mobile touch swipe gesture coordinate tracking.",
                ],
                tag="User Interface Engines",
            ),
            RealWorldApplication(
                title="Homogeneous Coordinates in GPU Pipelines",
                description=(
                    "Using 3×3 homogeneous coordinate matrices allows translation to be represented as matrix multiplication "
                    "rather than vector addition, enabling hardware GPU matrix pipelines to chain Translation, Rotation, and Scaling."
                ),
                contexts=[
                    "DirectX, Vulkan, Metal transformation pipelines.",
                    "Robotic manipulator Cartesian arm positioning.",
                ],
                tag="Computer Graphics Architecture",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why do computer graphics systems use 3×3 homogeneous matrices for 2D transformations instead of 2×2 matrices?",
                options=[
                    "2×2 matrices cannot represent translation as matrix multiplication; 3×3 matrices unify translation, rotation, and scaling",
                    "3×3 matrices use less GPU memory",
                    "2×2 matrices cannot rotate objects",
                    "Homogeneous coordinates prevent colors from clipping",
                ],
                correct_index=0,
                explanation="In 2×2 matrices, translation is vector addition (v + t). Homogeneous 3×3 coordinates convert translation into matrix multiplication, allowing complex transformation sequences to be pre-multiplied into a single composite matrix.",
            ),
            QuizQuestion(
                question="If a 2D point (x, y) is translated by displacement vector (dx, dy), what are its new coordinates (x', y')?",
                options=[
                    "x' = x · dx, y' = y · dy",
                    "x' = x + dx, y' = y + dy",
                    "x' = x - dy, y' = y + dx",
                    "x' = x / dx, y' = y / dy",
                ],
                correct_index=1,
                explanation="Translation adds the displacement components directly to the point coordinates: x' = x + dx and y' = y + dy.",
            ),
            QuizQuestion(
                question="What type of transformation is 2D translation classified as in geometry?",
                options=[
                    "Non-linear perspective projection",
                    "Rigid body isometry (preserves all distances, angles, areas, and orientation)",
                    "Shear transformation",
                    "Scale transformation",
                ],
                correct_index=1,
                explanation="Translation is a rigid body isometry: shifting an object through space changes only its position, keeping shape, edge lengths, internal angles, and surface area completely unchanged.",
            ),
        ],
    ),

    "trans_scaling": TopicPracticalData(
        topic_key="trans_scaling",
        display_name="2D Scaling",
        category="2D Transformations",
        summary="Expands or contracts an object by scale factors (sx, sy) relative to the origin or a fixed pivot.",
        practical_example=PracticalExample(
            scenario="Pinch-to-Zoom on Smartphone Photos",
            description=(
                "When zooming in on a digital photo with two fingers, the touch processor calculates the distance between fingers "
                "and applies uniform scaling: x' = sx · x and y' = sy · y."
            ),
            visualization_connection=(
                "ProofMotion displays the scale bounding box changing in real time, illustrating independent non-uniform (sx ≠ sy) and uniform scaling."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="High-DPI Retina Display Scaling in Operating Systems",
                description=(
                    "macOS, Windows, and Android automatically scale UI elements by 1.25×, 1.5×, or 2.0× on high-density displays "
                    "so text and icons remain crisp and legible at high physical pixel densities."
                ),
                contexts=[
                    "Retina / 4K display OS vector UI scaling.",
                    "SVG vector icon dynamic resolution scaling in web browsers.",
                ],
                tag="Operating Systems & UI",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="If a 2D rectangle is scaled by sx = 2.0 and sy = 3.0, by what factor does its surface area multiply?",
                options=[
                    "5× (2 + 3)",
                    "6× (2.0 × 3.0, the determinant of the scaling matrix)",
                    "1× (area does not change)",
                    "8×",
                ],
                correct_index=1,
                explanation="The determinant of a 2D scaling matrix is sx · sy. With factors of 2.0 and 3.0, the enclosed area scales by 2 × 3 = 6 times.",
            ),
            QuizQuestion(
                question="What visual effect occurs when a negative scale factor (e.g. sx = -1.0, sy = 1.0) is applied about the origin?",
                options=[
                    "The object disappears completely",
                    "The object is mirrored/reflected across the Y-axis",
                    "The object rotates 45 degrees clockwise",
                    "The object doubles in size",
                ],
                correct_index=1,
                explanation="Multiplying the x-coordinate by -1 inverts its sign while preserving magnitude, producing a geometric reflection across the vertical Y-axis.",
            ),
            QuizQuestion(
                question="What is the determinant of a 2D scaling matrix with diagonal factors sx and sy, and what does it indicate?",
                options=[
                    "det(S) = sx + sy, indicating perimeter expansion",
                    "det(S) = sx · sy, indicating the signed area scaling factor",
                    "det(S) = 1.0 always",
                    "det(S) = 0",
                ],
                correct_index=1,
                explanation="The determinant of the diagonal scaling matrix is sx · sy, which directly gives the ratio of the transformed polygon area to the original polygon area.",
            ),
        ],
    ),

    "trans_rotation": TopicPracticalData(
        topic_key="trans_rotation",
        display_name="2D Rotation",
        category="2D Transformations",
        summary="Rotates an object about the coordinate origin by an angle θ using trigonometric rotation matrices.",
        practical_example=PracticalExample(
            scenario="Aircraft Heading Indicator & Compass Dial",
            description=(
                "A cockpit flight display or radar screen continuously rotates the aircraft icon to match magnetic heading θ: "
                "x' = x·cos(θ) - y·sin(θ) and y' = x·sin(θ) + y·cos(θ)."
            ),
            visualization_connection=(
                "ProofMotion shows circular motion arcs and angular coordinates, proving that distances from the origin are preserved (isometry)."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Autonomous Vehicle LiDAR Point Cloud Alignment",
                description=(
                    "Self-driving cars rotate incoming 3D LiDAR point cloud scans based on vehicle inertial gyro sensors "
                    "to match new sensor frames with high-definition base maps."
                ),
                contexts=[
                    "Waymo / Tesla real-time odometry and localization.",
                    "Skeletal character animation bone joint rotations.",
                ],
                tag="Robotics & Autonomous Driving",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What trigonometric identity guarantees that 2D rotation is a rigid body transformation (preserving distances)?",
                options=[
                    "tan(θ) = sin(θ) / cos(θ)",
                    "cos²(θ) + sin²(θ) = 1 (the determinant of the rotation matrix is 1.0)",
                    "sin(2θ) = 2 sin(θ) cos(θ)",
                    "cos(0°) = 1",
                ],
                correct_index=1,
                explanation="The determinant of a 2D rotation matrix is cos²(θ) - (-sin²(θ)) = cos²(θ) + sin²(θ) = 1.0, meaning areas and lengths are strictly preserved.",
            ),
            QuizQuestion(
                question="What are the algebraic formulas for rotating a point (x, y) counterclockwise by angle θ about the origin?",
                options=[
                    "x' = x cos θ - y sin θ,  y' = x sin θ + y cos θ",
                    "x' = x cos θ + y sin θ,  y' = y cos θ - x sin θ",
                    "x' = x + cos θ,  y' = y + sin θ",
                    "x' = x tan θ,  y' = y cot θ",
                ],
                correct_index=0,
                explanation="Applying standard polar coordinate expansion yields x' = x cos θ - y sin θ and y' = x sin θ + y cos θ for counterclockwise rotation about the coordinate origin.",
            ),
            QuizQuestion(
                question="What is the determinant of any 2D pure rotation matrix R(θ)?",
                options=[
                    "0.0",
                    "+1.0",
                    "-1.0",
                    "tan(θ)",
                ],
                correct_index=1,
                explanation="det(R) = cos(θ)·cos(θ) - (-sin(θ)·sin(θ)) = cos²(θ) + sin²(θ) = 1.0. A determinant of +1 confirms that area and vertex winding orientation are strictly preserved.",
            ),
        ],
    ),

    "trans_pivot_rotation": TopicPracticalData(
        topic_key="trans_pivot_rotation",
        display_name="Rotation About an Arbitrary Pivot",
        category="2D Transformations",
        summary="Rotates geometry around a chosen pivot point (px, py) by translating to origin, rotating, and translating back.",
        practical_example=PracticalExample(
            scenario="Opening a Door Hinged at One Corner",
            description=(
                "A door does not rotate around the center of the house; it rotates around its corner hinge. In software, "
                "the hinge is the pivot point."
            ),
            visualization_connection=(
                "ProofMotion illustrates the three-stage sequence: T(-p) → R(θ) → T(+p), showing why pivot choice changes the orbital path."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="CAD Software & Architectural Drafting",
                description=(
                    "In AutoCAD and SolidWorks, mechanical parts are swung around axle shafts or mounting pin pivot coordinates."
                ),
                contexts=[
                    "Mechanical gear train and clockwork rotation.",
                    "Digital art canvas rotation around cursor position in Procreate/Photoshop.",
                ],
                tag="CAD & Design Tools",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What is the correct 3-step matrix sequence to rotate an object around arbitrary pivot (px, py)?",
                options=[
                    "Scale → Rotate → Shear",
                    "Translate by (-px, -py) to origin → Rotate by θ → Translate back by (+px, +py)",
                    "Rotate by θ → Translate by (px, py)",
                    "Translate by (px, py) → Rotate by θ",
                ],
                correct_index=1,
                explanation="Standard rotation operates about (0,0). Shifting pivot to origin, applying rotation, and shifting back produces correct local rotation.",
            ),
            QuizQuestion(
                question="Why is translating the pivot point to the origin required before applying the rotation matrix R(θ)?",
                options=[
                    "Because standard rotation matrices rotate coordinates specifically about the origin (0, 0)",
                    "Because matrix multiplication does not work for non-zero points",
                    "To convert coordinates into pixels",
                    "To invert the polygon winding",
                ],
                correct_index=0,
                explanation="Standard trigonometric rotation matrices R(θ) inherently rotate points around the coordinate origin (0, 0). Translating pivot (px, py) to the origin aligns the desired rotation center with the origin.",
            ),
            QuizQuestion(
                question="When using column-vector notation P' = M · P, in what order are the 3 transformation matrices concatenated: M = T(px, py) · R(θ) · T(-px, -py)?",
                options=[
                    "From left to right",
                    "From right to left (T(-px, -py) executes first on P, followed by R(θ), then T(px, py))",
                    "In arbitrary order since matrix multiplication is commutative",
                    "Simultaneously without order",
                ],
                correct_index=1,
                explanation="In column-vector convention P' = M · P, matrix transformations evaluate right-to-left: the point is first shifted by T(-px, -py), then rotated by R(θ), and finally returned by T(px, py).",
            ),
        ],
    ),

    "trans_reflection": TopicPracticalData(
        topic_key="trans_reflection",
        display_name="2D Reflection",
        category="2D Transformations",
        summary="Mirrors an object across an axis (X-axis, Y-axis, or origin), reversing coordinate signs and polygon winding order.",
        practical_example=PracticalExample(
            scenario="Mirroring Symmetrical Car Body Designs in CAD",
            description=(
                "Automotive designers model only the left half of a sports car body. A reflection transformation across the central axis "
                "instantly creates a perfectly symmetrical right half."
            ),
            visualization_connection=(
                "ProofMotion draws the mirror line of symmetry, flipping vertices and showing how clockwise winding flips to counter-clockwise."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Computer Vision Training Data Augmentation",
                description=(
                    "Training autonomous driving AI models requires millions of images. Horizontally reflecting images "
                    "doubles dataset size for training pedestrian and lane detection models without collecting new photos."
                ),
                contexts=[
                    "Convolutional Neural Network (CNN) data augmentation pipelines.",
                    "Real-time mirror and puddle reflections in 3D game shaders.",
                ],
                tag="Artificial Intelligence & Computer Vision",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What happens to the winding order (vertex orientation) of a polygon when reflected across the X-axis?",
                options=[
                    "It stays exactly the same",
                    "It reverses (clockwise becomes counter-clockwise), flipping polygon normal direction",
                    "All vertices become zero",
                    "The polygon becomes a circle",
                ],
                correct_index=1,
                explanation="Reflection has a negative determinant (-1), which inverts coordinate chirality and flips polygon face normal orientations in 3D rendering.",
            ),
            QuizQuestion(
                question="What transformation matrix reflects a 2D point (x, y) across the horizontal X-axis (y -> -y)?",
                options=[
                    "[[1, 0], [0, 1]]",
                    "[[1, 0], [0, -1]]",
                    "[[-1, 0], [0, 1]]",
                    "[[0, 1], [1, 0]]",
                ],
                correct_index=1,
                explanation="Reflecting across the X-axis leaves x unchanged (x' = x) while negating y (y' = -y), represented by the diagonal matrix with entries 1 and -1.",
            ),
            QuizQuestion(
                question="What is the determinant of any 2D reflection matrix, and what does its sign indicate?",
                options=[
                    "det = +1, indicating clockwise winding",
                    "det = -1, indicating orientation reversal (chirality change)",
                    "det = 0, indicating projection onto a line",
                    "det = π",
                ],
                correct_index=1,
                explanation="A negative determinant (-1) indicates that reflection reverses spatial orientation: counterclockwise polygon vertices become clockwise, requiring back-face culling flags to flip in 3D.",
            ),
        ],
    ),

    "trans_composite": TopicPracticalData(
        topic_key="trans_composite",
        display_name="Composite Transformations (T · R · S)",
        category="2D Transformations",
        summary="Concatenates multiple transformation matrices into a single composite matrix: M = T · R · S.",
        practical_example=PracticalExample(
            scenario="Rendering Video Game Props in World Space",
            description=(
                "A 3D tree asset modeled at (0,0) is scaled to 1.5× size, rotated 45° to look natural, and placed at world coordinates (120, 85). "
                "GPU pipelines multiply all three steps into one single transformation matrix."
            ),
            visualization_connection=(
                "ProofMotion demonstrates matrix non-commutativity: reordering transformations produces dramatically different visual results."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Scene Graphs in Game Engines (Unreal, Unity, Godot)",
                description=(
                    "Video games structure worlds as hierarchical scene graphs (e.g. Car → Steering Wheel → Hands). "
                    "Each child's final world transform is the composite matrix multiplication of all ancestor transforms."
                ),
                contexts=[
                    "Skeletal character animation bone transform hierarchies.",
                    "UI layout container transforms in web and native app toolkits.",
                ],
                tag="Game Engines & Scene Graphs",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Is matrix multiplication commutative in computer graphics (does T · R always equal R · T)?",
                options=[
                    "Yes, transformation order never affects the visual result",
                    "No, matrix multiplication is non-commutative; translating then rotating yields a different position than rotating then translating",
                    "Only on 64-bit operating systems",
                    "Only when scaling factors are equal",
                ],
                correct_index=1,
                explanation="Because matrix multiplication is non-commutative, translating before rotating swings the object in a wide orbit, whereas rotating before translating spins it in place.",
            ),
            QuizQuestion(
                question="Why is matrix concatenation computationally beneficial in 3D graphics rendering pipelines?",
                options=[
                    "It eliminates the need for vertex shaders",
                    "It combines multiple model, view, and projection transforms into a single 4×4 matrix, requiring only one matrix-vector multiplication per vertex",
                    "It compresses 3D meshes into 2D images",
                    "It converts floating point coordinates into integers",
                ],
                correct_index=1,
                explanation="Multiplying a sequence of transformation matrices together once produces a single composite matrix M. Transforming millions of vertices then requires only one matrix multiply M · v each.",
            ),
            QuizQuestion(
                question="What mathematical property allows multiple transformation matrices to be grouped as A · (B · C) = (A · B) · C?",
                options=[
                    "Commutativity",
                    "Associativity",
                    "Distributivity of vectors",
                    "Orthogonality",
                ],
                correct_index=1,
                explanation="Matrix multiplication is strictly associative: (A · B) · C = A · (B · C). This guarantees that transformation pipelines can pre-multiply matrices in any grouping order.",
            ),
        ],
    ),

    # ------------------------------------------------------------------
    # 7. RASTERIZATION
    # ------------------------------------------------------------------
    "rast_dda": TopicPracticalData(
        topic_key="rast_dda",
        display_name="DDA Line Algorithm",
        category="Rasterization",
        summary="Digital Differential Analyzer: steps along major axis by 1 and increments minor axis by slope m = Δy/Δx, rounding to pixels.",
        practical_example=PracticalExample(
            scenario="Plotting Telemetry on Low-Power Digital Displays",
            description=(
                "An embedded medical monitor plotting an ECG heart rhythm on a small LCD grid uses DDA to connect discrete sensor samples with smooth pixel lines."
            ),
            visualization_connection=(
                "ProofMotion displays the continuous mathematical line superimposed on the pixel grid, highlighting rounded raster coordinates at each step."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Voxel Raymarching in 3D Games (Minecraft-style engines)",
                description=(
                    "Voxel engines and atmospheric smoke simulators use fast 3D DDA algorithms (Amanatides-Woo algorithm) "
                    "to trace light rays through grid voxels to detect block collisions and shadows."
                ),
                contexts=[
                    "Volumetric smoke and fog light raymarching shaders.",
                    "Line-of-sight collision checking in tile-based games.",
                ],
                tag="Voxel Graphics & Raycasting",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What is the primary computational disadvantage of the classic DDA line algorithm on embedded hardware?",
                options=[
                    "It cannot render horizontal lines",
                    "It relies on floating-point arithmetic and explicit round() calls in every pixel step loop",
                    "It requires O(n²) memory",
                    "It only works on monochrome displays",
                ],
                correct_index=1,
                explanation="DDA calculates floating-point increments and calls round() on every step, which was historically slow on hardware lacking dedicated floating-point units (FPUs).",
            ),
            QuizQuestion(
                question="How does the Digital Differential Analyzer (DDA) choose its sampling axis?",
                options=[
                    "It always steps along the X-axis",
                    "It steps unit increments along whichever axis has the larger coordinate span (max(|Δx|, |Δy|))",
                    "It alternates between X and Y on every tick",
                    "It steps along the normal vector",
                ],
                correct_index=1,
                explanation="To ensure a continuous, gap-free line without duplicate pixel steps, DDA sets step_count = max(|Δx|, |Δy|) and increments the dominant axis by 1.0 unit per step.",
            ),
            QuizQuestion(
                question="For a line with |slope| m < 1, what is the exact coordinate increment along the Y-axis for each unit step in X?",
                options=[
                    "Δy = 1.0",
                    "Δy = m (the slope Δy / Δx)",
                    "Δy = 1 / m",
                    "Δy = 0",
                ],
                correct_index=1,
                explanation="Since x advances by 1.0 on each step, y increments by dy = m · dx = m · 1.0 = m.",
            ),
        ],
    ),

    "rast_bresenham": TopicPracticalData(
        topic_key="rast_bresenham",
        display_name="Bresenham's Line Algorithm",
        category="Rasterization",
        summary="Fast incremental rasterizer using pure integer arithmetic and a decision parameter d_k to select the closest pixel.",
        practical_example=PracticalExample(
            scenario="3D Printer Stepper Motor Control (G-Code Motion)",
            description=(
                "A 3D printer nozzle moving from (0,0) to (100, 35) mm must decide at every motor microstep whether to step only the X motor "
                "or step both X and Y motors together. Bresenham's integer decision variable controls the motors in real time."
            ),
            visualization_connection=(
                "ProofMotion shows the integer decision parameter d_k updating at each column: when d_k < 0 it chooses East, "
                "when d_k ≥ 0 it chooses North-East and adjusts d_k accordingly."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="GPU Silicon Hardware Rasterizers",
                description=(
                    "Dedicated fixed-function hardware units inside modern GPUs (NVIDIA, AMD, Apple Silicon) rasterize triangle edges "
                    "into fragment pixels using hardware-pipelined variants of Bresenham's integer logic."
                ),
                contexts=[
                    "Hardware fragment generator stages in GPU pipelines.",
                    "CNC milling machine and laser engraver pulse controllers.",
                ],
                tag="Hardware & GPU Architecture",
            ),
            RealWorldApplication(
                title="Roguelike Video Game 2D Line-of-Sight",
                description=(
                    "Grid-based games use Bresenham's line algorithm to trace visibility rays from the player to enemies to determine "
                    "if vision is obstructed by walls on the dungeon grid."
                ),
                contexts=[
                    "Fog-of-war calculations in strategy games.",
                    "Field-of-view algorithms in simulation engines.",
                ],
                tag="Game AI & Visibility",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why was Jack Bresenham's line algorithm such a major milestone in computer graphics history?",
                options=[
                    "It introduced color antialiasing",
                    "It eliminated floating-point division entirely, determining exact pixel steps using fast integer addition and bit shifts",
                    "It rendered 3D curves directly on CRT monitors",
                    "It allowed lines to be drawn backwards",
                ],
                correct_index=1,
                explanation="Bresenham formulated an incremental error term that relies exclusively on fast integer addition, subtraction, and sign bit checks, running at maximum speed on early hardware.",
            ),
            QuizQuestion(
                question="What is the initial decision parameter p0 in Bresenham's line algorithm for a line with Δx and Δy (0 < m < 1)?",
                options=[
                    "p0 = 2Δy - Δx",
                    "p0 = Δy - 2Δx",
                    "p0 = 0",
                    "p0 = Δx · Δy",
                ],
                correct_index=0,
                explanation="Evaluating the midpoint decision equation at the start pixel yields p0 = 2Δy - Δx. If p0 < 0, the midpoint lies above the line, so the lower pixel is closer.",
            ),
            QuizQuestion(
                question="If the current decision parameter p_k < 0 in Bresenham's algorithm, what pixel is plotted next and how does p update?",
                options=[
                    "Plot (x + 1, y), update p = p + 2Δy",
                    "Plot (x + 1, y + 1), update p = p + 2Δy - 2Δx",
                    "Plot (x, y + 1), update p = p - 2Δx",
                    "Stop line rasterization",
                ],
                correct_index=0,
                explanation="When p_k < 0, the candidate pixel East (x + 1, y) is closer to the true line. The y coordinate remains unchanged, and the decision parameter increments by 2Δy.",
            ),
        ],
    ),

    "rast_midpoint_circle": TopicPracticalData(
        topic_key="rast_midpoint_circle",
        display_name="Midpoint Circle Algorithm",
        category="Rasterization",
        summary="Exploits 8-way circle symmetry, computing pixels in a single 45° octant using integer decision variables and mirroring to all 8 octants.",
        practical_example=PracticalExample(
            scenario="Drawing Circular Avatar Frames in Vector UI Engines",
            description=(
                "When rendering a circular user profile badge or notification badge on screen, UI renderers use midpoint circle logic "
                "to calculate pixel boundaries with zero trigonometry."
            ),
            visualization_connection=(
                "ProofMotion calculates pixels in octant 1 and highlights the 8-way symmetric mirror reflections simultaneously across the canvas."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Marine Radar & Sonar Circular Range Rings",
                description=(
                    "Naval navigation systems and aviation air-traffic radar scopes render concentric distance rings across digital displays "
                    "using midpoint circle rasterization."
                ),
                contexts=[
                    "Air-traffic control primary surveillance radar sweeps.",
                    "Digital oscilloscope circular calibration dials.",
                ],
                tag="Avionics & Marine Systems",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="How does 8-fold symmetry benefit the Midpoint Circle algorithm?",
                options=[
                    "It renders 8 circles simultaneously",
                    "It computes pixels in only one 45° octant and mirrors them to the remaining 7 octants, cutting math by ~87%",
                    "It prevents circles from distorting into ellipses",
                    "It eliminates the need for a coordinate origin",
                ],
                correct_index=1,
                explanation="A circle is symmetric across 8 octants (±x, ±y) and (±y, ±x). Calculating one 45° arc allows plotting all 8 pixels immediately per step.",
            ),
            QuizQuestion(
                question="What is the initial value of the midpoint circle decision parameter p0 for radius r (using integer approximation)?",
                options=[
                    "p0 = 1 - r",
                    "p0 = r²",
                    "p0 = 2r",
                    "p0 = 0",
                ],
                correct_index=0,
                explanation="Evaluating the implicit circle function at the first midpoint (1, r - 0.5) gives f(1, r - 0.5) = 5/4 - r. Rounding 5/4 to 1 for integer arithmetic yields p0 = 1 - r.",
            ),
            QuizQuestion(
                question="If the decision parameter p_k < 0 in the midpoint circle algorithm, which candidate pixel is selected?",
                options=[
                    "Pixel East (x + 1, y)",
                    "Pixel South-East (x + 1, y - 1)",
                    "Pixel North (x, y + 1)",
                    "Pixel West (x - 1, y)",
                ],
                correct_index=0,
                explanation="When p_k < 0, the midpoint lies inside the circle perimeter, meaning the upper pixel East (x + 1, y) is closer to the true boundary.",
            ),
        ],
    ),

    "curve_bezier": TopicPracticalData(
        topic_key="curve_bezier",
        display_name="Bézier Curve Subdivision (De Casteljau)",
        category="Rasterization & Curves",
        summary="Evaluates and subdivides smooth parametric curves through recursive linear interpolation between control points.",
        practical_example=PracticalExample(
            scenario="Vector Pen Tool in Design Software (Figma / Illustrator)",
            description=(
                "When drawing logos or smooth typography in Figma, designers click and drag handles. The curve bends smoothly "
                "according to the positions of the four control points P₀, P₁, P₂, P₃."
            ),
            visualization_connection=(
                "ProofMotion draws the convex hull polygon, animates intermediate lerp line segments at parameter t, "
                "and displays recursive subdivision splits into flat pixel segments."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Digital Typography & Font Rendering Engines",
                description=(
                    "TrueType (.ttf) and OpenType (.otf) vector fonts define all letter glyphs (such as 'S' and 'g') as sequences "
                    "of quadratic and cubic Bézier curves. FreeType and OS font renderers rasterize these curves into sharp screen pixels."
                ),
                contexts=[
                    "Operating system font rasterization (FreeType, DirectWrite, CoreText).",
                    "SVG vector graphics path rendering in modern web browsers.",
                ],
                tag="Typography & Operating Systems",
            ),
            RealWorldApplication(
                title="Automotive Aerodynamic Body Styling & CAD",
                description=(
                    "Pierre Bézier developed these curves at Renault to design smooth aerodynamic automobile body panels. "
                    "Modern CAD software (CATIA, Autodesk Alias) uses them for Class-A surfacing."
                ),
                contexts=[
                    "Aerospace fuselage and wing cross-section design.",
                    "3D camera motion track splines in animation software (Blender, Maya).",
                ],
                tag="Industrial & Automotive CAD",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What fundamental operation does De Casteljau's algorithm recursively execute to evaluate a Bézier curve point?",
                options=[
                    "Matrix inversion",
                    "Repeated linear interpolation (lerp) between adjacent control points with parameter t ∈ [0, 1]",
                    "Fast Fourier Transform",
                    "Polygon line clipping",
                ],
                correct_index=1,
                explanation="De Casteljau's algorithm computes intermediate points by linear interpolation: P(t) = (1 - t)·A + t·B, repeating down to a single point on the curve.",
            ),
            QuizQuestion(
                question="What is the convex hull property of Bézier curves and why is it useful in CAD software?",
                options=[
                    "The curve is completely contained within the convex polygon formed by its control points, enabling rapid bounding-box collision tests",
                    "The curve always forms a closed circle",
                    "The curve has constant curvature throughout",
                    "The control points must lie on a single straight line",
                ],
                correct_index=0,
                explanation="Because Bernstein basis polynomials are non-negative and sum to 1, any point on the curve is a convex combination of control points, guaranteeing it never strays outside their convex hull.",
            ),
            QuizQuestion(
                question="For a cubic Bézier curve with control points P0, P1, P2, P3, what are its start and end tangent vectors?",
                options=[
                    "Tangent at start is 3(P1 - P0), and tangent at end is 3(P3 - P2)",
                    "Tangent is constant everywhere",
                    "Tangent at start is P3 - P0",
                    "Tangent is always perpendicular to P1",
                ],
                correct_index=0,
                explanation="Differentiating the cubic Bernstein polynomial yields B'(0) = 3(P1 - P0) and B'(1) = 3(P3 - P2), meaning curve direction at the endpoints is tangent to the outer control legs.",
            ),
        ],
    ),

    # ------------------------------------------------------------------
    # 8. CLIPPING ALGORITHMS
    # ------------------------------------------------------------------
    "clip_cohen_sutherland": TopicPracticalData(
        topic_key="clip_cohen_sutherland",
        display_name="Cohen-Sutherland Line Clipping",
        category="Clipping Algorithms",
        summary="Divides 2D space into 9 regions using 4-bit Outcodes (TBRL). Enables fast trivial accept/reject of lines against viewports.",
        practical_example=PracticalExample(
            scenario="Displaying a Digital Road Map on a Smartphone Viewport",
            description=(
                "A highway spans 500 kilometers across the country, but your phone screen only shows a 5 km window. "
                "Cohen-Sutherland calculates the exact screen boundary intersections, discarding off-screen road sections "
                "so the phone GPU doesn't waste battery drawing invisible geometry."
            ),
            visualization_connection=(
                "ProofMotion displays the 4-bit region outcodes (e.g. 1001 for Top-Left), marks trivial accept/reject states, "
                "and animates intersection clipping steps against window edges."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Viewport Culling in 2D & 3D Video Game Engines",
                description=(
                    "Game engines cull off-screen geometry before sending draw calls to the GPU. Lines and wireframes outside "
                    "the camera view frustum are trivially rejected in nanoseconds using bitwise outcode operations."
                ),
                contexts=[
                    "Unreal Engine and Unity 2D culling passes.",
                    "CAD viewport clipping in AutoCAD and Revit.",
                    "GUI window manager clipping of obscured desktop application windows.",
                ],
                tag="Game Engines & CAD",
            ),
            RealWorldApplication(
                title="Digital Mapping Tile Rendering (Google Maps, Mapbox)",
                description=(
                    "Vector map engines slice continental road and river vector networks into 256×256 pixel vector map tiles "
                    "using line clipping algorithms during map tile generation."
                ),
                contexts=[
                    "Web map vector tile generation (MVT format).",
                    "Flight simulator navigation display route line clipping.",
                ],
                tag="Geospatial & Web Mapping",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="How does Cohen-Sutherland trivially reject a line segment that lies entirely outside the viewing window?",
                options=[
                    "If Code1 + Code2 == 0",
                    "If (Code1 AND Code2) != 0 (both endpoints share an exterior boundary bit)",
                    "If Code1 == Code2",
                    "If the line slope is negative",
                ],
                correct_index=1,
                explanation="If the bitwise AND of both endpoint outcodes is non-zero, both endpoints share an exterior region (e.g., both are to the Left), meaning the entire line segment is guaranteed to be completely outside.",
            ),
            QuizQuestion(
                question="What outcode represents a point that is located inside the clipping window?",
                options=[
                    "0000",
                    "1111",
                    "1001",
                    "0001",
                ],
                correct_index=0,
                explanation="The outcode 0000 indicates that the point violates neither Top, Bottom, Right, nor Left boundaries, meaning it lies strictly inside the window.",
            ),
            QuizQuestion(
                question="Under what condition does Cohen-Sutherland trivially accept a line segment?",
                options=[
                    "When (Code1 OR Code2) == 0 (both endpoint outcodes are 0000)",
                    "When (Code1 AND Code2) == 0",
                    "When Code1 != Code2",
                    "When both endpoints have negative coordinates",
                ],
                correct_index=0,
                explanation="If Code1 | Code2 == 0000, neither endpoint violates any boundary, proving that the entire line segment lies completely inside the clipping rectangle without computing intersections.",
            ),
        ],
    ),

    "clip_sutherland_hodgman": TopicPracticalData(
        topic_key="clip_sutherland_hodgman",
        display_name="Sutherland-Hodgman Polygon Clipping",
        category="Clipping Algorithms",
        summary="Clips a general polygon against convex clipping boundaries one edge at a time, outputting a new clipped polygon vertex list.",
        practical_example=PracticalExample(
            scenario="Cookie-Cutter Floorplan Clipping in Architectural CAD",
            description=(
                "An architect draws a large irregularly-shaped garden patio that extends past the property boundary line. "
                "Sutherland-Hodgman acts like a precision cookie cutter, trimming the patio polygon cleanly along the property fence line."
            ),
            visualization_connection=(
                "ProofMotion shows sequential clipping passes against Left, Right, Bottom, and Top boundaries in sequence, "
                "highlighting vertex transitions: In→In, In→Out, Out→Out, and Out→In."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="3D Graphics Hardware Frustum Clipping",
                description=(
                    "Every 3D GPU graphics pipeline clips polygon triangles against the 6 camera frustum planes "
                    "(Near, Far, Left, Right, Top, Bottom) before perspective division using Sutherland-Hodgman algorithms."
                ),
                contexts=[
                    "Hardware clipping units in GPUs (Direct3D / Vulkan pipelines).",
                    "Shadow volume stencil clipping in real-time lighting engines.",
                ],
                tag="3D Graphics Pipelines",
            ),
            RealWorldApplication(
                title="Geographic Information Systems (GIS) Polygon Intersections",
                description=(
                    "Urban planners calculate land-use zoning intersections by clipping municipal parcel polygons against "
                    "floodplain boundary polygons to determine flood insurance risk zones."
                ),
                contexts=[
                    "PostGIS ST_Intersection spatial polygon queries.",
                    "Satellite imagery land classification boundaries.",
                ],
                tag="GIS & Urban Planning",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="When Sutherland-Hodgman processes an edge transitioning from INSIDE to OUTSIDE the clipping boundary, what vertex is output?",
                options=[
                    "The outside vertex",
                    "Only the intersection point between the edge and the clipping boundary line",
                    "Both vertices",
                    "No vertex is output",
                ],
                correct_index=1,
                explanation="When exiting the boundary (In → Out), the clipping edge terminates at the boundary, so only the intersection point is added to the output vertex list.",
            ),
            QuizQuestion(
                question="When Sutherland-Hodgman processes an edge transitioning from OUTSIDE to INSIDE the clipping boundary, what vertices are output?",
                options=[
                    "No vertices are output",
                    "Both the intersection vertex and the terminating inside vertex are output",
                    "Only the starting outside vertex is output",
                    "The entire polygon is discarded",
                ],
                correct_index=1,
                explanation="Entering the valid half-plane produces two points: the boundary intersection point where the edge enters, followed by the terminating vertex located inside.",
            ),
            QuizQuestion(
                question="What geometric limitation does basic Sutherland-Hodgman have when clipping concave polygons?",
                options=[
                    "It cannot clip lines",
                    "It can produce extraneous connecting bridge edges between separate concave components, which requires Weiler-Atherton to split cleanly",
                    "It only works on triangles",
                    "It changes all vertex colors to black",
                ],
                correct_index=1,
                explanation="Because Sutherland-Hodgman outputs a single continuous vertex loop, clipping a concave polygon across multiple boundaries can leave degenerate connecting edges between disconnected pieces.",
            ),
        ],
    ),

    # ------------------------------------------------------------------
    # 9. 3D PROJECTIONS
    # ------------------------------------------------------------------
    "proj_cube_persp": TopicPracticalData(
        topic_key="proj_cube_persp",
        display_name="3D Perspective Projection",
        category="3D Computer Graphics",
        summary="Projects 3D objects onto a 2D viewing plane where projection rays converge at a center of projection (focal point).",
        practical_example=PracticalExample(
            scenario="First-Person Video Game Camera View",
            description=(
                "When looking down a long highway or railway track in a 3D video game like Grand Theft Auto, the two parallel rails "
                "appear to converge toward a distant vanishing point on the horizon."
            ),
            visualization_connection=(
                "ProofMotion renders a 3D wireframe cube on the hardware OpenGL canvas, illustrating how distant vertices scale down."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Video Games & Virtual Reality (VR)",
                description=(
                    "All first-person 3D games and VR headsets (Meta Quest, Apple Vision Pro) use perspective projection "
                    "to replicate the human eye's natural depth perception."
                ),
                contexts=[
                    "VR stereoscopic dual-camera rendering.",
                    "3D video game camera field-of-view (FOV) sliders.",
                ],
                tag="Virtual Reality & Games",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="What is the defining characteristic of Perspective Projection compared to Orthographic Projection?",
                options=[
                    "Distant objects appear smaller because projection rays converge toward a focal center",
                    "Parallel lines always remain parallel on screen",
                    "It cannot display 3D models",
                    "It eliminates shadows",
                ],
                correct_index=0,
                explanation="In perspective projection, projection lines converge at a viewpoint, causing distant objects to shrink inversely with depth Z.",
            ),
            QuizQuestion(
                question="In standard perspective projection with camera focal length d, how are 3D coordinates (X, Y, Z) projected onto 2D screen coordinates (x_s, y_s)?",
                options=[
                    "x_s = X, y_s = Y (Z is ignored)",
                    "x_s = d · (X / Z), y_s = d · (Y / Z)",
                    "x_s = X · Z, y_s = Y · Z",
                    "x_s = X + d, y_s = Y + d",
                ],
                correct_index=1,
                explanation="By similar triangles, projected screen position scales inversely with distance Z: x_s = d · X / Z and y_s = d · Y / Z. Dividing by Z creates natural perspective foreshortening.",
            ),
            QuizQuestion(
                question="What visual effect is caused by perspective projection on parallel lines that recede into the distance?",
                options=[
                    "They remain exactly equidistant on screen",
                    "They appear to converge toward a common vanishing point on the horizon",
                    "They bend into circular arcs",
                    "They rotate 90 degrees",
                ],
                correct_index=1,
                explanation="Because objects and intervals shrink proportionally to 1/Z as depth increases, parallel railway tracks or hallway edges appear to meet at a vanishing point.",
            ),
        ],
    ),

    "proj_cube_ortho": TopicPracticalData(
        topic_key="proj_cube_ortho",
        display_name="3D Orthographic Projection",
        category="3D Computer Graphics",
        summary="Projects 3D objects with parallel projection rays perpendicular to the view plane, preserving true scale and parallel lines.",
        practical_example=PracticalExample(
            scenario="Architectural Blueprints & Engineering CAD Drawings",
            description=(
                "When an engineer drafts blueprints for a machined engine gear, a 10 mm bolt must measure identically regardless of "
                "whether it is in the foreground or background, ensuring precise manufacturing measurements."
            ),
            visualization_connection=(
                "ProofMotion displays the orthographic 3D cube with parallel projection lines, preserving dimension ratios."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title="Engineering CAD Software (SolidWorks, AutoCAD)",
                description=(
                    "Mechanical CAD systems use orthographic projections (Top, Front, Side viewports) so engineers can verify tolerances "
                    "without perspective distortion."
                ),
                contexts=[
                    "Machining blueprints and CNC toolpath verification.",
                    "Isometric strategy games (SimCity, Diablo).",
                ],
                tag="Mechanical CAD & Gaming",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question="Why do mechanical engineers rely on Orthographic viewports rather than Perspective viewports when dimensioning parts?",
                options=[
                    "Orthographic projection preserves exact scale and parallel lines without perspective shrinking",
                    "Orthographic views are faster to print in color",
                    "Perspective projection cannot render circles",
                    "Orthographic views prevent shadows",
                ],
                correct_index=0,
                explanation="Orthographic projection does not scale objects down with distance, allowing measurements and dimensions taken from drawings to represent true physical lengths.",
            ),
            QuizQuestion(
                question="What happens to depth coordinate Z in an orthographic projection onto the XY viewing plane?",
                options=[
                    "It is divided by focal length",
                    "Coordinates are mapped directly as x_s = X and y_s = Y; depth Z does not affect scale or position",
                    "Z is multiplied by infinity",
                    "Z replaces the X coordinate",
                ],
                correct_index=1,
                explanation="Orthographic projection uses parallel projection rays perpendicular to the view plane. Screen position is directly x_s = X and y_s = Y regardless of depth Z.",
            ),
            QuizQuestion(
                question="Does the apparent size of an object change when it moves farther along the view axis in orthographic projection?",
                options=[
                    "Yes, it gets smaller as 1/Z",
                    "No, object size on screen is strictly invariant with distance along the view axis",
                    "Yes, it expands",
                    "It flips upside down",
                ],
                correct_index=1,
                explanation="Because projection rays are completely parallel (no focal convergence), distance from the camera has zero effect on projected dimensions, preserving exact scale everywhere.",
            ),
        ],
    ),
}


# ======================================================================
# PUBLIC HELPER FUNCTIONS & FALLBACKS
# ======================================================================

def get_practical_content(topic_key: str) -> TopicPracticalData:
    """
    Retrieve structured practical learning data for any topic key.
    Provides graceful alias resolution and universal fallback.
    """
    if topic_key in PRACTICAL_KNOWLEDGE_BASE:
        return PRACTICAL_KNOWLEDGE_BASE[topic_key]

    # Check common aliases
    alias_map = {
        "trans_rotation_pivot": "trans_pivot_rotation",
        "rast_compare": "rast_bresenham",
        "curve_bspline": "curve_bezier",
        "curve_hermite": "curve_bezier",
        "proj_pyramid": "proj_cube_persp",
        "compare_mst": "prim_mst",
        "compare_sorting": "bubble_sort",
        "compare_searching": "linear_search",
    }
    target_key = alias_map.get(topic_key)
    if target_key and target_key in PRACTICAL_KNOWLEDGE_BASE:
        return PRACTICAL_KNOWLEDGE_BASE[target_key]

    # Universal graceful fallback
    clean_title = topic_key.replace("_", " ").title()
    return TopicPracticalData(
        topic_key=topic_key,
        display_name=clean_title,
        category="General Computing & Applied Mathematics",
        summary=f"Practical engineering applications and real-world relevance of {clean_title}.",
        practical_example=PracticalExample(
            scenario=f"Applied Computing with {clean_title}",
            description=(
                f"In commercial software development, {clean_title} provides a foundational algorithmic building block "
                "for transforming, organizing, or rendering data efficiently under constrained system resources."
            ),
            visualization_connection=(
                f"ProofMotion demonstrates the deterministic state progression of {clean_title}, "
                "illustrating why each intermediate state transition is mathematically necessary."
            ),
        ),
        real_world_applications=[
            RealWorldApplication(
                title=f"Industrial Systems & Software Infrastructure",
                description=(
                    f"Core implementations of {clean_title} are embedded in production operating systems, "
                    "database runtimes, or rendering graphics libraries."
                ),
                contexts=[
                    "Performance-critical loops in commercial software products.",
                    "Standard library and framework algorithmic components.",
                ],
                tag="Production Software",
            ),
        ],
        knowledge_check=[
            QuizQuestion(
                question=f"What is the primary engineering objective when applying {clean_title}?",
                options=[
                    "To solve the domain problem deterministically with optimal time and space complexity",
                    "To increase memory allocation size",
                    "To avoid using mathematical formulas",
                    "To generate random outcomes",
                ],
                correct_index=0,
                explanation=f"{clean_title} delivers provable deterministic behavior with well-defined mathematical complexity guarantees.",
            ),
        ],
    )
