"""WindIO_to_OpenSG: convert a windIO v2 wind-turbine blade into OpenSG cross-section inputs.

For any spanwise station it emits an OpenSG 1D-shell SG YAML (for the JAX MSG shell homogenizers
RM / Kirchhoff) and a PreVABS XML (-> prevabs.exe -> .sg -> 2D-solid SG YAML for the FEniCS solid /
VABS reference).
"""
from .converter import (
    WindIOBlade,
    build_cross_section,
    emit_opensg_yaml,
    emit_prevabs,
    interp,
    arc_param,
)

__all__ = ["WindIOBlade", "build_cross_section", "emit_opensg_yaml", "emit_prevabs", "interp", "arc_param"]
__version__ = "0.1.0"
