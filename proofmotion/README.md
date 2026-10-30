# ProofMotion

ProofMotion is a desktop educational application for Computer Graphics and Image Processing (CGIP) and discrete mathematics. It is written in Python 3 using PyQt5, NumPy, SymPy, PyOpenGL, and OpenCV. The application demonstrates the step-by-step mathematical calculations behind theorem proofs, sorting and searching algorithms, 2D affine transformations, rasterization algorithms, and line/polygon clipping.

---

## Implementation Status

The table below summarizes the actual state of the codebase and whether each feature is accessible through the graphical user interface.

| Module / Feature | Backend Implementation | Accessible in UI | Technology | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Mathematical Theorems | Complete | Yes | SymPy, NumPy, QPainter | 4 theorems with step-by-step derivations |
| Sorting and Searching | Complete | Yes | Python, QPainter | 5 sorting and 2 searching algorithms |
| 2D Transformations | Complete | Yes | NumPy 3x3 matrices, QPainter | Column-vector format, composite transforms, window-to-viewport |
| Rasterization | Complete | Yes | Integer algorithms, QPainter | DDA, Bresenham (all 8 octants), Midpoint Circle on a pixel grid |
| Clipping | Complete | Yes | Region outcodes, QPainter | Cohen-Sutherland line and Sutherland-Hodgman polygon clipping |
| UI Controls | Complete | Yes | PyQt5 | Timers, steppers, presets, zoom, pan, grid, fullscreen |
| Image Processing | Complete | No | NumPy, OpenCV | Implemented in backend; navigation tab hidden |
| 3D Projections / OpenGL | Complete | No | NumPy 4x4 matrices, PyOpenGL | Implemented in backend; navigation tab hidden |

The active navigation bar currently displays five core sections: Theorems, Algorithms, Transformations, Rasterization, and Clipping. The Image Processing and 3D OpenGL modules are implemented in the computational backend and verified by automated tests, but their buttons have been removed from the navigation bar.

---

## Accessible Features

### 1. Theorem Visualizations
- **Pythagorean Theorem:** Right-triangle construction with configurable leg lengths $a$ and $b$, side squares, Bhaskara $(a+b)^2$ dissection proof, and numerical validation.
- **Circle Geometry:** Subdivides a circle into $n$ congruent sectors and rearranges them into an alternating strip approaching a rectangle of dimensions $\pi r \times r$ to derive area and circumference formulas.
- **Similar Triangles:** Triangle scaling by factor $k$, showing angle invariance ($\angle A = \angle A'$, $\angle B = \angle B'$, $\angle C = \angle C'$), proportional sides ($a'/a = b'/b = c'/c = k$), and quadratic area scaling ($k^2$).
- **Law of Cosines:** Projects altitude $h = a \sin C$ and splits the base into segments $CD = a \cos C$ and $DA = b - a \cos C$, deriving $c^2 = a^2 + b^2 - 2ab \cos C$ through the Pythagorean theorem.

### 2. Sorting and Searching Algorithms
- **Sorting Algorithms:** Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, and Quick Sort.
- **Searching Algorithms:** Linear Search and Binary Search (with input validation and automatic sorting of unsorted arrays).
- **Interface Details:** Dynamic bar chart with status tags (`CMP`, `SWAP`, `PIVOT`, `SORTED`), real-time operation counters, time and space complexity information, and synchronized pseudocode display.

### 3. 2D Geometric Transformations
- **Coordinate System:** 2D homogeneous coordinates using $3 \times 3$ matrices in column-vector convention ($P' = M \cdot P$).
- **Supported Operations:**
  - Translation $T(dx, dy)$
  - Scaling $S(sx, sy)$
  - Rotation about the origin $R(\theta)$
  - Rotation about an arbitrary pivot point $(cx, cy)$: $T(cx, cy) \cdot R(\theta) \cdot T(-cx, -cy)$
  - Reflection across the X-axis, Y-axis, origin, or the line $y = x$
  - Composite transformations ($T \cdot R \cdot S$) illustrating matrix non-commutativity
- **Window-to-Viewport:** Maps world coordinates $(X_{wmin}, Y_{wmin}, X_{wmax}, Y_{wmax})$ to screen device coordinates while maintaining aspect ratio.

### 4. Rasterization Algorithms
- **DDA Line Drawing:** Calculates $\Delta x$ and $\Delta y$, incremental floating-point steps, and pixel rounding.
- **Bresenham's Line Algorithm:** Uses integer arithmetic across all eight octants (shallow, steep, positive, and negative slopes) and tracks decision variable $p_k$.
- **Midpoint Circle Algorithm:** Evaluates initial decision parameter $p_0 = 1 - r$, iterates through the first octant, and generates remaining points using eight-way symmetry.
- **Grid Display:** Highlights pixels (`CURRENT`, `PLOTTED`, `START`, `END`) on a discrete Cartesian grid.

### 5. Clipping and Viewing
- **Cohen-Sutherland Line Clipping:** Computes 4-bit region outcodes (`LEFT`, `RIGHT`, `BOTTOM`, `TOP`), performs bitwise tests for trivial acceptance and trivial rejection, and calculates parametric edge intersections.
- **Sutherland-Hodgman Polygon Clipping:** Iteratively clips polygon edges against the four boundary lines of a rectangular clipping window. Tested on convex and concave shapes including stars, triangles, diamonds, and hexagons.

### 6. Playback and View Controls
- **Execution Transport:** Non-blocking play, pause, step forward, step backward, replay, and progress slider.
- **Speed Adjustment:** Playback speed slider ranging from 0.25x to 4.0x.
- **Canvas Navigation:** View toolbar (+, -, pan arrows, reset view, coordinate grid toggle, fullscreen toggle) and mouse-drag panning.
- **Inspector Panel:** Precision stepper controls, instant preset buttons, and validation messages.
- **HUD Panel:** Formula display, textual step explanations, and live intermediate metrics.

---

## Backend Features (Not in Active Navigation)

The following modules have complete backend implementations and unit test coverage, but their UI buttons are currently hidden:

### Image Processing (`proofmotion/cgip/image_processing.py`)
- **Implemented Operations:**
  - ITU-R BT.601 Grayscale conversion ($Y = 0.299R + 0.587G + 0.114B$) written with NumPy array operations.
  - Binary thresholding ($dst(x, y) = 255 \text{ if } src(x, y) \ge T \text{ else } 0$).
  - 2D Gaussian blur: evaluates the Gaussian formula $G(x,y) = \frac{1}{2\pi\sigma^2} e^{-\frac{x^2+y^2}{2\sigma^2}}$, normalizes the kernel, and convolves with reflected borders.
  - Mean filter: spatial averaging over a $K \times K$ neighborhood.
  - Median filter: neighborhood median selection to suppress salt-and-pepper noise.
  - Sobel edge detection: $3 \times 3$ horizontal and vertical convolution masks computing gradient magnitude $\sqrt{G_x^2 + G_y^2}$.
  - Canny edge detection: uses OpenCV (`cv2.Canny`) as a reference comparison.
- **Current Scope:** Runs on procedural test patterns (`shapes`, `checkerboard`, `salt_and_pepper`, `gradient`). An external image file picker is not yet attached.

### 3D Projections and OpenGL (`proofmotion/cgip/projection_3d.py`, `proofmotion/graphics/opengl_widget.py`)
- **Implemented Operations:**
  - 4x4 affine transformation engine: translation, scaling, 3-axis rotation, composite model matrix, look-at view matrix, perspective projection matrix, and orthographic projection matrix.
  - Dedicated OpenGL widget: `OpenGL3DWidget` (`QOpenGLWidget`) with depth testing (`GL_DEPTH_TEST`), alpha blending (`GL_BLEND`), line smoothing, RGB coordinate axes, ground grid, mouse orbit/pan/zoom, and wireframe/shaded rendering for cubes and pyramids.
  - The central canvas uses a `QStackedWidget` capable of switching between 2D and 3D widgets.

---

## Technology Stack

| Library | Role in Project |
| :--- | :--- |
| **Python 3** | Application language (tested on Python 3.9+). |
| **PyQt5** | GUI framework: window layout, splitters, custom widgets, event dispatching. |
| **NumPy** | Matrix arithmetic, vector transformations, and image convolution arrays. |
| **SymPy** | Symbolic algebra verification for theorem calculations. |
| **PyOpenGL** | Hardware-accelerated 3D rendering pipeline inside `QOpenGLWidget`. |
| **OpenCV** | Reference implementation for Canny edge detection comparison. |

---

## Project Structure

```
proofmotion/
├── main.py                               # Application entry point
├── requirements.txt                      # Project dependencies
├── README.md                             # Documentation
├── ui/                                   # Presentation layer
│   ├── main_window.py                    # Main window, navigation bar, and canvas stack
│   ├── theorem_panel.py                  # Left sidebar topic list
│   ├── parameter_panel.py                # Right sidebar inputs, steppers, and presets
│   ├── equation_panel.py                 # Lower panel formula and metrics display
│   ├── animation_controls.py             # Playback transport bar
│   └── view_controls.py                  # Zoom, pan, grid, and fullscreen toolbar
├── controllers/                          # Application logic
│   └── application_controller.py         # Coordinates UI events, engines, and step playback
├── models/                               # Data models
│   └── theorem_state.py                  # Theorem, ProofStep, and ParameterSpec classes
├── core/                                 # Shared infrastructure
│   └── step_model.py                     # Visualization step definitions and 2D drawing primitives
├── graphics/                             # Rendering components
│   ├── visualization_widget.py           # 2D QPainter canvas
│   └── opengl_widget.py                  # 3D PyOpenGL hardware canvas
├── theorems/                             # Mathematical theorem logic
│   ├── theorem_engine.py                 # Theorem coordinator
│   ├── pythagorean.py                    # Pythagorean theorem proof generator
│   ├── circle_geometry.py                # Circle sector rearrangement
│   ├── similar_triangles.py              # Triangle dilation calculations
│   └── law_of_cosines.py                 # Law of cosines derivation
├── algorithms/                           # Algorithm implementations
│   ├── algorithm_engine.py               # Sorting and searching coordinator
│   ├── sorting/                          # Bubble, Selection, Insertion, Merge, Quick sort
│   └── searching/                        # Linear and Binary search
├── cgip/                                 # Computer Graphics and Image Processing engines
│   ├── transformations.py                # 2D homogeneous matrices and window-to-viewport
│   ├── rasterization.py                  # DDA, Bresenham (8 octants), Midpoint circle
│   ├── clipping.py                       # Cohen-Sutherland and Sutherland-Hodgman clipping
│   ├── image_processing.py               # Manual 2D convolution and OpenCV reference
│   └── projection_3d.py                  # 4x4 model, view, and projection matrices
└── tests/                                # Automated tests (77 tests across 12 files)
    ├── test_theorems.py
    ├── test_sorting.py
    ├── test_searching.py
    ├── test_transformations.py
    ├── test_rasterization.py
    ├── test_clipping.py
    ├── test_polygon_clipping.py
    ├── test_cgip_theorem_integration.py
    ├── test_image_processing.py
    ├── test_projection_3d.py
    ├── test_opengl_integration.py
    └── test_gui_integration.py
```

---

## Installation and Setup

### 1. Prerequisites
Make sure Python 3.9 or newer is installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/proofmotion.git
cd proofmotion
```

### 3. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate        # macOS and Linux
# .\venv\Scripts\activate      # Windows
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

On macOS Apple Silicon machines, PyOpenGL runs over the system Metal OpenGL layer (`GL Version: 2.1 Metal`).

---

## Running the Application

From the project root directory:

```bash
PYTHONPATH=proofmotion python3 proofmotion/main.py
```

Or from inside the `proofmotion/` folder:

```bash
PYTHONPATH=. python3 main.py
```

---

## Verification and Testing

The repository includes a test suite covering mathematical consistency, algorithm traces, matrix operations, and UI interactions.

### Run tests with pytest:
```bash
PYTHONPATH=proofmotion python3 -m pytest proofmotion/tests
```

### Test execution output:
```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/saanvi/Downloads/proofmotion 2
collected 77 items

proofmotion/tests/test_cgip_theorem_integration.py ..                    [  2%]
proofmotion/tests/test_clipping.py .....                                 [  9%]
proofmotion/tests/test_gui_integration.py .............                  [ 25%]
proofmotion/tests/test_image_processing.py .........                     [ 37%]
proofmotion/tests/test_opengl_integration.py ............                [ 53%]
proofmotion/tests/test_polygon_clipping.py ....                          [ 58%]
proofmotion/tests/test_projection_3d.py .........                        [ 70%]
proofmotion/tests/test_rasterization.py ....                             [ 75%]
proofmotion/tests/test_searching.py ......                               [ 83%]
proofmotion/tests/test_sorting.py .                                      [ 84%]
proofmotion/tests/test_theorems.py .....                                 [ 90%]
proofmotion/tests/test_transformations.py .......                        [100%]

============================== 77 passed in 0.68s ==============================
```

### Run tests with Python's unittest runner:
```bash
PYTHONPATH=proofmotion python3 -m unittest discover -s proofmotion/tests -p "test_*.py" -v
```

---

## Known Limitations and Planned Work

1. **Active UI Focus:** The Image Processing and 3D OpenGL modules are currently disabled in `ui/main_window.py` to keep the interface focused on the core 2D curriculum. They can be re-enabled by adding them back to the navigation list.
2. **File Dialog for Images:** The image processing engine currently processes procedurally generated patterns. Connecting a `QFileDialog` for loading user-supplied JPEG/PNG images is planned.
3. **GLSL Shaders:** The 3D pipeline uses legacy fixed-function matrix loading for broad driver compatibility on macOS. Migrating to programmable vertex and fragment shaders with configurable lighting models is a potential next step.
4. **Additional 3D Models:** The 3D backend currently supports cubes and pyramids; adding a Wavefront `.obj` file parser will allow loading arbitrary meshes.
