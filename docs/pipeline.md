# windIO v2 → OpenSG cross-section: how the mapping works

## windIO v2 blade model (what we read)

`components.blade` =
- `reference_axis{x,y,z}` — spanwise axis (prebend/sweep/length), each `{grid,values}`.
- `outer_shape{chord, twist, rthick, section_offset_y, airfoils}` — spanwise scalar distributions
  (`{grid,values}`) and an airfoil list (`{name, spanwise_position}`).
- `structure{webs, layers, anchors, elastic_properties}`:
  - `anchors` — named arc positions (TE, LE, spar_cap_ss/ps, le/te_reinforcement, web attachments);
    each gives `start_nd_arc` / `end_nd_arc` as `{grid,values}` over the span.
  - `layers` — each spans `start_nd_arc → end_nd_arc` (referencing anchors via `{anchor:{name,handle}}`)
    with a spanwise `thickness` and `fiber_orientation`, and a `material`.
  - `webs` — connect a suction-side anchor to a pressure-side anchor; their layers are `*_skin/*_filler/*_skin`.

`nd_arc` s ∈ [0,1] runs **TE(0) → suction/upper → LE(~0.5) → pressure/lower → TE(1)**, matching the windIO
airfoil coordinate ordering (coords start at the TE upper, x: 1 → 0 → 1).

## Building a cross-section at span r (`build_cross_section`)

1. **Airfoil** — blend the two bracketing airfoils (by `spanwise_position`) onto a common arc, scale by
   `chord(r)`.
2. **Breakpoints** — collect every layer `start/end` arc and every web attachment arc → segment boundaries.
3. **Per-segment laminate** — for each arc segment, the laminate = all layers covering its midpoint, ordered
   outer→inner (`gelcoat, shell_triax_outer, te/spar/le reinforcement, fillers, shell_triax_inner`). Each
   distinct laminate tuple `(material, thickness, fiber_angle)…` becomes an element set / layup.
4. **Webs** — each web is a node chain from its suction attachment node to its pressure attachment node,
   carrying the web laminate (skin/foam/skin).
5. **Materials** — windIO `E=[E1,E2,E3] G=[G12,G13,G23] nu=[nu12,nu13,nu23]` (orthotropic) map 1:1 to the
   OpenSG material block; isotropic materials replicate the scalar.

## Emit

- `emit_opensg_yaml` — the 1D-shell SG (line elements, e1=+z, e2=tangent, e3 inward on skin / e1×e2 on webs).
- `emit_prevabs` — `{name}.dat` (normalised airfoil), `materials.xml` (materials + laminae, ply count =
  round(layer_thickness / ply_t)), and `{name}.xml` (airfoil baseline + dividing points by normalised x and
  side + vertical web baselines + layups + components) for `prevabs.exe -i {name}.xml --vabs --hm`.

## Notes / limitations

- Ply count in the PreVABS layup is `round(thickness / material.ply_t)`; the OpenSG 1D YAML carries the exact
  continuous thickness, so the two paths can differ by < one ply at thin layers.
- Fiber orientation is taken as the windIO `fiber_orientation` (deg, relative to the spanwise axis = OpenSG
  theta3).
- Airfoil blending is linear in arc; very-thick root (circular) stations are supported but the structure
  there is dominated by the shell layers.
