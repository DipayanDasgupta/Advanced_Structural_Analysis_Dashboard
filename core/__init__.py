# This makes it easier to import from the 'core' package
from .materials import Material, MATERIALS_LIB, get_material
from .cross_sections import CrossSection, RectangularSection, CircularSection, create_cross_section # Add IBeamSection when created
from .elements import StructuralElement, Beam, Column
from .beam_solvers import (
    solve_simply_supported_beam_point_load,
    solve_cantilever_beam_point_load_end,
    solve_simply_supported_beam_udl,  # Added
    solve_cantilever_beam_udl         # Added
)
from .column_solvers import solve_column_axial_buckling
from .utils import generate_beam_points, get_color_for_value