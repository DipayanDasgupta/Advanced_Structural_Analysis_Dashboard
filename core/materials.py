# core/materials.py
import math

class Material:
    def __init__(self, name, youngs_modulus_E_GPa, yield_strength_MPa, poissons_ratio=0.3, density_kg_m3=7850):
        self.name = name
        self.E_Pa = youngs_modulus_E_GPa * 1e9  # Young's Modulus in Pa (N/m^2)
        self.Fy_Pa = yield_strength_MPa * 1e6  # Yield Strength in Pa (N/m^2)
        self.poissons_ratio = poissons_ratio
        # Shear Modulus G = E / (2 * (1 + v))
        self.G_Pa = self.E_Pa / (2 * (1 + self.poissons_ratio))
        self.density_kg_m3 = density_kg_m3
        # Approximate ultimate tensile strength (can be refined)
        self.Fu_Pa = self.Fy_Pa * 1.2 # General approximation for steel
        # Approximate shear yield strength (Von Mises criterion)
        self.Fsy_Pa = self.Fy_Pa / math.sqrt(3)


# Predefined materials dictionary
MATERIALS_LIB = {
    "steel_generic_s275": Material(
        name="Generic S275 Steel",
        youngs_modulus_E_GPa=200,
        yield_strength_MPa=275,
        poissons_ratio=0.3,
        density_kg_m3=7850
    ),
    "steel_generic_s355": Material(
        name="Generic S355 Steel",
        youngs_modulus_E_GPa=200,
        yield_strength_MPa=355,
        poissons_ratio=0.3,
        density_kg_m3=7850
    ),
    "aluminum_6061_t6": Material(
        name="Aluminum 6061-T6",
        youngs_modulus_E_GPa=69,
        yield_strength_MPa=276,
        poissons_ratio=0.33,
        density_kg_m3=2700
    ),
    "wood_douglas_fir": Material( # Properties highly variable, illustrative
        name="Wood (Douglas Fir, No.1/2)",
        youngs_modulus_E_GPa=11, # Average E
        yield_strength_MPa=30,   # Bending strength Fb, treat as pseudo-yield
        poissons_ratio=0.37, # Approx
        density_kg_m3=530
    ),
}

def get_material(name="steel_generic_s275"):
    return MATERIALS_LIB.get(name, MATERIALS_LIB["steel_generic_s275"])