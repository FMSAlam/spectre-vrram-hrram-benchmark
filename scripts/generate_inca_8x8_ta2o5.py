#!/usr/bin/env python3
"""Generate 2023 INCA 8x8 Array Spectre Netlists (Ta2O5 Variant)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "netlists" / "arrays" / "inca_2023"

NMOS_INC = "$FREEPDK45_DIR/ncsu_basekit/models/hspice/tran_models/models_nom/NMOS_VTG.inc"
CELL_SCS = "../../cells/inca_2t1r_cell_ta2o5.scs"


def generate_array_subckt(uniform_lrs: bool = True) -> str:
    lines = [
        "// 8x8 INCA Subarray Macro (Ta2O5)",
        "subckt inca_8x8_array ( p0 p1 p2 p3 p4 p5 p6 p7 r0 r1 r2 r3 r4 r5 r6 r7 c0 c1 c2 c3 c4 c5 c6 c7 plane_out gnd_ref )",
    ]
    for r in range(8):
        for c in range(8):
            x_init = "1.0" if (uniform_lrs or (r < 3 and c < 3)) else "0.3"
            lines.append(
                f"\tXcell_{r}_{c} ( p{c} r{r} c{c} plane_out gnd_ref ) inca_2t1r_cell_ta2o5 x0={x_init}"
            )
    lines.append("ends inca_8x8_array\n")
    return "\n".join(lines)


def generate_netlist(mode: str = "current") -> str:
    title_mode = "CURRENT MEASUREMENT" if mode == "current" else "VOLTAGE MEASUREMENT"
    out = [
        f"// Spectre Netlist: 2023 3D INCA 8x8 Array - Ta2O5 ({title_mode})",
        "// Architecture: Kim et al. (HPCA 2023) 2T1R Input-Stationary Dataflow",
        "// Baseline Node: FreePDK 45nm CMOS | Workload: 3x3 Spatial Gated Conv Window\n",
        "simulator lang=spectre",
        "global 0\n",
        f'include "{NMOS_INC}"',
        f'include "{CELL_SCS}"\n',
        generate_array_subckt(uniform_lrs=True),
        "// 3x3 Window Inputs (P0..P2 Driven, P3..P7 Grounded)",
    ]

    if mode == "current":
        out.append("Vp0 (drive_p0 0) vsource type=pulse val0=0 val1=0.5 period=100n delay=70n rise=1n fall=1n width=10n")
        out.append("Vprb0 (drive_p0 p0) vsource type=dc dc=0")
    else:
        out.append("Vp0 (p0 0) vsource type=pulse val0=0 val1=0.5 period=100n delay=70n rise=1n fall=1n width=10n")

    out.append("Vp1 (p1 0) vsource type=pulse val0=0 val1=0.5 period=100n delay=70n rise=1n fall=1n width=10n")
    out.append("Vp2 (p2 0) vsource type=pulse val0=0 val1=0.5 period=100n delay=70n rise=1n fall=1n width=10n")
    for c in range(3, 8):
        out.append(f"Vp{c} (p{c} 0) vsource type=dc dc=0")

    out.append("\n// Row Select Gates (TR1)")
    for r in range(8):
        v_r = "1.1" if r < 3 else "0.0"
        out.append(f"Vr{r} (r{r} 0) vsource type=dc dc={v_r}")

    out.append("\n// Col Select Gates (TR2)")
    for c in range(8):
        v_c = "1.1" if c < 3 else "0.0"
        out.append(f"Vc{c} (c{c} 0) vsource type=dc dc={v_c}")

    out.append("\n// Shared Collection Plane Resistor Load")
    out.append("Rload (plane_out 0) resistor r=1.0\n")

    out.append("// Instantiate Macro")
    out.append("Xmacro ( p0 p1 p2 p3 p4 p5 p6 p7 r0 r1 r2 r3 r4 r5 r6 r7 c0 c1 c2 c3 c4 c5 c6 c7 plane_out 0 ) inca_8x8_array\n")

    out.append("tran_analysis tran stop=120n errpreset=moderate")
    out.append("saveOptions options rawfmt=psfascii")

    if mode == "current":
        out.append("save plane_out Vprb0:p Vp1:p Vp2:p Vp4:p")
    else:
        out.append("save plane_out p0 p1 p2 p3 p4 r0 r1 r2 r3 c0 c1 c2 c3 Xmacro.Xcell_0_0.n1 Xmacro.Xcell_0_0.n2")

    return "\n".join(out) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for mode in ["current", "voltage"]:
        fname = f"inca_8x8_ta2o5_{mode}_meas.scs"
        fpath = OUT_DIR / fname
        fpath.write_text(generate_netlist(mode), encoding="utf-8")
        print(f"Generated: {fpath.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()