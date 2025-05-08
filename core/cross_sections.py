# core/cross_sections.py
import math

class CrossSection:
    def __init__(self, type_name):
        self.type_name = type_name
        self.area_m2 = 0.0
        self.Ix_m4 = 0.0  # Moment of inertia about strong axis (typically x-x for bending in y-direction)
        self.Iy_m4 = 0.0  # Moment of inertia about weak axis (typically y-y for bending in x-direction)
        
        self.Zx_top_m3 = 0.0    # Section modulus for strong axis bending, top fiber
        self.Zx_bottom_m3 = 0.0 # Section modulus for strong axis bending, bottom fiber
        self.Zy_left_m3 = 0.0   # Section modulus for weak axis bending, left fiber
        self.Zy_right_m3 = 0.0  # Section modulus for weak axis bending, right fiber

        self.cy_top_m = 0.0      # Distance from neutral axis to top fiber
        self.cy_bottom_m = 0.0   # Distance from neutral axis to bottom fiber
        self.cx_left_m = 0.0     # Distance from neutral axis to left fiber
        self.cx_right_m = 0.0    # Distance from neutral axis to right fiber

        # For shear stress: tau = VQ / (Ib)
        self.Qx_max_m3 = 0.0  # Max first moment of area for shear force in y-dir (V_y)
        self.bx_at_Qx_max_m = 0.0 # Width b for shear V_y at location of Qx_max (usually NA)
        
        self.Qy_max_m3 = 0.0  # Max first moment of area for shear force in x-dir (V_x)
        self.by_at_Qy_max_m = 0.0 # Width b for shear V_x at location of Qy_max

        self.rx_m = 0.0 # Radius of gyration about x-axis
        self.ry_m = 0.0 # Radius of gyration about y-axis

    def _calculate_properties(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def get_properties_dict(self):
        return {
            "type": self.type_name,
            "area_m2": self.area_m2,
            "Ix_m4": self.Ix_m4, "Iy_m4": self.Iy_m4,
            "Zx_top_m3": self.Zx_top_m3, "Zx_bottom_m3": self.Zx_bottom_m3,
            "Zy_left_m3": self.Zy_left_m3, "Zy_right_m3": self.Zy_right_m3,
            "cy_top_m": self.cy_top_m, "cy_bottom_m": self.cy_bottom_m,
            "cx_left_m": self.cx_left_m, "cx_right_m": self.cx_right_m,
            "Qx_max_m3": self.Qx_max_m3, "bx_at_Qx_max_m": self.bx_at_Qx_max_m,
            "Qy_max_m3": self.Qy_max_m3, "by_at_Qy_max_m": self.by_at_Qy_max_m,
            "rx_m": self.rx_m, "ry_m": self.ry_m,
        }


class RectangularSection(CrossSection):
    def __init__(self, width_mm, height_mm): # width is b, height is h
        super().__init__("Rectangular")
        self.b_m = width_mm / 1000.0
        self.h_m = height_mm / 1000.0
        self._calculate_properties()

    def _calculate_properties(self):
        self.area_m2 = self.b_m * self.h_m
        
        # Strong axis bending (about x-x, horizontal axis through centroid)
        self.Ix_m4 = (self.b_m * self.h_m**3) / 12
        self.cy_top_m = self.h_m / 2.0
        self.cy_bottom_m = self.h_m / 2.0
        self.Zx_top_m3 = self.Ix_m4 / self.cy_top_m
        self.Zx_bottom_m3 = self.Ix_m4 / self.cy_bottom_m
        self.Qx_max_m3 = self.b_m * (self.h_m / 2.0) * (self.h_m / 4.0) # A_half * y_bar_half
        self.bx_at_Qx_max_m = self.b_m

        # Weak axis bending (about y-y, vertical axis through centroid)
        self.Iy_m4 = (self.h_m * self.b_m**3) / 12
        self.cx_left_m = self.b_m / 2.0
        self.cx_right_m = self.b_m / 2.0
        self.Zy_left_m3 = self.Iy_m4 / self.cx_left_m
        self.Zy_right_m3 = self.Iy_m4 / self.cx_right_m
        self.Qy_max_m3 = self.h_m * (self.b_m / 2.0) * (self.b_m / 4.0)
        self.by_at_Qy_max_m = self.h_m
        
        if self.area_m2 > 0:
            self.rx_m = math.sqrt(self.Ix_m4 / self.area_m2)
            self.ry_m = math.sqrt(self.Iy_m4 / self.area_m2)

class CircularSection(CrossSection):
    def __init__(self, diameter_mm):
        super().__init__("Circular")
        self.d_m = diameter_mm / 1000.0
        self.r_m = self.d_m / 2.0
        self._calculate_properties()

    def _calculate_properties(self):
        self.area_m2 = math.pi * self.r_m**2
        
        self.Ix_m4 = (math.pi * self.r_m**4) / 4
        self.Iy_m4 = self.Ix_m4 # Symmetric
        
        self.cy_top_m = self.r_m
        self.cy_bottom_m = self.r_m
        self.cx_left_m = self.r_m
        self.cx_right_m = self.r_m

        self.Zx_top_m3 = self.Ix_m4 / self.r_m
        self.Zx_bottom_m3 = self.Zx_top_m3
        self.Zy_left_m3 = self.Iy_m4 / self.r_m
        self.Zy_right_m3 = self.Zy_left_m3

        # For solid circular section, Q_max = (2/3)*r^3 for shear at NA
        self.Qx_max_m3 = (2/3) * self.r_m**3
        self.bx_at_Qx_max_m = self.d_m # width at NA is diameter
        self.Qy_max_m3 = self.Qx_max_m3
        self.by_at_Qy_max_m = self.d_m
        
        if self.area_m2 > 0:
            self.rx_m = math.sqrt(self.Ix_m4 / self.area_m2) # r_g = r/2 for solid circle
            self.ry_m = self.rx_m

# Factory function
def create_cross_section(type_name, params_mm):
    if type_name == "rectangular":
        # params_mm = [width, height]
        return RectangularSection(params_mm[0], params_mm[1])
    elif type_name == "circular":
        # params_mm = [diameter]
        return CircularSection(params_mm[0])
    # Add I-beam, Hollow sections etc. later
    # elif type_name == "i_beam_metric":
    #     # params_mm = [height_d, width_bf, flange_thick_tf, web_thick_tw]
    #     return IBeamMetricSection(params_mm[0], params_mm[1], params_mm[2], params_mm[3])
    else:
        raise ValueError(f"Unknown cross-section type: {type_name}")