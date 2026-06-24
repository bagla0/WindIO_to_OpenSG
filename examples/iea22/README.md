# IEA-22-280-RWT benchmark (r = 0.50, mid-span)

Worked output of the converter for the **IEA 22 MW** reference blade (the windIO v2 file bundled with
`pip install windIO`), at non-dimensional span **r = 0.50**: chord 4.86 m, twist 1.16°, an FFA-W3 airfoil
blend with **3 shear webs** and **6 laminates** (carbon spar caps SS/PS, foam fillers, glass LE/TE
reinforcements, glass-triax skins, biax/foam webs).

| file | what |
|------|------|
| `iea22_r050_shell.yaml`        | OpenSG **1D-shell SG** (nodes, line elements, element sets = laminates, sections, materials) → JAX MSG-RM / Kirchhoff |
| `iea22_r050_prevabs/*.xml`     | **PreVABS** cross-section input (general/baselines/dividing-points/webs/layups/components) |
| `iea22_r050_prevabs/*.dat`     | normalised airfoil contour for PreVABS |
| `iea22_r050_prevabs/materials.xml` | PreVABS materials + laminae |
| `iea22_r050_orient.png`        | element e1/e2/e3 frames (e2 = blue tangent, e3 = green OML→IML on skin / red e1×e2 on webs; e1 = +z out-of-plane) |

## Regenerate / extend

```bash
# this exact station
python scripts/convert_station.py --r 0.5 --mesh-size 0.01 --out examples/iea22

# + mesh the 2D-solid (needs the PreVABS binary, see scripts/fetch_prevabs.py)
python scripts/convert_station.py --r 0.5 --out out --run --prevabs <path>/prevabs.exe
#   -> out/xsec_r050_prevabs/xsec_r050.sg   (then convert_sg_to_yaml -> 2D-solid SG YAML)

# all stations
python scripts/run_sweep.py
```

## Validated values (mid-span, r = 0.5)

The 1D-shell SG homogenizes (OpenSG-TW) to a Timoshenko 6×6 whose RM and Kirchhoff diagonals agree to
**< 0.4 %**:

| term | RM | KL |
|------|----|----|
| EA   | 2.185e10 | 2.185e10 |
| GA2  | 5.341e8  | 5.358e8  |
| GA3  | 1.928e8  | 1.935e8  |
| GJ   | 7.657e8  | 7.674e8  |
| EI2  | 7.355e9  | 7.355e9  |
| EI3  | 6.297e10 | 6.297e10 |

The PreVABS path meshes this same section to a ~26 k-element 2D-solid `.sg` for the VABS / FEniCS solid
reference (run `--run` above, then `convert_sg_to_yaml`).
