#!/usr/bin/env python3
"""Generate 2020 3D VRRAM 8x8 Voltage & Current Measurement Spectre Netlists."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "netlists" / "arrays" / "vrram_2020"

NMOS_INC = "$FREEPDK45_DIR/ncsu_basekit/models/hspice/tran_models/models_nom/NMOS_VTG.inc"
PILLAR_SCS = "../../cells/vrram_2r_pillar_ta2o5.scs"


def generate_array_subckt() -> str:
    lines = [
        "// Define 8x8 2R + Bottom-Select VRRAM Subarray",
        "subckt vrram_8x8_array ( bl0 bl1 bl2 bl3 bl4 bl5 bl6 bl7 sl0 sl1 sl2 sl3 sl4 sl5 sl6 sl7 wl_even0 wl_odd0 gnd_ref )",
    ]
    for r in range(8):
        if r == 0:
            lines.append("    // Row 0 (Active Select Line sl0 = 1.1V)")
        elif r == 1:
            lines.append("\n    // Row 1 (Active Select Line sl1 = 1.1V)")
        elif r == 2:
            lines.append("\n    // Row 2 (Active Select Line sl2 = 1.1V)")
        elif r == 3:
            lines.append("\n    // Row 3 (Unselected Select Line sl3 = 0.0V)")
        else:
            lines.append(f"\n    // Row {r}")

        for c in range(8):
            # 3x3 Active Window (Rows 0..2, Cols 0..2) programmed to LRS/HRS (1.0 / 0.0)
            if r < 3 and c < 3:
                x_even, x_odd = "1.0", "0.0"
            else:
                x_even, x_odd = "0.3", "0.3"
            lines.append(
                f"    Xp_{r}_{c} (wl_even0 wl_odd0 p_{r}_{c} sl{c} bl{c} gnd_ref) "
                f"vrram_pillar x0_even={x_even} x0_odd={x_odd}"
            )
    lines.append("ends vrram_8x8_array\n")
    return "\n".join(lines)


def generate_netlist(mode: str = "voltage") -> str:
    title = "VOLTAGE MEASUREMENT" if mode == "voltage" else "CURRENT MEASUREMENT"
    out = [
        f"// Spectre Netlist: 2020 3D VRRAM 8x8 Iso-Scale Array ({title})",
        "// Architecture: Kim & Li (ISVLSI 2020) 2R + Bottom-Select Transistor Architecture",
        "// Baseline PDK: FreePDK 45nm CMOS\n",
        "simulator lang=spectre",
        "global 0\n",
        f'include "{NMOS_INC}"',
        f'include "{PILLAR_SCS}"\n',
        generate_array_subckt(),
        "// --- INPUT & CONTROL STIMULI ---",
        "// Bit Line Drivers: 3x3 Active Window (BL0..BL2 @ 0.5V Read Pulse)",
    ]

    if mode == "voltage":
        out.append("Vbl0 (bl0 0) vsource type=pulse val0=0 val1=0.5 period=100n delay=70n rise=1n fall=1n width=10n")
    else:
        out.append("Vbl0 (drive_bl0 0) vsource type=pulse val0=0 val1=0.5 period=100n delay=70n rise=1n fall=1n width=10n")
        out.append("Vprb0 (drive_bl0 bl0) vsource type=dc dc=0")

    out.append("Vbl1 (bl1 0) vsource type=pulse val0=0 val1=0.5 period=100n delay=70n rise=1n fall=1n width=10n")
    out.append("Vbl2 (bl2 0) vsource type=pulse val0=0 val1=0.5 period=100n delay=70n rise=1n fall=1n width=10n")

    out.append("\n// Unselected Bit Lines (BL3..BL7 @ 0V)")
    for c in range(3, 8):
        out.append(f"Vbl{c} (bl{c} 0) vsource type=dc dc=0")

    out.append("\n// Select Line Gates: Active (SL0..SL2 @ 1.1V ON), Unselected (SL3..SL7 @ 0.0V OFF)")
    for c in range(8):
        v_sl = "1.1" if c < 3 else "0.0"
        out.append(f"Vsl{c} (sl{c} 0) vsource type=dc dc={v_sl}")

    out.append("\n// Word Line Planes (Sense Terminals)")
    out.append("V_wl_even (wl_even0 0) vsource type=dc dc=0")
    out.append("V_wl_odd (wl_odd0 0) vsource type=dc dc=0\n")

    out.append("// Instantiate 8x8 Array Macro")
    out.append("Xarray ( bl0 bl1 bl2 bl3 bl4 bl5 bl6 bl7 sl0 sl1 sl2 sl3 sl4 sl5 sl6 sl7 wl_even0 wl_odd0 0 ) vrram_8x8_array\n")

    out.append("// Simulation Controls")
    out.append("tran_analysis tran stop=120n errpreset=moderate")
    out.append("saveOptions options rawfmt=psfascii")

    if mode == "voltage":
        out.append("save bl0 bl1 bl2 bl3 bl4 sl0 sl3 wl_even0 wl_odd0 Xarray.p_0_0 Xarray.p_0_3 Xarray.p_4_4")
    else:
        out.append("save Vprb0:p Vbl1:p Vbl2:p Vbl3:p Vbl4:p V_wl_even:p V_wl_odd:p")

    return "\n".join(out) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for mode, filename in [("voltage", "vrram_8x8_voltage_meas.scs"), ("current", "vrram_8x8_current_meas.scs")]:
        filepath = OUT_DIR / filename
        filepath.write_text(generate_netlist(mode), encoding="utf-8")
        print(f"Generated: {filepath.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()