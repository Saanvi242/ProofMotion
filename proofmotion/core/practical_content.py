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
