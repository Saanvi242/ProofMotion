# ProofMotion — Interactive Mathematics, Algorithms and Computer Graphics Learning Platform

ProofMotion is an educational desktop application designed to bridge discrete mathematics, computer science algorithms, and fundamental computer graphics into an intuitive, visual learning experience. Built with Python 3, PyQt5, NumPy, SymPy, and PyOpenGL, ProofMotion breaks down abstract theorems and multi-stage algorithms into synchronized, step-by-step visual proofs, interactive diagrams, live mathematical derivations, and execution metrics.

---

## Table of Contents
- [Problem Statement & Objectives](#problem-statement--objectives)
- [Key Features](#key-features)
- [Implemented Modules](#implemented-modules)
  - [1. Mathematical Theorems](#1-mathematical-theorems)
  - [2. Sorting Algorithms](#2-sorting-algorithms)
  - [3. Searching Algorithms](#3-searching-algorithms)
  - [4. Graph Algorithms](#4-graph-algorithms)
  - [5. Trees & Traversals](#5-trees--traversals)
  - [6. 2D Geometric Transformations](#6-2d-geometric-transformations)
  - [7. Rasterization Algorithms](#7-rasterization-algorithms)
  - [8. Line and Polygon Clipping](#8-line-and-polygon-clipping)
  - [9. Interactive Viewport & Playback Controls](#9-interactive-viewport--playback-controls)
- [Pedagogical Teaching Architecture](#pedagogical-teaching-architecture)
- [Implementation Status](#implementation-status)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Running](#installation--running)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Future Scope & Planned Enhancements](#future-scope--planned-enhancements)
- [License](#license)

---

## Problem Statement & Objectives

### The Problem
Traditional computer science and mathematics pedagogy often presents theorems and graphics algorithms through static textbook diagrams and dense algebraic notation. Concepts such as:
- Spatial dissection proofs (e.g., Bhaskara's Pythagorean proof or circular sector rearrangement),
- Step-by-step algorithmic state transitions (e.g., pivot partitioning in Quick Sort or interval halving in Binary Search),
- Integer-based pixel decision variables across various octants (Bresenham's line and Midpoint circle algorithms), and
- Multi-boundary geometric clipping cases (Cohen-Sutherland outcodes and Sutherland-Hodgman polygon clipping)

are inherently dynamic. When taught statically, students frequently struggle to build geometric intuition, trace intermediate variables, or understand why algorithmic decisions are made.

### Project Objectives
1. **Visual Step-by-Step Transparency:** Deconstruct complex derivations and algorithms into discrete, sequentially animated steps where each change is highlighted in context.
2. **Synchronized Mathematical Explanations:** Display the exact formula, matrix, or pseudocode line alongside an English pedagogical explanation for every single step.
3. **Interactive Parametrization:** Empower learners to input custom numbers, arrays, coordinates, angles, and window boundaries to immediately observe how changes propagate.
4. **Intuitive Viewport Navigation:** Provide smooth panning, resetting, grid overlays, and fullscreen focus modes to explore visualizations without distraction.

---

## Key Features

- **Multi-Discipline Educational Scope:** Covers classic geometric theorems, fundamental discrete algorithms, and core Computer Graphics & Image Processing (CGIP) techniques.
- **Deterministic Step-by-Step Traces:** Pure computational logic generates comprehensive step objects with coordinate vectors, active indices, status tags, and explanatory text.
- **Synchronized Three-Panel Architecture:**
  - **Left Sidebar:** Module hierarchy and topic selection with custom vector icons.
  - **Center Canvas:** Smooth vector-rendered graphics with animated transitions, live HUD overlays, and flexible transport controls (Play, Pause, Step Back, Step Forward, Replay, Scrub).
  - **Right Sidebar:** Precision parameter controls with instant presets and a synchronized formula/metric inspector.
- **Responsive Layout & Focus Mode:** Collapsible panels, draggable splitters, and a full-canvas focus mode (press `Esc` to restore).

---

## Implemented Modules

### 1. Mathematical Theorems
Interactive geometric proofs with dynamic algebraic expressions and symbolic verification:
- **Pythagorean Theorem ($a^2 + b^2 = c^2$):**
  - Right-triangle construction with configurable leg lengths $a$ and $b$.
  - Geometric side squares representing $a^2$, $b^2$, and $c^2$.
  - Bhaskara's algebraic dissection proof showing $(a + b)^2 = 4 \cdot (\frac{1}{2}ab) + c^2 \implies a^2 + b^2 = c^2$.
  - Numerical sanity verification at every step.
- **Circle Geometry (Area $\pi r^2$ & Circumference $2\pi r$):**
  - Subdivides a circle of radius $r$ into $n$ congruent sectors.
  - Dynamically rearranges the sectors into an alternating strip approaching a parallelogram/rectangle of base $\pi r$ and height $r$.
  - Illustrates the limiting behavior that leads to $A = \pi r^2$.
- **Similar Triangles:**
  - Demonstrates geometric similarity between two triangles scaled by factor $k$.
  - Visualizes angle invariance ($\angle A = \angle A'$, $\angle B = \angle B'$, $\angle C = \angle C'$).
  - Demonstrates linear side proportionality ($a'/a = b'/b = c'/c = k$) and quadratic area scaling ($k^2$).
- **Law of Cosines ($c^2 = a^2 + b^2 - 2ab \cos C$):**
  - Projects an altitude $h = a \sin C$ from vertex $B$ down to the base.
  - Splits the base into segments $CD = a \cos C$ and $DA = b - a \cos C$.
  - Applies the Pythagorean theorem on sub-triangle $\triangle ABD$ to derive the full trigonometric formula.

### 2. Sorting Algorithms
Dedicated learning workspace preserving all proven sorting implementations, animated vertical bars, pointer cues, and live counters:
- **Bubble Sort:** Adjacent element comparisons, pairwise swaps, and early-exit optimization flag.
- **Selection Sort:** Scans unsorted suffixes to select the minimum element, swapping it into its sorted index.
- **Insertion Sort:** Iteratively shifts elements rightward to insert the current item into its correct sorted prefix position.
- **Merge Sort:** Recursive divide-and-conquer splitting arrays into halves and merging auxiliary sub-lists with linear scans.
- **Quick Sort:** Lomuto partition scheme with explicit pivot selection, scan pointers, and partition swaps.
- *Teaching & Metrics:* Step 0 concept introductions, comparison counters, swap/write counters, time complexity ($O$), space complexity, and synchronized pseudocode highlights.

### 3. Searching Algorithms
Dedicated search visualization workspace for linear and divide-and-conquer search paradigms:
- **Linear Search:** Sequential index scan with current pointer, target comparison, and termination flags.
- **Binary Search:** Interval halving on sorted arrays with dynamic `low`, `mid`, and `high` pointers, search range indicators, and automatic sorting of raw user input arrays.
- *Teaching & Metrics:* Educational comparison badges, search space halving visualizers, and logarithmic efficiency explanations.

### 4. Graph Algorithms
Interactive weighted graphs with real-time edge state badges, candidate cut edge inspection, and cycle detection:
- **Minimum Spanning Tree (Prim's Algorithm):**
  - Begins with arbitrary or user-chosen starting vertex.
  - Explains the **Cut Property**: at every step, identifies all candidate edges crossing from the visited component to the unvisited component.
  - Dynamically highlights the lightest cross-cut edge and proves why it is safe to add (*"Edge A-B with weight 3 was selected because it is the minimum-weight edge connecting the current MST to an unvisited vertex"*).
  - Updates total tree weight and tracks visited component expansion.
- **Minimum Spanning Tree (Kruskal's Algorithm):**
  - Sorts all graph edges globally in ascending order of weight.
  - Inspects edges one-by-one using **Disjoint Set Union (DSU) / Union-Find with Path Compression**.
  - **Explicit Cycle Detection:** When both endpoints share the same set root, the edge is rejected with red dashed styling and an educational explanation of what a cycle is and why trees must remain acyclic (*"Edge B-E with weight 5 was rejected because adding it would form a cycle"*).
  - When endpoints belong to different sets, accepts the edge and performs union.
- **Compare Prim vs Kruskal:**
  - Side-by-side verification proving both algorithms produce the exact same total MST weight.
  - Detailed comparison table of complexity, exploration strategies, and data structures.
- *Presets & Custom Graphs:* `Network Backbone`, `Metro Transit`, `Simple Diamond`, and custom user edge inputs (`u-v:wt, ...`) with automatic circular layout.

### 5. Trees & Traversals
Interactive Binary Search Tree operations and visual tree traversals:
- **Binary Search Tree (BST):**
  - **Introduction to BST:** Invariant demonstration ($(\text{Left}) < \text{Root} < (\text{Right})$) with sub-tree bounding boxes.
  - **BST Insertion:** Step-by-step navigation down the tree to locate the correct empty child slot, inserting while preserving ordering.
  - **BST Searching:** Path comparison against each node, demonstrating $O(\log n)$ logarithmic search space halving.
  - **BST Deletion:** Handles all three canonical cases:
    1. *Leaf Node (0 children):* Simply severed.
    2. *Single Child (1 child):* Parent adopts grandchild (bypass).
    3. *Two Children (2 children):* Locates in-order successor (minimum in right subtree), replaces value, and deletes successor leaf.
- **Tree Traversals:**
  - **Preorder (Root → Left → Right):** Demonstrates prefix evaluation, tree cloning, and hierarchical directory printing.
  - **Inorder (Left → Root → Right):** Demonstrates the property that in-order traversal of a BST outputs values in strictly sorted ascending order.
  - **Postorder (Left → Right → Root):** Bottom-up evaluation for postfix notation, directory size aggregation, and safe memory deallocation.
  - **Level Order Traversal:** Breadth-first level-by-level traversal using an explicit FIFO queue widget.
  - *Sequence Strip:* Traversal sequence strip dynamically displays visited nodes with explanatory transition badges.

### 6. 2D Geometric Transformations
Affine transformation pipeline using $3 \times 3$ homogeneous coordinate matrices in column-vector convention ($P' = M \cdot P$):
- **Translation:** Shifts geometries by vector $(dx, dy)$ using matrix:
  $$\begin{bmatrix} 1 & 0 & dx \\ 0 & 1 & dy \\ 0 & 0 & 1 \end{bmatrix}$$
- **Scaling:** Scales geometries by $(sx, sy)$ relative to origin or local reference point.
- **Rotation about Origin:** Rotates by angle $\theta$ using matrix:
  $$\begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
- **Rotation about Arbitrary Pivot $(cx, cy)$:** Demonstrates composite transformation pipeline:
  $$M = T(cx, cy) \cdot R(\theta) \cdot T(-cx, -cy)$$
- **Reflection:** Reflection across the X-axis, Y-axis, origin, and the diagonal line $y = x$.
- **Composite Transformations:** Successive applications of Translation, Rotation, and Scaling ($T \cdot R \cdot S$), demonstrating matrix non-commutativity ($A \cdot B \neq B \cdot A$).

### 7. Rasterization Algorithms
Discrete Cartesian grid visualization highlighting pixel states (`CURRENT`, `PLOTTED`, `START`, `END`):
- **DDA (Digital Differential Analyzer) Line:**
  - Calculates $\Delta x$, $\Delta y$, and iteration steps $N = \max(|\Delta x|, |\Delta y|)$.
  - Demonstrates floating-point increments $(x_{k+1} = x_k + \Delta x / N, y_{k+1} = y_k + \Delta y / N)$ and pixel rounding $\text{round}(x_k), \text{round}(y_k)$.
- **Bresenham's Line Algorithm:**
  - Efficient integer-only arithmetic avoiding floating-point rounding.
  - Evaluates decision parameter $p_k$ to choose between east and north-east pixels.
  - Robust implementation supporting all 8 octants (shallow slopes, steep slopes, positive and negative directions).
- **Midpoint Circle Algorithm:**
  - Evaluates initial decision parameter $p_0 = 1 - r$.
  - Iterates through the first octant ($x = 0$ to $x \ge y$) updating $p_k$ with integer additions.
  - Applies 8-way circular symmetry to mirror plotted points across all octants simultaneously.
- **Bézier Curve Subdivision & Pixel Rasterization (De Casteljau's Algorithm):**
  - Starts with four draggable control points and the original cubic Bézier curve.
  - Demonstrates repeated midpoint interpolation at $t = 0.5$ ($Q_0, Q_1, Q_2 \to R_0, R_1 \to S_0$).
  - Shows how De Casteljau's construction splits the curve into two smaller exact cubic Bézier curves (Left: $[P_0, Q_0, R_0, S_0]$, Right: $[S_0, R_1, Q_2, P_3]$).
  - Recursive subdivision ($2^d$ segments) converging to flat chords.
  - **Complete Pixel Rasterization:** Passes each subdivided segment chord to a selectable line rasterizer (**Bresenham** or **DDA**), displaying progressive pixel plotting, integer decision variables ($\text{err}, 2\cdot\text{err}$) or floating increments ($\Delta x / N, \Delta y / N$), active chord highlights with start/end badges, and live coordinate grid rendering.

### 8. Line and Polygon Clipping
Pedagogical viewing algorithms with geometric boundary testing:
- **Cohen-Sutherland Line Clipping:**
  - Computes 4-bit region outcodes ($\text{TOP}, \text{BOTTOM}, \text{RIGHT}, \text{LEFT}$) for endpoints.
  - Step-by-step bitwise OR testing for trivial acceptance ($P_1 \text{ code} = 0 \text{ and } P_2 \text{ code} = 0$).
  - Bitwise AND testing for trivial rejection ($P_1 \text{ code} \ \& \ P_2 \text{ code} \neq 0$).
  - Exact parametric intersection calculations against boundary lines $x = x_{\min}, x_{\max}$ and $y = y_{\min}, y_{\max}$.
- **Sutherland-Hodgman Polygon Clipping:**
  - Sequential pipeline clipping an arbitrary polygon against four infinite boundary edges (Left, Right, Bottom, Top).
  - Explicitly categorizes every edge transition into one of the four geometric cases:
    1. *In to In:* Output destination vertex $V_2$.
    2. *In to Out:* Output edge intersection $I$.
    3. *Out to Out:* Output nothing (rejected).
    4. *Out to In:* Output edge intersection $I$ and destination vertex $V_2$.
  - Supports convex and concave test geometries (triangles, diamonds, stars, hexagons).

### 9. Interactive Viewport & Playback Controls
- **Transport Bar:** Play, pause, single-step forward, single-step backward, replay, and timeline slider.
- **Speed Multiplier:** Variable playback speed scaling from 0.25x to 4.0x.
- **Canvas Navigation:** View toolbar with pan arrows, view reset, coordinate grid toggle, and fullscreen focus mode. Zoom in/out controls are enabled for geometric and graphics modules and automatically hidden for discrete algorithm bar views.
- **Parameter & Preset Panel:** Precision steppers and instant preset buttons (e.g., standard triangle dimensions, steep/shallow slopes, clipping cases).

### 10. Studio Proof Builder
Interactive authoring studio where students and educators can create custom mathematical proofs of any theorem from scratch or using templates:
- **Custom Steps Management:** Add, duplicate, delete, reorder, and carry forward shapes from previous steps.
- **Rich Mathematical Geometry Primitives:** Place and configure Points, Lines, Polygons, Triangles, Rectangles, Circles, Angle Arcs, Right-Angle (90°) symbols, and Math Text labels.
- **Interactive Drag-to-Edit Canvas:** Drag vertices on the live canvas with grid snapping, coordinate readout, and real-time shape updates.
- **Pedagogical Step Editor:** Enter step titles, equations with a clickable mathematical symbol bar (², ³, √, ∠, °, ⊥, ∥, Δ, π, θ, α, β, ⟹, ≅), and formatted explanations following the 5-step WHY-before-WHAT rule.
- **Prebuilt Educational Templates:** Instant one-click starters for Pythagorean Theorem ($a^2 + b^2 = c^2$), Triangle Angle Sum ($180^\circ$), Thales's Theorem (angle in a semicircle is $90^\circ$), Exterior Angle Theorem, and Triangle Area formula ($\frac{1}{2}bh$).
- **Built-in Learn Presentation View:** Presents the user's custom proof with the exact visual fidelity, smooth vector lerp animation, equation panel, and transport controls as prebuilt proofs in the Learn section.
- **Save & Load:** Export and import custom theorem proofs to and from standard JSON files.

---

## Pedagogical Teaching Architecture

ProofMotion is designed as an interactive engineering textbook where students understand *why* each step happens rather than merely watching animations.

### 1. Introduce Concept Before Algorithm (Step 0)
Every module begins with an intuitive introduction addressing:
- **What is this concept?** Clear, jargon-free explanation.
- **Why do we need it?** What practical problem does it solve?
- **Where is it used?** Real-world applications (e.g., network fiber routing, GPS navigation, compiler expression parsing).
- **Key Terms:** Clear definitions of foundational terms before mathematical steps begin.

### 2. The 5-Step "WHY Before WHAT" Rule
Every operational step follows a strict 5-stage pedagogical sequence:
1. **What are we trying to do?** High-level task definition.
2. **Why are we doing this?** Algorithmic justification (e.g., why this edge was considered, why distance was relaxed).
3. **What operation or calculation?** Explicit formula with substituted numbers.
4. **What does the result mean?** Interpretation of the intermediate outcome.
5. **What happens next?** Forward-looking cue to the next state transition.

### 3. Progressive Reveal & Exact Correspondence
Visual highlights, badge states, and formulas strictly correspond with current narrative explanations. Labels automatically adjust positions using collision-free placement logic to prevent visual clutter.

---

## Implementation Status

| Module / Feature | Backend Logic | Graphical UI | Technology Stack | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Mathematical Theorems** | Complete | Complete | SymPy, NumPy, QPainter | Production Ready |
| **Sorting & Searching** | Complete | Complete | Python, QPainter | Production Ready |
| **2D Geometric Transformations** | Complete | Complete | NumPy 3x3 Matrices, QPainter | Production Ready |
| **Rasterization Algorithms** | Complete | Complete | Integer Algorithms, QPainter | Production Ready |
| **Line & Polygon Clipping** | Complete | Complete | Region Outcodes, QPainter | Production Ready |
| **Interactive Playback & UI** | Complete | Complete | PyQt5 Custom Widgets | Production Ready |
| **3D Projections Studio** | Complete | Available via OpenGL canvas | NumPy 4x4 Matrices, PyOpenGL | Production Ready |
| **Studio Proof Builder** | Complete | Complete | Python, QPainter, Step Models | Production Ready |

---

## Technology Stack

| Library / Tool | Role in ProofMotion |
| :--- | :--- |
| **Python 3** | Core application language (compatible with Python 3.9+). |
| **PyQt5** | Desktop GUI framework, splitters, layout management, vector canvas painting (`QPainter`), and signal/slot event dispatching. |
| **NumPy** | High-performance matrix arithmetic, coordinate transformations, and vector computations. |
| **SymPy** | Symbolic algebra verification and exact mathematical formula derivations. |
| **PyOpenGL** | Hardware-accelerated OpenGL pipeline used in the 3D projection engine. |
| **Pytest** | Automated unit and integration testing framework. |

---

## Project Structure

```
proofmotion 3/
├── README.md                           # Project root documentation
└── proofmotion/                        # Application source package
    ├── main.py                         # Application entry point and font bootstrapping
    ├── requirements.txt                # Production dependencies
    ├── README.md                       # Package documentation
    │
    ├── algorithms/                     # Discrete algorithms module
    │   ├── algorithm_engine.py         # Algorithm registry and coordinator
    │   ├── searching/                  # Searching implementations
    │   │   ├── binary_search.py        # Interval halving trace generator
    │   │   └── linear_search.py        # Sequential scan trace generator
    │   └── sorting/                    # Sorting implementations
    │       ├── bubble_sort.py          # Bubble sort trace generator
    │       ├── insertion_sort.py       # Insertion sort trace generator
    │       ├── merge_sort.py           # Merge sort trace generator
    │       ├── quick_sort.py           # Quick sort trace generator
    │       ├── selection_sort.py       # Selection sort trace generator
    │       └── sorting_events.py       # Semantic event data structures
    │
    ├── cgip/                           # Computer Graphics and Image Processing algorithms
    │   ├── clipping.py                 # Cohen-Sutherland and Sutherland-Hodgman clipping
    │   ├── projection_3d.py            # 4x4 3D affine matrix math & projection engine
    │   ├── rasterization.py            # DDA, Bresenham, and Midpoint Circle algorithms
    │   └── transformations.py          # 2D affine transformations (3x3 homogeneous matrices)
    │
    ├── controllers/                    # Application controllers
    │   └── application_controller.py   # Central coordinator between UI, state, and engines
    │
    ├── core/                           # Shared core data models
    │   └── step_model.py               # RenderData, Point2D, Line2D, VisualizationStep
    │
    ├── graphics/                       # Rendering widgets and display logic
    │   ├── opengl_widget.py            # Hardware-accelerated QOpenGLWidget for 3D projections
    │   ├── sorting_renderer.py         # Dynamic sorting bar visualizations
    │   └── visualization_widget.py     # High-precision QPainter 2D vector canvas
    │
    ├── models/                         # UI state models
    │   └── theorem_state.py            # Theorem metadata, parameters, and step structures
    │
    ├── resources/                      # Application styling and static assets
    │   ├── backgroungimage.jpg         # Canvas background texture
    │   ├── geo_background.py           # Procedural geometric canvas backdrop
    │   ├── logo.png / icon.png         # Vector branding and icons
    │   ├── theme.py                    # Design tokens, color palettes, and typography
    │   └── Inter-*.otf                 # Inter font families
    │
    ├── tests/                          # Automated test suite (98 unit & integration tests)
    │   ├── test_cgip_theorem_integration.py
    │   ├── test_clipping.py
    │   ├── test_gui_integration.py
    │   ├── test_opengl_integration.py
    │   ├── test_polygon_clipping.py
    │   ├── test_projection_3d.py
    │   ├── test_rasterization.py
    │   ├── test_searching.py
    │   ├── test_sorting.py
    │   ├── test_sorting_playground.py
    │   ├── test_theorems.py
    │   └── test_transformations.py
    │
    ├── theorems/                       # Mathematical theorem visualizers
    │   ├── circle_geometry.py          # Circular sector rearrangement proof
    │   ├── law_of_cosines.py           # Altitude projection proof
    │   ├── pythagorean.py              # Bhaskara dissection proof
    │   ├── similar_triangles.py        # Proportionality & area scaling proof
    │   └── theorem_engine.py           # Theorem registry and step evaluator
    │
    └── ui/                             # PyQt5 user interface components
        ├── animation_controls.py       # Transport bar (Play/Pause, Slider, Speed)
        ├── clipping_tabs.py            # Lesson sub-tabs for clipping algorithms
        ├── equation_panel.py           # Mathematical formula and pseudocode HUD
        ├── main_window.py              # Top-level window, header navigation, canvas stack
        ├── parameter_panel.py          # Parameter steppers, input boxes, presets
        ├── theorem_panel.py            # Sidebar topic selector
        └── view_controls.py            # Zoom, Pan, Grid, and Fullscreen toolbar
```

---

## Installation & Running

### Prerequisites
- Python 3.9 or higher
- `pip` package manager
- macOS, Linux, or Windows with OpenGL support

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/proofmotion.git
   cd "proofmotion 3"
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate       # On macOS/Linux
   # or: venv\Scripts\activate    # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r proofmotion/requirements.txt
   ```

4. **Run the application:**
   ```bash
   cd proofmotion
   python3 main.py
   ```

---

## Testing & Quality Assurance

ProofMotion includes an automated test suite comprising **98 tests** across 12 test files, ensuring numerical accuracy, edge case handling, and crash-free UI signal dispatching.

### Running Tests
Execute the entire test suite using `pytest`:
```bash
PYTHONPATH=proofmotion python3 -m pytest proofmotion/tests
```

Or execute using Python's built-in `unittest` runner:
```bash
PYTHONPATH=proofmotion python3 -m unittest discover -s proofmotion/tests -p "test_*.py" -v
```

### Test Coverage Highlights
- **Theorems:** Verifies numeric invariants, altitude calculations, sector angles, and Bhaskara identity equality.
- **Sorting & Searching:** Tests edge cases (empty arrays, single-element arrays, identical values, negative integers, unsorted search inputs).
- **Transformations:** Confirms column-vector matrix products, pivot shift reversibility, and matrix non-commutativity.
- **Rasterization:** Validates DDA and Bresenham across all 8 octants, steep slopes ($|m| > 1$), negative directions, and Midpoint circle 8-way symmetry points.
- **Clipping:** Evaluates Cohen-Sutherland outcode classifications (trivial acceptance, trivial rejection, boundary intersections) and Sutherland-Hodgman polygon clipping on convex and concave geometries.
- **GUI Integration:** Tests module switching, parameter updates, transport state changes, fullscreen toggles, and view zoom/pan behaviors.

---

## Future Scope & Planned Enhancements

ProofMotion is designed as an extensible educational framework. Planned features for upcoming releases include:

### A. 2D and 3D Graphics Modes
- **Dual Graphics Selector:** Introduce a prominent mode toggle allowing users to choose between 2D Graphics and 3D Graphics environments upon opening the graphics module.
- **Interactive 3D Viewport:** Surface the existing hardware-accelerated OpenGL engine into the primary navigation, featuring interactive orbit camera controls, ground grids, and labeled RGB Cartesian axes.
- **Projection Comparisons:** Provide side-by-side split views comparing Perspective Projection (with depth division and vanishing points) against Orthographic Projection (parallel affine projection).

### B. Enhanced 3D Transformations
- **Arbitrary-axis rotation:** Extend the shipped X/Y/Z lessons with rotation about a custom spatial vector.
- **Animated 3D Space Trajectories:** Smooth interpolation showing geometries transitioning through 3D space, making spatial orientation changes intuitive.

### C. More Interactive Learning Experiences
- **Guided Step-by-Step Walkthroughs:** Structured pedagogical lessons with contextual annotations explaining *why* specific intermediate steps are taken (e.g., why a decision parameter becomes negative).
- **Interactive Understanding Quizzes:** Bite-sized challenge checkpoints at the end of visualizations (e.g., "What will be the next decision parameter $p_{k+1}$?" or "Compute the 4-bit outcode for point $(-4, 3)$").
- **Interactive Shape & Point Creator:** Allow learners to click directly on the canvas to place custom line endpoints, define clipping polygons, or drag triangle vertices to see proofs adapt in real time.

### D. Algorithm Visualization Improvements
- **Expanded Algorithm Library:** Add additional sorting algorithms (e.g., Heap Sort, Radix Sort) and searching techniques (e.g., Interpolation Search, Exponential Search).
- **Multi-Algorithm Race & Benchmark Mode:** Run two sorting algorithms side-by-side on the identical input dataset to compare total comparisons, memory writes, and visual completion time.
- **Alternative Visual Encodings:** Offer different visualization metaphors such as scatter plots, radial circle sorting, and audible frequency synthesis where pitch corresponds to element values.

### E. Export & Study Documentation
- **Worksheet and Report Generation:** One-click export of visual proofs and step-by-step mathematical derivations to formatted PDF study sheets.
- **Animation Export:** Export step sequences as lightweight animated GIFs or SVG sequences for lecture presentations and academic homework.

---

## License

ProofMotion is distributed under the MIT License. You are free to use, modify, and distribute this software for educational and academic purposes.
