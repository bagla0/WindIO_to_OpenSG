"""OpenSG_io -- a wrapper that converts various cross-section inputs into OpenSG YAMLs (1D shell + 2D solid).

  python scripts/opensg_io.py <input> <outdir> [--solid] [--stations ...] [--name STEM]

Input type is auto-detected:
  *.yaml / *.yml  (windIO v1 or v2)  -> 1D-shell + (--solid) 2D-solid PER STATION (--stations / --nstations)
  *.xml           (PreVABS)          -> 1D-shell (reconstructed from the XML) + (--solid) 2D-solid (runs PreVABS)
  *.fst / BeamDyn / ElastoDyn (OpenFAST) -> reads the blade-data REFERENCE 6x6 / EI (OpenFAST carries no layup,
                                            so no SG can be built from it -- this is for validation, not input).

OpenSG_io does NOT run windIO or OpenFAST; it only READS their files to prepare OpenSG input.
"""
import os, sys, glob, argparse, platform, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
from opensg_io import load_blade, build_cross_section, emit_opensg_yaml, emit_prevabs
from opensg_io import prevabs_xml
from opensg_io.openfast_io import read_elastodyn_blade, read_beamdyn_blade, beamdyn_to_timo


def find_prevabs():
    exe = "prevabs.exe" if platform.system().lower().startswith("win") else "prevabs"
    hits = glob.glob(os.path.join(REPO, "third_party", "prevabs_bin", "**", exe), recursive=True)
    return sorted(hits)[-1] if hits else os.environ.get("PREVABS_EXE")


def detect(inp):
    low = os.path.basename(inp).lower()
    if low.endswith((".yaml", ".yml")):
        return "windio"
    if low.endswith(".xml"):
        return "prevabs"
    if low.endswith(".fst") or any(k in low for k in ("beamdyn", "elastodyn", "aerodyn")):
        return "openfast"
    return "windio"


def _run_solid_from_xml(pvdir, name, prevabs, outdir, solid_yaml):
    subprocess.run([prevabs, "-i", "%s.xml" % name, "--vabs", "--hm"], cwd=pvdir, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    convert = os.path.join(HERE, "convert_sg_to_yaml.py")
    subprocess.run([sys.executable, convert, os.path.join(pvdir, "%s.sg" % name), solid_yaml], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def handle_windio(inp, outdir, a, prevabs):
    name = a.name or os.path.splitext(os.path.basename(inp))[0]
    stations = a.stations or [round((i + 1) / (a.nstations + 1), 4) for i in range(a.nstations)]
    blade = load_blade(inp)
    print("[windIO %s] %s -> %d stations" % (type(blade).__name__, name, len(stations)), flush=True)
    for r in stations:
        tag = "r%03d" % round(r * 100)
        cs = build_cross_section(blade, r, mesh_size=a.shell_ms)
        emit_opensg_yaml(cs, os.path.join(outdir, "shell_%s_%s.yaml" % (name, tag)))
        msg = "  r=%.2f chord=%.3f shell OK" % (r, cs["chord"])
        if a.solid:
            pv = os.path.join(outdir, "prevabs_%s" % tag)
            emit_prevabs(cs, pv, name="%s_%s" % (name, tag), mesh_size=a.solid_ms)
            try:
                _run_solid_from_xml(pv, "%s_%s" % (name, tag), prevabs, outdir,
                                    os.path.join(outdir, "solid_%s_%s.yaml" % (name, tag)))
                msg += " + 2D-solid OK"
            except Exception as e:
                msg += " (solid FAILED: %s)" % repr(e)[:60]
        print(msg, flush=True)


def handle_prevabs(inp, outdir, a, prevabs):
    name = os.path.splitext(os.path.basename(inp))[0]
    shell = os.path.join(outdir, "shell_%s.yaml" % name)
    info = prevabs_xml.to_shell(inp, shell)
    print("[PreVABS XML] %s -> 1D shell %s (%d nodes, %d elems, %d sets)"
          % (name, shell, info["n_nodes"], info["n_elems"], info["n_sets"]), flush=True)
    if a.solid:
        solid = os.path.join(outdir, "solid_%s.yaml" % name)
        prevabs_xml.to_solid(inp, solid, prevabs)
        print("[PreVABS XML] %s -> 2D solid %s" % (name, solid), flush=True)


def handle_openfast(inp, outdir, a):
    print("[OpenFAST] %s -- OpenFAST carries no cross-section layup, so NO SG can be built from it." % inp)
    print("           Reading it as a blade-data REFERENCE (for validating OpenSG results):", flush=True)
    low = inp.lower()
    import numpy as np
    if "elastodyn" in low:
        ed = read_elastodyn_blade(inp)
        out = os.path.join(outdir, "ref_elastodyn.dat")
        np.savetxt(out, np.column_stack([ed["BlFract"], ed["FlpStff"], ed["EdgStff"], ed["BMassDen"]]),
                   header="BlFract  FlpStff(EI2)  EdgStff(EI3)  BMassDen", comments="# ")
        print("           -> %d stations (EI_flap, EI_edge, mass) -> %s" % (len(ed["BlFract"]), out))
    else:
        etas, Ks, Ms = read_beamdyn_blade(inp)
        rows = [np.concatenate([[etas[i]], np.diag(beamdyn_to_timo(Ks[i]))]) for i in range(len(etas))]
        out = os.path.join(outdir, "ref_beamdyn.dat")
        np.savetxt(out, np.array(rows), header="eta  EA  GA2  GA3  GJ  EI2  EI3", comments="# ")
        print("           -> %d stations (Timoshenko 6x6 diagonal) -> %s" % (len(etas), out))


def main():
    ap = argparse.ArgumentParser(description="OpenSG_io: inputs -> OpenSG 1D-shell / 2D-solid YAML")
    ap.add_argument("input"); ap.add_argument("outdir")
    ap.add_argument("--name", default=None)
    ap.add_argument("--solid", action="store_true", help="also build the 2D-solid via PreVABS")
    ap.add_argument("--stations", type=float, nargs="+", default=None, help="windIO: span fractions")
    ap.add_argument("--nstations", type=int, default=10)
    ap.add_argument("--shell-ms", type=float, default=0.01)
    ap.add_argument("--solid-ms", type=float, default=0.02)
    ap.add_argument("--prevabs", default=None)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    prevabs = a.prevabs or find_prevabs()
    kind = detect(a.input)
    if kind == "windio":
        handle_windio(a.input, a.outdir, a, prevabs)
    elif kind == "prevabs":
        handle_prevabs(a.input, a.outdir, a, prevabs)
    else:
        handle_openfast(a.input, a.outdir, a)
    print("DONE -> %s" % a.outdir, flush=True)


if __name__ == "__main__":
    main()
