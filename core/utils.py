# core/utils.py
import numpy as np

def generate_beam_points(length, num_points=201):
    """Generates x-coordinates along the beam."""
    return np.linspace(0, length, num_points)

# More utilities can be added here, e.g., for numerical integration if needed later
# for complex load cases or deflection calculations.

def get_color_for_value(value, min_val, max_val, colormap_name="viridis_r"):
    """
    Maps a value to a color in a reversed Viridis-like colormap (hot is high).
    Adjust min_val and max_val carefully. If max_val is 0 (e.g. no moment), default to blue.
    If value is outside range, cap it.
    """
    if max_val == min_val: # Avoid division by zero if all values are same
        norm_value = 0.5
    else:
        norm_value = (value - min_val) / (max_val - min_val)
    
    norm_value = max(0, min(1, norm_value)) # Clamp between 0 and 1

    # Simple reversed Viridis-like: Blue -> Green -> Yellow -> Red (as norm_value goes 0 to 1)
    # This is a simplified version. For true Viridis, you'd use more points.
    r, g, b = 0, 0, 0
    if norm_value < 0.25: # Blue to Cyan
        r = 0
        g = int(255 * (norm_value / 0.25))
        b = 255
    elif norm_value < 0.5: # Cyan to Green
        r = 0
        g = 255
        b = int(255 * (1 - (norm_value - 0.25) / 0.25))
    elif norm_value < 0.75: # Green to Yellow
        r = int(255 * ((norm_value - 0.5) / 0.25))
        g = 255
        b = 0
    else: # Yellow to Red
        r = 255
        g = int(255 * (1 - (norm_value - 0.75) / 0.25))
        b = 0
    
    return f"rgb({r},{g},{b})"