# Advanced Structural Simulator

This application simulates bending, buckling, and failure of different structural elements.
It uses a Python Flask backend for calculations and a JavaScript frontend for UI and visualization.

## Project Structure

structural_simulator_py/
├── app.py # Flask app (main Python script to run)
├── core/ # Python calculation modules
│ ├── init.py
│ ├── materials.py
│ ├── cross_sections.py
│ ├── elements.py
│ ├── beam_solvers.py
│ ├── column_solvers.py
│ └── utils.py
├── static/
│ ├── css/
│ │ └── style.css
│ ├── js/
│ │ └── script.js
│ └── lib/
│ └── plotly.min.js # (Optional if using CDN) Download from plotly.com
├── templates/
│ └── index.html
└── README.md



## Setup

1.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install Flask numpy
    ```
    (NumPy is used implicitly by some calculations or can be added for more advanced ones).

3.  **Download Plotly.js (Optional):**
    If you prefer not to use the CDN link for Plotly.js in `index.html`, download `plotly.min.js` from [https://plotly.com/javascript/getting-started/](https://plotly.com/javascript/getting-started/) and place it in the `static/lib/` directory. Then, update the script tag in `index.html`:
    ```html
    <!-- <script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script> -->
    <script src="{{ url_for('static', filename='lib/plotly.min.js') }}"></script>
    ```

## Running the Application

1.  **Activate the virtual environment** (if you created one and it's not active).
2.  **Run the Flask application:**
    ```bash
    python app.py
    ```
3.  Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Features

*   **Element Types:** Beams and Columns.
*   **Beam Analysis:**
    *   Supports: Simply Supported, Cantilever (Fixed Left).
    *   Loads: Point Load (at any position for SSB, at end for Cantilever).
    *   Calculations: Reactions, Shear Force, Bending Moment, Deflection.
    *   Diagrams: SFD, BMD, Deflection Plot.
    *   Stress Analysis: Max Bending Stress, Max Shear Stress.
    *   Visualizations: Element diagram with load, supports, exaggerated deflected shape, bending moment color gradient along length, cross-section stress distribution.
*   **Column Analysis:**
    *   Loads: Axial Compressive Load.
    *   Calculations: Axial Stress, Euler Critical Buckling Load (Pcr for both axes).
    *   Visualizations: Column diagram with load, supports, (potential) buckled shape, axial stress color gradient, cross-section stress distribution.
*   **Material Library:** Predefined materials (Steel, Aluminum, Wood) with E, Fy.
*   **Cross-sections:** Rectangular, Circular.
*   **Failure Checks:**
    *   Beams: Bending Yield, Shear Yield, Deflection Limits.
    *   Columns: Yielding/Crushing, Euler Buckling.
*   **Interactive UI:**
    *   Sliders and inputs for dimensions, loads, material properties.
    *   Dynamic updates of displayed values.
    *   Selection of element type, support conditions, load types.
*   **Detailed Output:** JSON representation of inputs and all calculated results.

## How it Works

*   **Backend (Python/Flask):**
    *   `app.py`: Handles HTTP requests, serves the HTML page, and provides a `/calculate` API endpoint.
    *   `core/`: Contains modules for:
        *   `materials.py`: Defines material properties.
        *   `cross_sections.py`: Defines cross-sectional properties (Area, I, Z, etc.).
        *   `elements.py`: Defines `Beam` and `Column` classes.
        *   `beam_solvers.py`, `column_solvers.py`: Contain the engineering calculation logic for specific element types and load cases.
        *   `utils.py`: Helper functions (e.g., point generation, color mapping).
*   **Frontend (HTML/CSS/JavaScript):**
    *   `templates/index.html`: The main web page structure with input forms and placeholders for results/visualizations.
    *   `static/css/style.css`: Styles for the page.
    *   `static/js/script.js`: Handles all client-side interactivity:
        *   Collecting user inputs.
        *   Sending calculation requests to the Flask backend via `fetch` API.
        *   Receiving JSON results.
        *   Displaying numerical results and failure statuses.
        *   Using Plotly.js to render SFD, BMD, and Deflection plots.
        *   Using HTML5 Canvas to draw schematic diagrams of elements, loads, supports, deflected shapes, and stress distributions/gradients.

## Future Enhancements (Complexity Ideas)

*   **More Beam Load Types:** Uniformly Distributed Loads (UDL), Triangular Loads (LVL), Applied Moments.
*   **More Beam Support Types:** Fixed-Fixed, Propped Cantilever, Continuous Beams (2-span to start).
*   **Advanced Beam Solvers:** Numerical integration for complex load cases if closed-form solutions are too cumbersome.
*   **More Column End Conditions:** GUI to select standard end conditions (Fixed-Fixed, Fixed-Pinned, etc.) which map to K-factors.
*   **More Cross-sections:** I-Beams (with a small library of standard profiles), T-Beams, Hollow Rectangular/Circular sections.
*   **2D Trusses:**
    *   GUI for defining truss geometry (nodes, members).
    *   Method of Joints/Sections for analysis.
    *   Axial forces, stresses, buckling checks for members.
    *   Color-coded visualization of tension/compression.
*   **2D Frames (Simple):** Determinate portal frames. SFD, BMD, AFD for members.
*   **Combined Stresses:** e.g., Beam-columns (axial load + bending).
*   **Advanced Failure Modes:**
    *   Lateral Torsional Buckling (LTB) for slender beams.
    *   Inelastic buckling for columns.
    *   Von Mises / Tresca yield criteria (if principal stresses are calculated).
*   **Strain Calculation & Visualization:** (ε = σ/E for axial, ε = My/(EI) for bending curvature).
*   **More Sophisticated Canvas Visualizations:**
    *   Interactive cross-section viewer.
    *   3D-like representation (isometric) of simple elements.
*   **Units System:** Allow user to select input/output units (e.g., metric/imperial).
*   **Saving/Loading Designs:** Persist user configurations.