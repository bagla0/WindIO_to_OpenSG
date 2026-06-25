"""WindIO_to_OpenSG: convert a windIO wind-turbine blade into OpenSG cross-section inputs.

Version-agnostic: load_blade() reads windIO v2 (outer_shape / structure, e.g. IEA-22-280-RWT) AND
v1 (outer_shape_bem / internal_structure_2d_fem, e.g. the NREL BAR designs). For any spanwise station
it emits an OpenSG 1D-shell SG YAML (for the JAX MSG shell homogenizers RM / Kirchhoff) and a PreVABS
XML (-> prevabs -> .sg -> 2D-solid SG YAML for the FEniCS solid / VABS reference).

openfast_io bridges OpenFAST: read ElastoDyn/BeamDyn blade data as a validation reference, and write
BeamDyn blade files from the homogenized 6x6 to drive an OpenFAST aeroelastic run.
"""
from .converter import (
    WindIOBlade,
    WindIOBladeV1,
    load_blade,
    build_cross_section,
    emit_opensg_yaml,
    emit_prevabs,
    interp,
    arc_param,
)
from .openfast_io import (
    read_elastodyn_blade,
    elastodyn_at,
    read_beamdyn_blade,
    beamdyn_to_timo,
    timo_to_beamdyn,
    write_beamdyn_blade,
)

__all__ = [
    "WindIOBlade", "WindIOBladeV1", "load_blade", "build_cross_section",
    "emit_opensg_yaml", "emit_prevabs", "interp", "arc_param",
    "read_elastodyn_blade", "elastodyn_at", "read_beamdyn_blade",
    "beamdyn_to_timo", "timo_to_beamdyn", "write_beamdyn_blade",
]
__version__ = "0.2.0"
