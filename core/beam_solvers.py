# core/beam_solvers.py
import numpy as np
import math
from .utils import generate_beam_points

def solve_simply_supported_beam_point_load(beam_element, load_P_N, load_pos_a_m):
    """
    Solves a simply supported beam with a single point load P.
    Args:
        beam_element (Beam): The beam object.
        load_P_N (float): Magnitude of the point load (positive downwards).
        load_pos_a_m (float): Distance of the load from the left support (0 < a < L).
    Returns:
        dict: Updated beam_element.results
    """
    L = beam_element.length_m
    E = beam_element.material.E_Pa
    I = beam_element.cross_section.Ix_m4 # Assuming bending about strong x-axis
    Fy = beam_element.material.Fy_Pa
    Fsy = beam_element.material.Fsy_Pa # Shear yield strength
    Z_top = beam_element.cross_section.Zx_top_m3
    Z_bottom = beam_element.cross_section.Zx_bottom_m3
    
    if not (0 < load_pos_a_m < L):
        raise ValueError("Load position 'a' must be between 0 and L (exclusive).")

    results = beam_element.results # Get a reference to update

    # 1. Reactions
    b = L - load_pos_a_m
    R_A = (load_P_N * b) / L  # Reaction at left support (x=0)
    R_B = (load_P_N * load_pos_a_m) / L  # Reaction at right support (x=L)
    results["reactions"] = {"R_A_N": R_A, "R_B_N": R_B}

    # 2. SFD, BMD, Deflection Points
    # Ensure load_pos_a_m is part of the x_coords for accurate plotting of discontinuities
    x_coords = generate_beam_points(L)
    if load_pos_a_m not in x_coords:
        x_coords = np.sort(np.append(x_coords, load_pos_a_m))
        x_coords = np.unique(x_coords) # Remove duplicates if any from append

    shear_forces_arr = np.zeros_like(x_coords) # For internal calculation
    bending_moments_arr = np.zeros_like(x_coords)
    deflections_arr = np.zeros_like(x_coords)

    for i, x in enumerate(x_coords):
        # Shear Force
        if x < load_pos_a_m:
            shear_forces_arr[i] = R_A
        elif x == load_pos_a_m: 
             shear_forces_arr[i] = R_A # Value just to the left for array consistency
        else: # x > a
            shear_forces_arr[i] = R_A - load_P_N
        
        # Bending Moment
        if x <= load_pos_a_m:
            bending_moments_arr[i] = R_A * x
        else: # x > a
            bending_moments_arr[i] = R_A * x - load_P_N * (x - load_pos_a_m)

        # Deflection
        if E * I == 0:
            deflections_arr[i] = 0
        elif x <= load_pos_a_m:
            deflections_arr[i] = (load_P_N * b * x) / (6 * L * E * I) * (L**2 - b**2 - x**2)
        else: # x > a
            deflections_arr[i] = (load_P_N * load_pos_a_m * (L - x)) / (6 * L * E * I) * (L**2 - load_pos_a_m**2 - (L - x)**2)

    # Create SFD points for plotting, ensuring the jump is explicit
    sfd_plot_points = []
    for i, x_val in enumerate(x_coords):
        if x_val < load_pos_a_m:
            sfd_plot_points.append({"x": x_val, "v": R_A})
        elif x_val == load_pos_a_m:
            sfd_plot_points.append({"x": x_val, "v": R_A})  # Value just before/at load
            sfd_plot_points.append({"x": x_val, "v": R_A - load_P_N})  # Value just after load
        else: # x_val > load_pos_a_m
            sfd_plot_points.append({"x": x_val, "v": R_A - load_P_N})
    
    # Sort and remove duplicates, ensuring jump order
    unique_sfd_points = []
    seen_coords_for_jump_sfd = {} 
    for p in sfd_plot_points:
        coord = p['x']
        val = p['v']
        if coord == load_pos_a_m: # Handle jump point specially
            if coord not in seen_coords_for_jump_sfd:
                seen_coords_for_jump_sfd[coord] = set()
            if val not in seen_coords_for_jump_sfd[coord]:
                unique_sfd_points.append(p)
                seen_coords_for_jump_sfd[coord].add(val)
        else: # Standard duplicate check
            is_new = True
            for existing_p in unique_sfd_points:
                if existing_p['x'] == coord and existing_p['v'] == val:
                    is_new = False; break
            if is_new:
                unique_sfd_points.append(p)

    results["sfd_points"] = sorted(unique_sfd_points, key=lambda k: (k['x'], -k['v'] if k['x'] == load_pos_a_m and k['v'] == R_A else k['v']))
    results["bmd_points"] = [{"x": x, "m": m} for x, m in zip(x_coords, bending_moments_arr)]
    results["deflection_points"] = [{"x": x, "d": d} for x, d in zip(x_coords, deflections_arr)]

    # 3. Max/Min Values
    # Shear: directly from reactions for a single point load
    if load_P_N >= 0: # Assuming P positive downwards
        results["max_shear_N"] = R_A
        results["min_shear_N"] = R_A - load_P_N
    else: # Upward load
        results["max_shear_N"] = R_A - load_P_N # This will be more positive if P is negative
        results["min_shear_N"] = R_A          # This will be more negative if P is negative
    V_max_abs = max(abs(results["max_shear_N"]), abs(results["min_shear_N"]))

    # Moment: from calculated array for robustness
    results["max_moment_Nm"] = np.max(bending_moments_arr) if len(bending_moments_arr) > 0 else 0
    results["min_moment_Nm"] = np.min(bending_moments_arr) if len(bending_moments_arr) > 0 else 0
    
    results["max_deflection_m"] = np.max(deflections_arr) if len(deflections_arr) > 0 else 0
    results["min_deflection_m"] = np.min(deflections_arr) if len(deflections_arr) > 0 else 0


    # 4. Stresses
    # Max Bending Stress
    # Determine governing moment for stress (largest absolute value)
    M_gov_abs = max(abs(results["max_moment_Nm"]), abs(results["min_moment_Nm"]))
    M_gov = results["max_moment_Nm"] if abs(results["max_moment_Nm"]) >= abs(results["min_moment_Nm"]) else results["min_moment_Nm"]

    results["max_bending_stress_Pa"] = 0
    results["min_bending_stress_Pa"] = 0

    if M_gov_abs > 0: # Only calculate if there's a moment
        # Positive moment (M_gov > 0) => tension bottom (Z_bottom), compression top (Z_top)
        # Negative moment (M_gov < 0) => tension top (Z_top), compression bottom (Z_bottom)
        if M_gov > 0: # Sagging
            if Z_bottom > 0: results["max_bending_stress_Pa"] = M_gov / Z_bottom # Tension
            if Z_top > 0: results["min_bending_stress_Pa"] = -M_gov / Z_top    # Compression
        else: # Hogging (M_gov < 0)
            if Z_top > 0: results["max_bending_stress_Pa"] = -M_gov / Z_top     # Tension (M_gov is neg, Z_top is pos, -M/Z is pos)
            if Z_bottom > 0: results["min_bending_stress_Pa"] = M_gov / Z_bottom # Compression
    
    # Max Shear Stress
    cs = beam_element.cross_section
    tau_max_Pa = 0
    if cs.type_name == "Rectangular" and cs.area_m2 > 0:
        tau_max_Pa = 1.5 * V_max_abs / cs.area_m2
    elif cs.type_name == "Circular" and cs.area_m2 > 0:
        tau_max_Pa = (4/3) * V_max_abs / cs.area_m2
    elif I > 0 and cs.bx_at_Qx_max_m > 0 and hasattr(cs, 'Qx_max_m3') and cs.Qx_max_m3 is not None:
        tau_max_Pa = (V_max_abs * cs.Qx_max_m3) / (I * cs.bx_at_Qx_max_m)
    results["max_shear_stress_Pa"] = tau_max_Pa

    # 5. Failure Checks
    bending_stress_abs_max = max(abs(results.get("max_bending_stress_Pa",0)), abs(results.get("min_bending_stress_Pa",0)))
    bending_capacity_Pa = Fy
    bending_ratio = bending_stress_abs_max / bending_capacity_Pa if bending_capacity_Pa > 0 else float('inf')
    results["failure_checks"]["bending_yield"] = {
        "demand_Pa": bending_stress_abs_max,
        "capacity_Pa": bending_capacity_Pa,
        "ratio": bending_ratio,
        "status": "FAIL" if bending_ratio >= 1.0 else "PASS"
    }

    shear_capacity_Pa = Fsy
    shear_ratio = tau_max_Pa / shear_capacity_Pa if shear_capacity_Pa > 0 else float('inf')
    results["failure_checks"]["shear_yield"] = {
        "demand_Pa": tau_max_Pa,
        "capacity_Pa": shear_capacity_Pa,
        "ratio": shear_ratio,
        "status": "FAIL" if shear_ratio >= 1.0 else "PASS"
    }
    
    deflection_limit_span_ratio = getattr(beam_element.material, 'default_deflection_limit_beams_total_load_span_ratio', 300)
    deflection_limit_m = L / deflection_limit_span_ratio if deflection_limit_span_ratio > 0 else float('inf')
    max_abs_deflection = max(abs(results["max_deflection_m"]), abs(results["min_deflection_m"]))
    deflection_ratio = max_abs_deflection / deflection_limit_m if deflection_limit_m > 0 else 0
    results["failure_checks"]["deflection_limit"] = {
        "demand_m": max_abs_deflection,
        "limit_m": deflection_limit_m,
        "limit_description": f"L/{deflection_limit_span_ratio}",
        "ratio": deflection_ratio,
        "status": "FAIL" if deflection_ratio >= 1.0 else "PASS"
    }

    beam_element.results = results
    return results


def solve_cantilever_beam_point_load_end(beam_element, load_P_N):
    L = beam_element.length_m
    E = beam_element.material.E_Pa
    I = beam_element.cross_section.Ix_m4
    Fy = beam_element.material.Fy_Pa
    Fsy = beam_element.material.Fsy_Pa
    Z_top = beam_element.cross_section.Zx_top_m3
    Z_bottom = beam_element.cross_section.Zx_bottom_m3
    
    results = beam_element.results

    # 1. Reactions
    R_A_vertical = load_P_N
    M_A_moment = -load_P_N * L # Negative moment for positive P (tension top)
    results["reactions"] = {"R_A_vertical_N": R_A_vertical, "M_A_moment_Nm": M_A_moment}

    # 2. SFD, BMD, Deflection Points
    x_coords = generate_beam_points(L)
    # For cantilever end load, shear is constant V = P
    # Moment M(x) = -P(L-x). At x=0, M = -PL. At x=L, M=0.
    shear_forces_arr = np.full_like(x_coords, load_P_N)
    bending_moments_arr = np.array([M_A_moment + load_P_N * x for x in x_coords]) # Or -load_P_N * (L - x)
    
    deflections_arr = np.zeros_like(x_coords)
    if E * I > 0:
        for i, x in enumerate(x_coords):
            deflections_arr[i] = (load_P_N * x**2) / (6 * E * I) * (3 * L - x)

    results["sfd_points"] = [{"x": x, "v": v} for x, v in zip(x_coords, shear_forces_arr)]
    results["bmd_points"] = [{"x": x, "m": m} for x, m in zip(x_coords, bending_moments_arr)]
    results["deflection_points"] = [{"x": x, "d": d} for x, d in zip(x_coords, deflections_arr)]

    # 3. Max/Min Values
    results["max_shear_N"] = load_P_N if load_P_N >=0 else 0 # Shear is P if P is positive
    results["min_shear_N"] = load_P_N if load_P_N < 0 else 0  # Or just load_P_N and V_max_abs takes care of it
    V_max_abs = abs(load_P_N)

    # Max moment is 0 at free end, min moment is M_A_moment at fixed end for positive P
    results["max_moment_Nm"] = np.max(bending_moments_arr) # Should be 0 if P > 0
    results["min_moment_Nm"] = np.min(bending_moments_arr) # Should be M_A_moment if P > 0

    results["max_deflection_m"] = (load_P_N * L**3) / (3 * E * I) if E*I > 0 and load_P_N >=0 else 0 
    results["min_deflection_m"] = (load_P_N * L**3) / (3 * E * I) if E*I > 0 and load_P_N < 0 else 0 
    if load_P_N < 0: # Upward load, max deflection is negative
        results["max_deflection_m"], results["min_deflection_m"] = results["min_deflection_m"], results["max_deflection_m"]


    # 4. Stresses
    M_gov_abs = max(abs(results["max_moment_Nm"]), abs(results["min_moment_Nm"])) # abs(M_A_moment)
    M_gov = results["min_moment_Nm"] if abs(results["min_moment_Nm"]) >= abs(results["max_moment_Nm"]) else results["max_moment_Nm"]
    
    results["max_bending_stress_Pa"] = 0
    results["min_bending_stress_Pa"] = 0

    if M_gov_abs > 0:
        # For cantilever end load P (+ve down), M_gov = M_A_moment (-ve, hogging)
        # Tension top (-M_gov/Z_top), Compression bottom (M_gov/Z_bottom)
        if M_gov < 0: # Hogging (typical for cantilever with downward load at end)
            if Z_top > 0: results["max_bending_stress_Pa"] = -M_gov / Z_top      # Tension
            if Z_bottom > 0: results["min_bending_stress_Pa"] = M_gov / Z_bottom # Compression
        else: # Sagging (if load P was upwards)
            if Z_bottom > 0: results["max_bending_stress_Pa"] = M_gov / Z_bottom # Tension
            if Z_top > 0: results["min_bending_stress_Pa"] = -M_gov / Z_top     # Compression
    
    cs = beam_element.cross_section
    tau_max_Pa = 0
    if cs.type_name == "Rectangular" and cs.area_m2 > 0:
        tau_max_Pa = 1.5 * V_max_abs / cs.area_m2
    elif cs.type_name == "Circular" and cs.area_m2 > 0:
        tau_max_Pa = (4/3) * V_max_abs / cs.area_m2
    elif I > 0 and cs.bx_at_Qx_max_m > 0 and hasattr(cs, 'Qx_max_m3') and cs.Qx_max_m3 is not None:
        tau_max_Pa = (V_max_abs * cs.Qx_max_m3) / (I * cs.bx_at_Qx_max_m)
    results["max_shear_stress_Pa"] = tau_max_Pa

    # 5. Failure Checks
    bending_stress_abs_max = max(abs(results.get("max_bending_stress_Pa",0)), abs(results.get("min_bending_stress_Pa",0)))
    bending_capacity_Pa = Fy
    bending_ratio = bending_stress_abs_max / bending_capacity_Pa if bending_capacity_Pa > 0 else float('inf')
    results["failure_checks"]["bending_yield"] = {
        "demand_Pa": bending_stress_abs_max, "capacity_Pa": bending_capacity_Pa,
        "ratio": bending_ratio, "status": "FAIL" if bending_ratio >= 1.0 else "PASS"
    }

    shear_capacity_Pa = Fsy
    shear_ratio = tau_max_Pa / shear_capacity_Pa if shear_capacity_Pa > 0 else float('inf')
    results["failure_checks"]["shear_yield"] = {
        "demand_Pa": tau_max_Pa, "capacity_Pa": shear_capacity_Pa,
        "ratio": shear_ratio, "status": "FAIL" if shear_ratio >= 1.0 else "PASS"
    }
    
    deflection_limit_span_ratio = getattr(beam_element.material, 'default_deflection_limit_cantilever_total_load_span_ratio', 180)
    deflection_limit_m = L / deflection_limit_span_ratio if deflection_limit_span_ratio > 0 else float('inf')
    # Max deflection is positive downwards. If load is upwards, deflection is negative.
    max_abs_deflection = max(abs(results.get("max_deflection_m",0)), abs(results.get("min_deflection_m",0)))
    
    deflection_ratio = max_abs_deflection / deflection_limit_m if deflection_limit_m > 0 else 0
    results["failure_checks"]["deflection_limit"] = {
        "demand_m": max_abs_deflection, "limit_m": deflection_limit_m,
        "limit_description": f"L/{deflection_limit_span_ratio}",
        "ratio": deflection_ratio, "status": "FAIL" if deflection_ratio >= 1.0 else "PASS"
    }

    beam_element.results = results
    return results

def solve_simply_supported_beam_udl(beam_element, udl_w_N_per_m):
    """
    Solves a simply supported beam with a uniformly distributed load w.
    Args:
        beam_element (Beam): The beam object.
        udl_w_N_per_m (float): Magnitude of the UDL (positive downwards).
    Returns:
        dict: Updated beam_element.results
    """
    L = beam_element.length_m
    E = beam_element.material.E_Pa
    I = beam_element.cross_section.Ix_m4
    Fy = beam_element.material.Fy_Pa
    Fsy = beam_element.material.Fsy_Pa
    Z_top = beam_element.cross_section.Zx_top_m3
    Z_bottom = beam_element.cross_section.Zx_bottom_m3

    results = beam_element.results

    # 1. Reactions
    R_A = (udl_w_N_per_m * L) / 2
    R_B = R_A
    results["reactions"] = {"R_A_N": R_A, "R_B_N": R_B}

    # 2. SFD, BMD, Deflection
    x_coords = generate_beam_points(L)
    shear_forces_arr = np.zeros_like(x_coords)
    bending_moments_arr = np.zeros_like(x_coords)
    deflections_arr = np.zeros_like(x_coords)

    for i, x in enumerate(x_coords):
        shear_forces_arr[i] = R_A - udl_w_N_per_m * x
        bending_moments_arr[i] = R_A * x - (udl_w_N_per_m * x**2) / 2
        if E * I > 0:
            deflections_arr[i] = (udl_w_N_per_m * x) / (24 * E * I) * (L**3 - 2 * L * x**2 + x**3)
        else:
            deflections_arr[i] = 0
    
    results["sfd_points"] = [{"x": x, "v": v} for x, v in zip(x_coords, shear_forces_arr)]
    results["bmd_points"] = [{"x": x, "m": m} for x, m in zip(x_coords, bending_moments_arr)]
    results["deflection_points"] = [{"x": x, "d": d} for x, d in zip(x_coords, deflections_arr)]

    # 3. Max/Min Values
    results["max_shear_N"] = R_A if udl_w_N_per_m >=0 else -R_B # Max shear at support A for downward UDL
    results["min_shear_N"] = -R_B if udl_w_N_per_m >=0 else R_A # Min shear at support B for downward UDL
    V_max_abs = R_A # Max absolute shear is at supports = R_A = wL/2

    results["max_moment_Nm"] = (udl_w_N_per_m * L**2) / 8 if udl_w_N_per_m >=0 else 0 # At mid-span for downward UDL
    results["min_moment_Nm"] = 0 if udl_w_N_per_m >=0 else (udl_w_N_per_m * L**2) / 8

    results["max_deflection_m"] = (5 * udl_w_N_per_m * L**4) / (384 * E * I) if E*I>0 and udl_w_N_per_m >=0 else 0
    results["min_deflection_m"] = 0 if E*I>0 and udl_w_N_per_m >=0 else (5 * udl_w_N_per_m * L**4) / (384 * E * I)
    if udl_w_N_per_m < 0:
        results["max_deflection_m"], results["min_deflection_m"] = results["min_deflection_m"], results["max_deflection_m"]


    # 4. Stresses
    M_gov_abs = max(abs(results["max_moment_Nm"]), abs(results["min_moment_Nm"]))
    M_gov = results["max_moment_Nm"] if abs(results["max_moment_Nm"]) >= abs(results["min_moment_Nm"]) else results["min_moment_Nm"]

    results["max_bending_stress_Pa"] = 0
    results["min_bending_stress_Pa"] = 0
    if M_gov_abs > 0:
        if M_gov > 0: # Sagging
            if Z_bottom > 0: results["max_bending_stress_Pa"] = M_gov / Z_bottom
            if Z_top > 0: results["min_bending_stress_Pa"] = -M_gov / Z_top
        else: # Hogging
            if Z_top > 0: results["max_bending_stress_Pa"] = -M_gov / Z_top
            if Z_bottom > 0: results["min_bending_stress_Pa"] = M_gov / Z_bottom
    
    cs = beam_element.cross_section
    tau_max_Pa = 0
    if cs.type_name == "Rectangular" and cs.area_m2 > 0:
        tau_max_Pa = 1.5 * V_max_abs / cs.area_m2
    elif cs.type_name == "Circular" and cs.area_m2 > 0:
        tau_max_Pa = (4/3) * V_max_abs / cs.area_m2
    elif I > 0 and cs.bx_at_Qx_max_m > 0 and hasattr(cs, 'Qx_max_m3') and cs.Qx_max_m3 is not None:
         tau_max_Pa = (V_max_abs * cs.Qx_max_m3) / (I * cs.bx_at_Qx_max_m)
    results["max_shear_stress_Pa"] = tau_max_Pa
    
    # 5. Failure Checks
    bending_stress_abs_max = max(abs(results.get("max_bending_stress_Pa",0)), abs(results.get("min_bending_stress_Pa",0)))
    bending_capacity_Pa = Fy
    bending_ratio = bending_stress_abs_max / bending_capacity_Pa if bending_capacity_Pa > 0 else float('inf')
    results["failure_checks"]["bending_yield"] = {
        "demand_Pa": bending_stress_abs_max, "capacity_Pa": bending_capacity_Pa,
        "ratio": bending_ratio, "status": "FAIL" if bending_ratio >= 1.0 else "PASS"
    }
    shear_capacity_Pa = Fsy
    shear_ratio = tau_max_Pa / shear_capacity_Pa if shear_capacity_Pa > 0 else float('inf')
    results["failure_checks"]["shear_yield"] = {
        "demand_Pa": tau_max_Pa, "capacity_Pa": shear_capacity_Pa,
        "ratio": shear_ratio, "status": "FAIL" if shear_ratio >= 1.0 else "PASS"
    }
    deflection_limit_span_ratio = getattr(beam_element.material, 'default_deflection_limit_beams_total_load_span_ratio', 300)
    deflection_limit_m = L / deflection_limit_span_ratio if deflection_limit_span_ratio > 0 else float('inf')
    max_abs_deflection = max(abs(results.get("max_deflection_m",0)), abs(results.get("min_deflection_m",0)))
    deflection_ratio = max_abs_deflection / deflection_limit_m if deflection_limit_m > 0 else 0
    results["failure_checks"]["deflection_limit"] = {
        "demand_m": max_abs_deflection, "limit_m": deflection_limit_m,
        "limit_description": f"L/{deflection_limit_span_ratio}",
        "ratio": deflection_ratio, "status": "FAIL" if deflection_ratio >= 1.0 else "PASS"
    }

    beam_element.results = results
    return results

def solve_cantilever_beam_udl(beam_element, udl_w_N_per_m):
    """
    Solves a cantilever beam (fixed at x=0, free at x=L) with a UDL w.
    """
    L = beam_element.length_m
    E = beam_element.material.E_Pa
    I = beam_element.cross_section.Ix_m4
    Fy = beam_element.material.Fy_Pa
    Fsy = beam_element.material.Fsy_Pa
    Z_top = beam_element.cross_section.Zx_top_m3
    Z_bottom = beam_element.cross_section.Zx_bottom_m3
    
    results = beam_element.results

    # 1. Reactions
    R_A_vertical = udl_w_N_per_m * L
    M_A_moment = - (udl_w_N_per_m * L**2) / 2 
    results["reactions"] = {"R_A_vertical_N": R_A_vertical, "M_A_moment_Nm": M_A_moment}

    # 2. SFD, BMD, Deflection
    x_coords = generate_beam_points(L)
    shear_forces_arr = np.array([R_A_vertical - udl_w_N_per_m * x for x in x_coords]) 
    bending_moments_arr = np.array([M_A_moment + R_A_vertical * x - (udl_w_N_per_m * x**2) / 2 for x in x_coords])
    
    deflections_arr = np.zeros_like(x_coords)
    if E * I > 0:
        for i, x in enumerate(x_coords):
            deflections_arr[i] = (udl_w_N_per_m * x**2) / (24 * E * I) * (x**2 + 6 * L**2 - 4 * L * x)

    results["sfd_points"] = [{"x": x, "v": v} for x, v in zip(x_coords, shear_forces_arr)]
    results["bmd_points"] = [{"x": x, "m": m} for x, m in zip(x_coords, bending_moments_arr)]
    results["deflection_points"] = [{"x": x, "d": d} for x, d in zip(x_coords, deflections_arr)]

    # 3. Max/Min Values
    results["max_shear_N"] = R_A_vertical if udl_w_N_per_m >= 0 else 0
    results["min_shear_N"] = 0 if udl_w_N_per_m >= 0 else R_A_vertical 
    V_max_abs = abs(R_A_vertical)

    results["max_moment_Nm"] = 0 if udl_w_N_per_m >= 0 else abs(M_A_moment)
    results["min_moment_Nm"] = M_A_moment if udl_w_N_per_m >= 0 else 0 

    results["max_deflection_m"] = (udl_w_N_per_m * L**4) / (8 * E * I) if E * I > 0 and udl_w_N_per_m >=0 else 0
    results["min_deflection_m"] = 0 if E * I > 0 and udl_w_N_per_m >=0 else (udl_w_N_per_m * L**4) / (8 * E * I)
    if udl_w_N_per_m < 0:
        results["max_deflection_m"], results["min_deflection_m"] = results["min_deflection_m"], results["max_deflection_m"]

    # 4. Stresses
    M_gov_abs = max(abs(results["max_moment_Nm"]), abs(results["min_moment_Nm"]))
    M_gov = results["min_moment_Nm"] if abs(results["min_moment_Nm"]) >= abs(results["max_moment_Nm"]) else results["max_moment_Nm"]
    
    results["max_bending_stress_Pa"] = 0
    results["min_bending_stress_Pa"] = 0
    if M_gov_abs > 0:
        if M_gov < 0: # Hogging (typical for cantilever UDL down)
            if Z_top > 0: results["max_bending_stress_Pa"] = -M_gov / Z_top
            if Z_bottom > 0: results["min_bending_stress_Pa"] = M_gov / Z_bottom
        else: # Sagging (UDL up)
            if Z_bottom > 0: results["max_bending_stress_Pa"] = M_gov / Z_bottom
            if Z_top > 0: results["min_bending_stress_Pa"] = -M_gov / Z_top
    
    cs = beam_element.cross_section
    tau_max_Pa = 0
    if cs.type_name == "Rectangular" and cs.area_m2 > 0:
        tau_max_Pa = 1.5 * V_max_abs / cs.area_m2
    elif cs.type_name == "Circular" and cs.area_m2 > 0:
        tau_max_Pa = (4/3) * V_max_abs / cs.area_m2
    elif I > 0 and cs.bx_at_Qx_max_m > 0 and hasattr(cs, 'Qx_max_m3') and cs.Qx_max_m3 is not None:
        tau_max_Pa = (V_max_abs * cs.Qx_max_m3) / (I * cs.bx_at_Qx_max_m)
    results["max_shear_stress_Pa"] = tau_max_Pa

    # 5. Failure Checks
    bending_stress_abs_max = max(abs(results.get("max_bending_stress_Pa",0)), abs(results.get("min_bending_stress_Pa",0)))
    bending_capacity_Pa = Fy
    bending_ratio = bending_stress_abs_max / bending_capacity_Pa if bending_capacity_Pa > 0 else float('inf')
    results["failure_checks"]["bending_yield"] = {
        "demand_Pa": bending_stress_abs_max, "capacity_Pa": bending_capacity_Pa,
        "ratio": bending_ratio, "status": "FAIL" if bending_ratio >= 1.0 else "PASS"
    }

    shear_capacity_Pa = Fsy
    shear_ratio = tau_max_Pa / shear_capacity_Pa if shear_capacity_Pa > 0 else float('inf')
    results["failure_checks"]["shear_yield"] = {
        "demand_Pa": tau_max_Pa, "capacity_Pa": shear_capacity_Pa,
        "ratio": shear_ratio, "status": "FAIL" if shear_ratio >= 1.0 else "PASS"
    }
    
    deflection_limit_span_ratio = getattr(beam_element.material, 'default_deflection_limit_cantilever_total_load_span_ratio', 180)
    deflection_limit_m = L / deflection_limit_span_ratio if deflection_limit_span_ratio > 0 else float('inf')
    max_abs_deflection = max(abs(results.get("max_deflection_m",0)), abs(results.get("min_deflection_m",0)))
    deflection_ratio = max_abs_deflection / deflection_limit_m if deflection_limit_m > 0 else 0
    results["failure_checks"]["deflection_limit"] = {
        "demand_m": max_abs_deflection, "limit_m": deflection_limit_m,
        "limit_description": f"L/{deflection_limit_span_ratio}",
        "ratio": deflection_ratio, "status": "FAIL" if deflection_ratio >= 1.0 else "PASS"
    }

    beam_element.results = results
    return results