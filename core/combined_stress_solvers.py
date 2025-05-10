# core/combined_stress_solvers.py
import math
from .utils import format_value, format_formula
from .column_solvers import solve_column_axial_buckling # Import to get Pcr calculation
from .torsion_solvers import solve_torsion # Import to get torsional stress/angle

def solve_beam_column(element):
    """
    Solves a beam-column element under combined axial load, bending moments, and torsion.
    Provides basic stress calculations and a simplified interaction check.
    Args:
        element (BeamColumn): The beam-column object with total_loads set.
    Returns:
        tuple: (results_dict, calculation_log_list)
    """
    L = element.length_m
    E = element.material.E_Pa
    G = element.material.G_Pa # Needed for torsion
    Fy = element.material.Fy_Pa
    Fsy = element.material.Fsy_Pa # Needed for shear checks
    A = element.cross_section.area_m2
    Ix = element.cross_section.Ix_m4 # For bending Mz
    Iy = element.cross_section.Iy_m4 # For bending My
    J = element.cross_section.J_m4 # For torsion
    Zt = element.cross_section.Z_torsion_m3 # For torsional shear stress
    Zx_top = element.cross_section.Zx_top_m3    # For bending Mz
    Zx_bottom = element.cross_section.Zx_bottom_m3 # For bending Mz
    Zy_left = element.cross_section.Zy_left_m3   # For bending My
    Zy_right = element.cross_section.Zy_right_m3 # For bending My
    Kx = element.Kx # For buckling Mz (about X-X axis)
    Ky = element.Ky # For buckling My (about Y-Y axis)

    P_applied = element.total_axial_load_N # Positive for compression
    My_applied = element.total_bending_moment_My_Nm # Bending about Y-Y axis
    Mz_applied = element.total_bending_moment_Mz_Nm # Bending about Z-Z axis
    T_applied = element.total_torsional_moment_Mx_Nm # Torsion about X-X axis (longitudinal)


    results = {} # Reset results
    log = [] # Initialize calculation log

    log.append({"title": "Beam-Column Combined Stress Analysis", "notes": "Analysis of an element under combined axial, bending, and torsional loads."})
    log.append({"title": "Inputs", "notes": f"Length (L) = {format_value(L, 'm')}, Material E = {format_value(E, 'Pa')}, G = {format_value(G, 'Pa')}, Fy = {format_value(Fy, 'Pa')}, Fsy = {format_value(Fsy, 'Pa')}, Area = {format_value(A, 'm²')}, Ix = {format_value(Ix, 'm⁴')}, Iy = {format_value(Iy, 'm⁴')}, J/K = {format_value(J, 'm⁴')}, Zx_top = {format_value(Zx_top, 'm³')}, Zx_bottom = {format_value(Zx_bottom, 'm³')}, Zy_left = {format_value(Zy_left, 'm³')}, Zy_right = {format_value(Zy_right, 'm³')}, Z_torsion = {format_value(Zt, 'm³')}, Kx = {format_value(Kx)}, Ky = {format_value(Ky)}, Applied Loads: P = {format_value(P_applied, 'N')}, My = {format_value(My_applied, 'Nm')}, Mz = {format_value(Mz_applied, 'Nm')}, T = {format_value(T_applied, 'Nm')}"})

    # Basic input validation warnings
    if A <= 0: log.append({"title": "", "notes": "Warning: Section Area is zero or negative. Axial stress and buckling calculations may be invalid."})
    if E <= 0: log.append({"title": "", "notes": "Warning: Material Elastic Modulus (E) is zero or negative. Bending/Buckling calculations may be invalid."})
    if G <= 0: log.append({"title": "", "notes": "Warning: Material Shear Modulus (G) is zero or negative. Torsion calculations may be invalid."})
    if Fy <= 0: log.append({"title": "", "notes": "Warning: Material Yield Strength (Fy) is zero or negative. Yield checks may be invalid."})
    if Fsy <= 0: log.append({"title": "", "notes": "Warning: Material Shear Yield Strength (Fsy) is zero or negative. Shear yield checks may be invalid."})
    if Ix <= 0 or (Zx_top <= 0 or Zx_bottom <= 0): log.append({"title": "", "notes": "Warning: Section Ix or Zx is zero or negative. Bending stress (Mz) calculations may be invalid."})
    if Iy <= 0 or (Zy_left <= 0 or Zy_right <= 0): log.append({"title": "", "notes": "Warning: Section Iy or Zy is zero or negative. Bending stress (My) calculations may be invalid."})
    if J <= 0: log.append({"title": "", "notes": "Warning: Section Torsional Constant (J/K) is zero or negative. Torsion calculations may be invalid."})
    if Zt <= 0: log.append({"title": "", "notes": "Warning: Section Torsional Section Modulus (Z_torsion) is zero or negative. Torsional shear stress calculations may be invalid."})
    if L <= 0: log.append({"title": "", "notes": "Warning: Element Length is zero or negative. Buckling calculations may be invalid."})


    # --- Stress Calculations ---
    log.append({"title": "Calculate Stress Components"})

    # 1. Axial Stress (σ_axial)
    sigma_axial_Pa = 0
    if A > 0:
        sigma_axial_Pa = P_applied / A
        log.append({"title": "Axial Stress", "formula": "σ_axial = P / A", "calculation": format_formula("P / A", {"P": P_applied, "A": A}), "result": format_value(sigma_axial_Pa/1e6, "MPa"), "notes": "Uniform stress (compression positive) over cross-section."})
    else:
         log.append({"title": "Axial Stress", "notes": "Area is zero, axial stress is infinite (or zero if P=0).", "result": format_value(sigma_axial_Pa/1e6, "MPa")})
    results["axial_stress_Pa"] = sigma_axial_Pa


    # 2. Bending Stress (σ_bending)
    # Bending about Y-Y (moment My) causes normal stress in Z direction. max/min stress at +/- cx_right, +/- cx_left
    # Bending about Z-Z (moment Mz) causes normal stress in Y direction. max/min stress at +/- cy_top, +/- cy_bottom
    # Total bending stress is sum of stresses from My and Mz.
    # We need to consider all 4 corners (or extreme fibers for non-rectangular) for max/min total normal stress.

    sigma_bending_My_at_left_Pa = 0
    sigma_bending_My_at_right_Pa = 0
    sigma_bending_Mz_at_top_Pa = 0
    sigma_bending_Mz_at_bottom_Pa = 0

    log.append({"title": "Bending Stress"})
    if My_applied != 0:
        log.append({"title": "Bending Stress (due to My about Y-Y)", "notes": "Causes stress varying with Z coordinate."})
        if Zy_left > 0: sigma_bending_My_at_left_Pa = -My_applied / Zy_left # Tension if My > 0
        if Zy_right > 0: sigma_bending_My_at_right_Pa = My_applied / Zy_right # Compression if My > 0
        log.append({"title": "", "formula": "σ_My_left = -My / Zy_left", "calculation": format_formula("-My / Zy_left", {"My": My_applied, "Zy_left": Zy_left}), "result": format_value(sigma_bending_My_at_left_Pa/1e6, "MPa")})
        log.append({"title": "", "formula": "σ_My_right = My / Zy_right", "calculation": format_formula("My / Zy_right", {"My": My_applied, "Zy_right": Zy_right}), "result": format_value(sigma_bending_My_at_right_Pa/1e6, "MPa")})
        if Zy_left <= 0 or Zy_right <= 0: log.append({"title": "", "notes": "Zy is zero, My bending stress cannot be calculated."})
    elif My_applied == 0:
        log.append({"title": "Bending Stress (due to My about Y-Y)", "notes": "Applied moment My is zero, bending stress is zero.", "result": format_value(0, "MPa")})


    if Mz_applied != 0:
        log.append({"title": "Bending Stress (due to Mz about Z-Z)", "notes": "Causes stress varying with Y coordinate."})
        if Zx_top > 0: sigma_bending_Mz_at_top_Pa = -Mz_applied / Zx_top # Tension if Mz > 0
        if Zx_bottom > 0: sigma_bending_Mz_at_bottom_Pa = Mz_applied / Zx_bottom # Compression if Mz > 0
        log.append({"title": "", "formula": "σ_Mz_top = -Mz / Zx_top", "calculation": format_formula("-Mz / Zx_top", {"Mz": Mz_applied, "Zx_top": Zx_top}), "result": format_value(sigma_bending_Mz_at_top_Pa/1e6, "MPa")})
        log.append({"title": "", "formula": "σ_Mz_bottom = Mz / Zx_bottom", "calculation": format_formula("Mz / Zx_bottom", {"Mz": Mz_applied, "Zx_bottom": Zx_bottom}), "result": format_value(sigma_bending_Mz_at_bottom_Pa/1e6, "MPa")})
        if Zx_top <= 0 or Zx_bottom <= 0: log.append({"title": "", "notes": "Zx is zero, Mz bending stress cannot be calculated."})
    elif Mz_applied == 0:
         log.append({"title": "Bending Stress (due to Mz about Z-Z)", "notes": "Applied moment Mz is zero, bending stress is zero.", "result": format_value(0, "MPa")})

    # Note: Max bending stress is the max of the absolute values from My and Mz combined depending on location.
    # For a rectangular section, max bending stress is at a corner.
    # For other shapes, it's at the furthest point from the respective neutral axis.
    # This simple solver calculates stress at extreme points for My (left/right) and Mz (top/bottom).
    # A full calculation requires iterating over critical points (like corners for rectangle).
    # Let's calculate stress at the 4 "corners" of a notional bounding box.
    # Corner 1 (Top, Right): σ_axial + σ_Mz_top + σ_My_right
    # Corner 2 (Top, Left): σ_axial + σ_Mz_top + σ_My_left
    # Corner 3 (Bottom, Right): σ_axial + σ_Mz_bottom + σ_My_right
    # Corner 4 (Bottom, Left): σ_axial + σ_Mz_bottom + σ_My_left

    sigma_total_c1_TR_Pa = sigma_axial_Pa + sigma_bending_Mz_at_top_Pa + sigma_bending_My_at_right_Pa
    sigma_total_c2_TL_Pa = sigma_axial_Pa + sigma_bending_Mz_at_top_Pa + sigma_bending_My_at_left_Pa
    sigma_total_c3_BR_Pa = sigma_axial_Pa + sigma_bending_Mz_at_bottom_Pa + sigma_bending_My_at_right_Pa
    sigma_total_c4_BL_Pa = sigma_axial_Pa + sigma_bending_Mz_at_bottom_Pa + sigma_bending_My_at_left_Pa

    all_total_sigmas = [sigma_total_c1_TR_Pa, sigma_total_c2_TL_Pa, sigma_total_c3_BR_Pa, sigma_total_c4_BL_Pa]

    results["max_bending_stress_My_Pa"] = max(sigma_bending_My_at_left_Pa, sigma_bending_My_at_right_Pa)
    results["min_bending_stress_My_Pa"] = min(sigma_bending_My_at_left_Pa, sigma_bending_My_at_right_Pa)
    results["max_bending_stress_Mz_Pa"] = max(sigma_bending_Mz_at_top_Pa, sigma_bending_Mz_at_bottom_Pa)
    results["min_bending_stress_Mz_Pa"] = min(sigma_bending_Mz_at_top_Pa, sigma_bending_Mz_at_bottom_Pa)


    # 3. Torsional Shear Stress (τ_torsion)
    log.append({"title": "Torsional Shear Stress"})
    tau_torsion_max_Pa = 0
    if T_applied != 0:
        if Zt > 0:
            tau_torsion_max_Pa = abs(T_applied) / Zt
            log.append({"title": "", "formula": "τ_torsion_max = |T| / Z_torsion", "calculation": format_formula("|T| / Z_torsion", {"|T|": abs(T_applied), "Z_torsion": Zt}), "result": format_value(tau_torsion_max_Pa/1e6, "MPa")})
            log.append({"title": "", "notes": "Maximum torsional shear stress occurs on the outer surface."})
        else:
            tau_torsion_max_Pa = float('inf')
            log.append({"title": "", "notes": "Z_torsion is zero, torsional shear stress is infinite (or zero if T=0).", "result": format_value(tau_torsion_max_Pa/1e6, "MPa")})
    else:
        log.append({"title": "", "notes": "Applied torsional moment T is zero, torsional shear stress is zero.", "result": format_value(0, "MPa")})
    results["max_torsional_shear_stress_Pa"] = tau_torsion_max_Pa


    # 4. Total Normal Stress (σ_total)
    # Max/Min of the 4 corner stresses calculated above.
    results["max_combined_normal_stress_Pa"] = max(all_total_sigmas)
    results["min_combined_normal_stress_Pa"] = min(all_total_sigmas)
    sigma_combined_normal_abs_max = max(abs(results["max_combined_normal_stress_Pa"]), abs(results["min_combined_normal_stress_Pa"]))

    log.append({"title": "Maximum/Minimum Total Normal Stress", "notes": "Maximum/Minimum of axial + bending (My + Mz) stress at the 4 bounding corners of the cross-section.",
                "result": f"σ_total_max = {format_value(results['max_combined_normal_stress_Pa']/1e6, 'MPa')}, σ_total_min = {format_value(results['min_combined_normal_stress_Pa']/1e6, 'MPa')}, |σ|_max = {format_value(sigma_combined_normal_abs_max/1e6, 'MPa')}"})


    # 5. Total Shear Stress (τ_total)
    # This is complex. Shear comes from transverse shear (Vy, Vz) AND torsion (Tx).
    # Max shear stress from Vy occurs at NA. Max shear stress from Vz occurs at NA.
    # Max shear stress from Torsion occurs on the outer surface.
    # These maximums don't necessarily occur at the same point on the cross-section.
    # A full analysis needs combining stresses at various points (like web-flange junctions, NA, outer surface).
    # For this simplified solver, we'll just list the max shear stresses from each source if they were acting alone.
    # The combination check (e.g., Von Mises) below will use a simplified approach or just check max normal and max shear separately.

    # This solver does NOT calculate Vy or Vz from applied loads. It assumes My, Mz, T, P are RESULTANTS.
    # Thus, it cannot calculate shear stress from V.
    # We will only include Torsional shear stress here for now.

    # log.append({"title": "Total Shear Stress", "notes": "Maximum shear stress from torsion. Shear from transverse loads (Vy, Vz) is NOT calculated in this solver."})
    # (Max torsional shear already calculated above)
    # tau_total_max_Pa = tau_torsion_max_Pa # Simplified: only including torsion for now

    results["max_combined_shear_stress_Pa"] = tau_torsion_max_Pa # Only torsional shear included here


    # --- Capacity & Interaction Checks ---
    log.append({"title": "Capacity & Interaction Checks"})

    # 1. Yield Check (using max/min total normal stress vs Fy)
    combined_normal_yield_ratio = sigma_combined_normal_abs_max / Fy if Fy > 0 else float('inf') if sigma_combined_normal_abs_max != 0 else 0
    results["failure_checks"] = {
        "combined_normal_yield": {
            "demand_Pa": sigma_combined_normal_abs_max,
            "capacity_Pa": Fy,
            "ratio": combined_normal_yield_ratio,
            "status": "FAIL" if combined_normal_yield_ratio >= 1.0 else ("N/A" if Fy <= 0 and sigma_combined_normal_abs_max != 0 else "PASS")
        }
    }
    log.append({"title": "Combined Normal Stress Yield", "formula": "Ratio = |σ_total|_max / F_y", "calculation": format_formula("|σ_total|_max / F_y", {"|σ_total|_max": sigma_combined_normal_abs_max, "F_y": Fy}), "result": format_value(combined_normal_yield_ratio), "status": results["failure_checks"]["combined_normal_yield"]["status"], "notes": "Checks if the maximum absolute total normal stress (axial + bending) exceeds yield."})


    # 2. Torsional Shear Yield Check
    torsional_shear_yield_ratio = tau_torsion_max_Pa / Fsy if Fsy > 0 else float('inf') if tau_torsion_max_Pa != 0 else 0
    results["failure_checks"]["torsional_shear_yield"] = {
        "demand_Pa": tau_torsion_max_Pa,
        "capacity_Pa": Fsy,
        "ratio": torsional_shear_yield_ratio,
        "status": "FAIL" if torsional_shear_yield_ratio >= 1.0 else ("N/A" if Fsy <= 0 and tau_torsion_max_Pa != 0 else "PASS")
    }
    log.append({"title": "Torsional Shear Yield", "formula": "Ratio = τ_torsion_max / F_sy", "calculation": format_formula("τ_torsion_max / F_sy", {"τ_torsion_max": tau_torsion_max_Pa, "F_sy": Fsy}), "result": format_value(torsional_shear_yield_ratio), "status": results["failure_checks"]["torsional_shear_yield"]["status"], "notes": "Checks if max torsional shear stress exceeds shear yield strength."})


    # 3. Interaction Check (Axial + Bending)
    # Simplified interaction check (Eurocode/AISC-like simplified form):
    # P / Pc + My / Mc_y + Mz / Mc_z <= 1.0 (for axial + bending)
    # Where Pc is compressive capacity (min of axial yield and buckling capacity, possibly reduced by interaction factors),
    # Mc_y is bending capacity about Y-Y, Mc_z is bending capacity about Z-Z.
    # This requires considering buckling capacity under combined loads (complex) or using simplified interaction formulas.
    # Let's use a basic linear interaction: |P|/Pcr_min + |My|/Myield_y + |Mz|/Myield_z <= 1.0

    log.append({"title": "Interaction Check (Simplified Axial + Bending + Torsion)"})

    # Get Pcr values using the Column solver logic
    # Create a temporary Column object to use the existing solver for Pcr calculation
    temp_column = type('TempColumn', (object,), { # Create a simple mock object
        'length_m': L,
        'material': element.material,
        'cross_section': element.cross_section,
        'Kx': Kx,
        'Ky': Ky,
        '_applied_axial_load_N': 1.0 # Dummy load, we only need Pcr values
    })()
    # Call the column solver to get Pcr values (and log them separately if desired, or extract)
    # We won't add the column solver log to this beam-column log to keep it focused.
    column_results, _ = solve_column_axial_buckling(temp_column) # Don't care about dummy results or log here

    Pcr_x_N = column_results.get("critical_buckling_load_Pcr_x_N", float('inf')) # Buckling about X-X (relevant for Mz)
    Pcr_y_N = column_results.get("critical_buckling_load_Pcr_y_N", float('inf')) # Buckling about Y-Y (relevant for My)
    Pcr_min_N = column_results.get("min_critical_buckling_load_N", float('inf')) # Overall buckling limit

    log.append({"title": "", "notes": f"Pcr,x = {format_value(Pcr_x_N/1000, 'kN')} (Buckling about X-X, related to Mz), Pcr,y = {format_value(Pcr_y_N/1000, 'kN')} (Buckling about Y-Y, related to My), Pcr,min = {format_value(Pcr_min_N/1000, 'kN')} (Minimum Pcr)"})


    # Get Bending Yield Capacities
    # Myield_y = Fy * Zy_min (capacity for bending My about Y-Y axis)
    # Myield_z = Fy * Zx_min (capacity for bending Mz about Z-Z axis)
    Zy_min = min(Zy_left, Zy_right) if Zy_left > 0 and Zy_right > 0 else max(Zy_left, Zy_right) if max(Zy_left, Zy_right) > 0 else 0
    Zx_min = min(Zx_top, Zx_bottom) if Zx_top > 0 and Zx_bottom > 0 else max(Zx_top, Zx_bottom) if max(Zx_top, Zx_bottom) > 0 else 0

    Myield_y_Nm = Fy * Zy_min if Fy > 0 and Zy_min > 0 else float('inf')
    Myield_z_Nm = Fy * Zx_min if Fy > 0 and Zx_min > 0 else float('inf') # Note: Myield_z uses Zx (for bending about Z-Z)

    log.append({"title": "", "notes": f"Myield (about Y-Y) = {format_value(Myield_y_Nm, 'Nm')}, Myield (about Z-Z) = {format_value(Myield_z_Nm, 'Nm')}"})


    # Torsional Yield Capacity
    Tyield_Nm = Fsy * Zt if Fsy > 0 and Zt > 0 else float('inf')
    log.append({"title": "", "notes": f"Tyield (about X-X) = {format_value(Tyield_Nm, 'Nm')}"})


    # Basic Interaction Check (Linear Sum of Ratios)
    # Often simplified as P/Pc + Mb/Mbc + Mt/Mt_cap <= 1
    # Using a simplified version: |P|/Pcr_min + |My|/Myield_y + |Mz|/Myield_z + |T|/Tyield <= 1

    interaction_ratio = 0.0
    axial_term = 0.0
    bending_My_term = 0.0
    bending_Mz_term = 0.0
    torsion_term = 0.0

    log.append({"title": "Simplified Interaction Equation", "formula": "|P| / Pcr,min + |My| / Myield,y + |Mz| / Myield,z + |T| / Tyield <= 1.0"})

    # Axial term
    if Pcr_min_N > 0: axial_term = abs(P_applied) / Pcr_min_N
    elif abs(P_applied) > 0: axial_term = float('inf')
    log.append({"title": "", "notes": f"Axial Term = |{format_value(P_applied, 'N')}| / {format_value(Pcr_min_N, 'N')} = {format_value(axial_term)}"})

    # Bending My term
    if Myield_y_Nm > 0: bending_My_term = abs(My_applied) / Myield_y_Nm
    elif abs(My_applied) > 0: bending_My_term = float('inf')
    log.append({"title": "", "notes": f"Bending My Term = |{format_value(My_applied, 'Nm')}| / {format_value(Myield_y_Nm, 'Nm')} = {format_value(bending_My_term)}"})

    # Bending Mz term
    if Myield_z_Nm > 0: bending_Mz_term = abs(Mz_applied) / Myield_z_Nm
    elif abs(Mz_applied) > 0: bending_Mz_term = float('inf')
    log.append({"title": "", "notes": f"Bending Mz Term = |{format_value(Mz_applied, 'Nm')}| / {format_value(Myield_z_Nm, 'Nm')} = {format_value(bending_Mz_term)}"})

    # Torsion Term
    if Tyield_Nm > 0: torsion_term = abs(T_applied) / Tyield_Nm
    elif abs(T_applied) > 0: torsion_term = float('inf')
    log.append({"title": "", "notes": f"Torsion Term = |{format_value(T_applied, 'Nm')}| / {format_value(Tyield_Nm, 'Nm')} = {format_value(torsion_term)}"})


    interaction_ratio = axial_term + bending_My_term + bending_Mz_term + torsion_term

    interaction_status = "FAIL" if interaction_ratio >= 1.0 else "PASS"
    if interaction_ratio == float('inf'): interaction_status = "FAIL (Infinite Ratio)"
    if interaction_ratio == 0 and (abs(P_applied) + abs(My_applied) + abs(Mz_applied) + abs(T_applied)) == 0:
        interaction_status = "N/A (No Load)" # Special case for zero load

    results["failure_checks"]["interaction_combined_stress"] = {
        "demand_P_N": P_applied,
        "capacity_Pcr_min_N": Pcr_min_N,
        "demand_My_Nm": My_applied,
        "capacity_Myield_y_Nm": Myield_y_Nm,
        "demand_Mz_Nm": Mz_applied,
        "capacity_Myield_z_Nm": Myield_z_Nm,
        "demand_T_Nm": T_applied,
        "capacity_Tyield_Nm": Tyield_Nm,
        "ratio": interaction_ratio,
        "status": interaction_status,
        "note": "Simplified linear interaction: |P|/Pcr_min + |My|/Myield,y + |Mz|/Myield,z + |T|/Tyield <= 1.0. Does NOT include second-order effects (P-delta), lateral-torsional buckling (LTB), shear interaction, or detailed code-specific factors."
    }

    log.append({"title": "Interaction Ratio", "result": format_value(interaction_ratio), "status": results["failure_checks"]["interaction_combined_stress"]["status"]})
    log.append({"title": "", "notes": results["failure_checks"]["interaction_combined_stress"]["note"]})


    element.results = results
    element.calculation_log = log
    return results, log