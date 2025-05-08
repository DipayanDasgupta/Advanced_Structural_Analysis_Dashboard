# core/column_solvers.py
import math
import numpy as np

def solve_column_axial_buckling(column_element, axial_load_P_N):
    """
    Solves a column for axial stress and Euler buckling.
    Args:
        column_element (Column): The column object.
        axial_load_P_N (float): Magnitude of the axial compressive load (positive).
    Returns:
        dict: Updated column_element.results
    """
    L = column_element.length_m
    E = column_element.material.E_Pa
    A = column_element.cross_section.area_m2
    Ix = column_element.cross_section.Ix_m4
    Iy = column_element.cross_section.Iy_m4
    Kx = column_element.Kx
    Ky = column_element.Ky
    Fy = column_element.material.Fy_Pa

    results = column_element.results

    # 1. Axial Stress
    if A > 0:
        axial_stress_Pa = axial_load_P_N / A
    else:
        axial_stress_Pa = float('inf')
    results["axial_stress_Pa"] = axial_stress_Pa

    # 2. Euler Buckling Critical Loads
    # Buckling about strong axis (x-x)
    Pcr_x_N = (math.pi**2 * E * Ix) / (Kx * L)**2 if (Kx * L) > 0 and E * Ix > 0 else float('inf')
    # Buckling about weak axis (y-y)
    Pcr_y_N = (math.pi**2 * E * Iy) / (Ky * L)**2 if (Ky * L) > 0 and E * Iy > 0 else float('inf')
    
    results["critical_buckling_load_Pcr_x_N"] = Pcr_x_N
    results["critical_buckling_load_Pcr_y_N"] = Pcr_y_N
    
    min_Pcr_N = min(Pcr_x_N, Pcr_y_N)
    results["min_critical_buckling_load_N"] = min_Pcr_N

    # Buckling Stresses
    results["critical_buckling_stress_Fcr_x_Pa"] = Pcr_x_N / A if A > 0 else float('inf')
    results["critical_buckling_stress_Fcr_y_Pa"] = Pcr_y_N / A if A > 0 else float('inf')

    # 3. Failure Checks
    # Yielding / Crushing (axial stress vs yield strength)
    yielding_ratio = axial_stress_Pa / Fy if Fy > 0 else float('inf')
    results["failure_checks"]["yielding_crushing"] = {
        "demand_Pa": axial_stress_Pa,
        "capacity_Pa": Fy,
        "ratio": yielding_ratio,
        "status": "FAIL" if yielding_ratio >= 1.0 else "PASS"
    }

    # Buckling (applied load vs critical buckling load)
    # Euler buckling is valid if Fcr <= Fy (elastic buckling)
    # If Fcr > Fy, yielding occurs first. More advanced codes use inelastic buckling curves.
    # For simplicity, we check P vs Pcr.
    buckling_ratio = axial_load_P_N / min_Pcr_N if min_Pcr_N > 0 else float('inf')
    buckling_status = "FAIL"
    buckling_note = ""

    if buckling_ratio >= 1.0:
        buckling_status = "FAIL (Buckling)"
    elif min_Pcr_N / A > Fy : # If critical elastic buckling stress exceeds yield
        buckling_status = "PASS (Buckling check governed by yielding)"
        buckling_note = "Elastic buckling stress > yield; yielding governs if P < Pcr. For P > Pcr *and* P > Pyield, actual failure is complex."
        # If axial_stress < Fy and P < Pcr, then it's a pass for both.
        if yielding_ratio < 1.0: # Redundant check, but clear
             buckling_status = "PASS"
    else: # Elastic buckling is possible
        buckling_status = "PASS"


    results["failure_checks"]["euler_buckling"] = {
        "demand_N": axial_load_P_N,
        "capacity_N": min_Pcr_N,
        "ratio": buckling_ratio,
        "status": buckling_status,
        "note": buckling_note
    }
    
    column_element.results = results
    return results