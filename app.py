# app.py
from flask import Flask, render_template, request, jsonify
import traceback # For debugging
import math # For isnan, isinf
import numpy as np # For numpy float types

# Import core modules
from core.materials import MATERIALS_LIB, get_material
from core.cross_sections import create_cross_section
from core.elements import Beam, Column
from core.beam_solvers import (
    solve_simply_supported_beam_point_load,
    solve_cantilever_beam_point_load_end,
    solve_simply_supported_beam_udl,
    solve_cantilever_beam_udl
)
from core.column_solvers import solve_column_axial_buckling

app = Flask(__name__)

# --- Helper to prepare results for JSON (handle NaN/Inf) ---
def make_results_json_safe(data_to_clean):
    """
    Recursively traverses a dictionary or list and converts NaN/Infinity
    to string representations, and numpy floats to Python floats.
    """
    if isinstance(data_to_clean, dict):
        return {k: make_results_json_safe(v) for k, v in data_to_clean.items()}
    elif isinstance(data_to_clean, list):
        return [make_results_json_safe(i) for i in data_to_clean]
    # Updated line to be compatible with NumPy 2.0+
    elif isinstance(data_to_clean, np.floating): # Use np.floating to catch all NumPy float types
        data_to_clean = float(data_to_clean)
    
    if isinstance(data_to_clean, float):
        if math.isnan(data_to_clean):
            return "NaN"
        if math.isinf(data_to_clean):
            return "Infinity" if data_to_clean > 0 else "-Infinity"
    return data_to_clean


# --- Routes ---
@app.route('/')
def index():
    material_names = list(MATERIALS_LIB.keys())
    return render_template('index.html', material_names=material_names)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        app.logger.info(f"Received data for calculation: {data}")

        element_type = data.get('elementType')
        length_m = float(data.get('length'))
        material_name = data.get('material')
        
        section_type = data.get('sectionType')
        section_params_str = data.get('sectionParams', []) 
        section_params_mm = [float(p) for p in section_params_str]

        results = {}
        element_info = {}
        
        if element_type == 'beam':
            beam_support_type = data.get('beamSupportType')
            load_type = data.get('beamLoadType')
            
            beam = Beam(length_m, material_name, section_type, section_params_mm, beam_support_type)

            if beam_support_type == "simplySupported":
                if load_type == "pointLoad":
                    load_p_kn = float(data.get('pointLoad'))
                    load_pos_a_m_ratio = float(data.get('pointLoadPositionRatio', 0.5))
                    load_pos_a_m = length_m * load_pos_a_m_ratio
                    analysis_results = solve_simply_supported_beam_point_load(beam, load_p_kn * 1000, load_pos_a_m)
                elif load_type == "udl":
                    udl_w_kn_per_m = float(data.get('udlValue'))
                    analysis_results = solve_simply_supported_beam_udl(beam, udl_w_kn_per_m * 1000)
                else:
                    return jsonify({"error": f"Load type '{load_type}' not implemented for Simply Supported beams"}), 400
            
            elif beam_support_type == "cantilever":
                if load_type == "pointLoadEnd":
                    load_p_kn = float(data.get('pointLoad'))
                    analysis_results = solve_cantilever_beam_point_load_end(beam, load_p_kn * 1000)
                elif load_type == "udl":
                    udl_w_kn_per_m = float(data.get('udlValue'))
                    analysis_results = solve_cantilever_beam_udl(beam, udl_w_kn_per_m * 1000)
                else:
                    return jsonify({"error": f"Load type '{load_type}' not implemented for Cantilever beams"}), 400
            else:
                return jsonify({"error": f"Beam support type '{beam_support_type}' not implemented"}), 400
            
            results = analysis_results
            element_info = beam.get_element_info()

        elif element_type == 'column':
            eff_length_factor_Kx = float(data.get('effLengthFactorKx', 1.0))
            eff_length_factor_Ky = float(data.get('effLengthFactorKy', 1.0))
            axial_load_kn = float(data.get('axialLoad'))

            column = Column(length_m, material_name, section_type, section_params_mm, eff_length_factor_Kx, eff_length_factor_Ky)
            analysis_results = solve_column_axial_buckling(column, axial_load_kn * 1000)
            results = analysis_results
            element_info = column.get_element_info()
            
        else:
            return jsonify({"error": "Unknown element type"}), 400

        safe_results = make_results_json_safe(results)
        safe_element_info = make_results_json_safe(element_info)
        
        return jsonify({
            "success": True,
            "element_info": safe_element_info,
            "results": safe_results
        })

    except ValueError as ve:
        app.logger.error(f"ValueError in calculation: {ve}\n{traceback.format_exc()}")
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except KeyError as ke:
        app.logger.error(f"Missing key in input data: {ke}\n{traceback.format_exc()}")
        return jsonify({"error": f"Missing expected input data: {str(ke)}"}), 400
    except Exception as e:
        app.logger.error(f"Error during calculation: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "An unexpected error occurred on the server. Please check logs."}), 500


if __name__ == '__main__':
    app.run(debug=True)