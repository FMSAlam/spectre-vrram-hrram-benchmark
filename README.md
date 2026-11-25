# spectre-vrram-hrram-benchmark

Cadence Spectre netlists and Verilog-A models for transient simulation of 8x8 3D VRRAM (2R) and 3D INCA HRRAM (2T1R) arrays at 45 nm.

## Files

```text
veriloga/
  memristor_ta2o5.va
  memristor_hfo2.va
netlists/
  cells/
    vrram_2r_pillar_ta2o5.scs
    inca_2t1r_cell_ta2o5.scs
    inca_2t1r_cell_hfo2.scs
  arrays/
    vrram_2020/
      vrram_8x8_voltage_meas.scs
      vrram_8x8_current_meas.scs
    inca_2023/
      inca_8x8_ta2o5_voltage_meas.scs
      inca_8x8_ta2o5_current_meas.scs
      inca_8x8_hfo2_voltage_meas.scs
      inca_8x8_hfo2_current_meas.scs
scripts/
  generate_vrram_8x8.py
  generate_inca_8x8_ta2o5.py
  generate_inca_8x8_hfo2.py
```

## Requirements

- Cadence IC 6.1.5 / Spectre (with Verilog-A support)
- NCSU FreePDK45 (`NMOS_VTG.inc`)
- Python 2.x (optional, for netlist generation)

## Usage

Set the PDK path and run Spectre on any array netlist:

```bash
export FREEPDK45_DIR=/path/to/FreePDK45

# 3D VRRAM (2R, Ta2O5)
spectre netlists/arrays/vrram_2020/vrram_8x8_current_meas.scs
spectre netlists/arrays/vrram_2020/vrram_8x8_voltage_meas.scs

# 3D INCA HRRAM (2T1R, Ta2O5)
spectre netlists/arrays/inca_2023/inca_8x8_ta2o5_current_meas.scs
spectre netlists/arrays/inca_2023/inca_8x8_ta2o5_voltage_meas.scs

# 3D INCA HRRAM (2T1R, HfO2)
spectre netlists/arrays/inca_2023/inca_8x8_hfo2_current_meas.scs
spectre netlists/arrays/inca_2023/inca_8x8_hfo2_voltage_meas.scs
```

Regenerate netlists:

```bash
python scripts/generate_vrram_8x8.py
python scripts/generate_inca_8x8_ta2o5.py
python scripts/generate_inca_8x8_hfo2.py
```