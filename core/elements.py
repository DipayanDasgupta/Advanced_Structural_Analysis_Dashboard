# core/elements.py
from .materials import get_material
from .cross_sections import create_cross_section

class StructuralElement:
    def __init__(self, length_m, material_name, section_type, section_params_mm):
        self.length_m = float(length_m)
        self.material = get_material(material_name)
        self.cross_section = create_cross_section(section_type, section_params_mm)
        self.loads = [] # List to store loads (type, magnitude, position)
        self.results = {} # To store calculation results

    def add_load(self, load_type, magnitude_N, position_m=None, start_m=None, end_m=None):
        self.loads.append({
            "type": load_type, # e.g., "point_load_Fy", "udl_Fy", "axial_load_Fx"
            "magnitude_N": float(magnitude_N),
            "position_m": float(position_m) if position_m is not None else None,
            "start_m": float(start_m) if start_m is not None else None,
            "end_m": float(end_m) if end_m is not None else None,
        })
    
    def clear_loads(self):
        self.loads = []

    def get_element_info(self):
        return {
            "length_m": self.length_m,
            "material": self.material.__dict__,
            "cross_section": self.cross_section.get_properties_dict(),
            "loads": self.loads
        }


class Beam(StructuralElement):
    def __init__(self, length_m, material_name, section_type, section_params_mm, support_type):
        super().__init__(length_m, material_name, section_type, section_params_mm)
        self.support_type = support_type # e.g., "simply_supported", "cantilever_left_fixed"
        self.results = { # Initialize results structure for beams
            "reactions": {},
            "sfd_points": [], "bmd_points": [], "deflection_points": [],
            "max_shear_N": 0, "min_shear_N": 0,
            "max_moment_Nm": 0, "min_moment_Nm": 0,
            "max_deflection_m": 0, "min_deflection_m": 0,
            "max_bending_stress_Pa": 0, "min_bending_stress_Pa": 0,
            "max_shear_stress_Pa": 0,
            "failure_checks": {}
        }


# core/elements.py

# ... (other imports and classes like StructuralElement, Beam) ...

class Column(StructuralElement):
    def __init__(self, length_m, material_name, section_type, section_params_mm, effective_length_factor_Kx, effective_length_factor_Ky):
        super().__init__(length_m, material_name, section_type, section_params_mm)
        self.Kx = float(effective_length_factor_Kx) # Effective length factor for buckling about x-axis
        self.Ky = float(effective_length_factor_Ky) # Effective length factor for buckling about y-axis
        self.results = { # Initialize results structure for columns
            "axial_stress_Pa": 0,
            "critical_buckling_load_Pcr_x_N": 0,
            "critical_buckling_load_Pcr_y_N": 0,
            "critical_buckling_stress_Fcr_x_Pa": 0,
            "critical_buckling_stress_Fcr_y_Pa": 0,
            "min_critical_buckling_load_N": 0,
            "failure_checks": {}
        }

    def get_element_info(self): # <<<< ADD THIS METHOD TO OVERRIDE THE BASE CLASS
        """Returns a dictionary with the column's properties, including Kx and Ky."""
        info = super().get_element_info() # Get common properties from base class
        info['Kx'] = self.Kx
        info['Ky'] = self.Ky
        return info
    def __init__(self, length_m, material_name, section_type, section_params_mm, effective_length_factor_Kx, effective_length_factor_Ky):
        super().__init__(length_m, material_name, section_type, section_params_mm)
        self.Kx = float(effective_length_factor_Kx) # Effective length factor for buckling about x-axis
        self.Ky = float(effective_length_factor_Ky) # Effective length factor for buckling about y-axis
        self.results = { # Initialize results structure for columns
            "axial_stress_Pa": 0,
            "critical_buckling_load_Pcr_x_N": 0,
            "critical_buckling_load_Pcr_y_N": 0,
            "critical_buckling_stress_Fcr_x_Pa": 0,
            "critical_buckling_stress_Fcr_y_Pa": 0,
            "min_critical_buckling_load_N": 0,
            "failure_checks": {}
        }