#!/usr/bin/env python3
"""Run tb_op.spice in ngspice and dump the per-device operating point of both
mirrors to op_points.json (consumed by draw_schematic.py so the annotations
come straight from the simulator).  Requires $PDK_ROOT set.
    PDK_ROOT=/path/to/pdk python3 extract_op.py
"""
import subprocess, re, os, json, tempfile

PDK = os.environ.get("PDK_ROOT", "/home/usr1/bw4375/pdk")
LIB = f"{PDK}/sky130A/libs.tech/ngspice/sky130.lib.spice"

DECK = f'''.lib "{LIB}" tt
.include "../spice/cm_cascode.spice"
.include "../spice/cm_sooch.spice"
.param IREF=10u
.param VOUT=0.9
Vvss   vss 0 0
Iin_c  vss c_iin dc {{IREF}}
Vo_c   c_vout vss {{VOUT}}
Xc     c_iin c_vout vss cm_cascode
Iin_s  vss s_iin dc {{IREF}}
Ib_s   vss s_ibias dc {{IREF}}
Vo_s   s_vout vss {{VOUT}}
Xs     s_iin s_ibias s_vout vss cm_sooch
.control
op
'''
DEVS = {"cascode": ("xc", ["xm1","xm2","xm3","xm4"]),
        "sooch":   ("xs", ["xm5","xm1","xm2","xm3","xm4"])}
for inst, ds in DEVS.values():
    for d in ds:
        b = f"@m.{inst}.{d}.msky130_fd_pr__nfet_01v8"
        DECK += f"print {b}[id] {b}[vgs] {b}[vds] {b}[vth] {b}[vdsat] {b}[gm] {b}[gds]\n"
DECK += ".endc\n.end\n"

with tempfile.NamedTemporaryFile("w", suffix=".spice", delete=False, dir=".") as f:
    f.write(DECK); fn = f.name
out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True).stdout
os.unlink(fn)

def val(inst, d, p):
    m = re.search(rf"m\.{inst}\.{d}\.msky130_fd_pr__nfet_01v8\[{p}\]\s*=\s*([-\d.eE+]+)", out)
    return float(m.group(1))

data = {}
for mirror, (inst, ds) in DEVS.items():
    data[mirror] = {}
    for d in ds:
        idv = val(inst, d, "id"); vgs = val(inst, d, "vgs"); vds = val(inst, d, "vds")
        vth = val(inst, d, "vth"); vdsat = val(inst, d, "vdsat")
        gm = val(inst, d, "gm"); gds = val(inst, d, "gds")
        data[mirror][d.upper()] = dict(
            Id=idv, Vgs=vgs, Vds=vds, Vth=vth, Vov=vgs - vth, Vdsat=vdsat,
            gm=gm, ro=1.0 / gds, gm_id=gm / idv)

json.dump(data, open("op_points.json", "w"), indent=2)
print(json.dumps(data, indent=2))
