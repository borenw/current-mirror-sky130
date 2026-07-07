#!/usr/bin/env python3
"""Generate the doc figures for the current-mirror comparison from the
ngspice output-characteristic sweeps (doc/_iv_*.txt, written by tb_compliance.spice).

    ngspice -b spice/tb_compliance.spice   # writes doc/_iv_cascode.txt, doc/_iv_sooch.txt
    python3 plot.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_CASC = "#C1440E"   # burnt orange
C_SOOCH = "#1B6CA8"  # blue
IREF = 10.0          # uA target

def load(name):
    d = np.loadtxt(f"doc/_iv_{name}.txt")
    return d[:, 0], d[:, 1]   # Vout [V], Iout [uA]

def compliance(v, i, ref):
    return next(vv for vv, ii in zip(v, i) if ii >= 0.99 * ref)

vc, ic = load("cascode")
vs, is_ = load("sooch")
Ihi_c = ic[np.argmin(abs(vc - 1.6))]
Ihi_s = is_[np.argmin(abs(vs - 1.6))]
cc = compliance(vc, ic, Ihi_c)
cs = compliance(vs, is_, Ihi_s)

# ---------- Figure 1: output characteristic ----------
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.plot(vc, ic, color=C_CASC, lw=2.2, label="2-stack cascode (4T)")
ax.plot(vs, is_, color=C_SOOCH, lw=2.2, label="Sooch wide-swing (5T)")
ax.axhline(IREF, color="#888888", ls=":", lw=1, zorder=0)
for v0, col, txt, dx in [(cc, C_CASC, f"{cc:.2f} V", 0.04), (cs, C_SOOCH, f"{cs:.2f} V", -0.30)]:
    ax.axvline(v0, color=col, ls="--", lw=1.2)
    ax.annotate(f"V$_{{out,min}}$ = {txt}", xy=(v0, 4.6), xytext=(v0 + dx, 4.6),
                color=col, fontsize=9, va="center")
ax.annotate("", xy=(cc, 6.3), xytext=(cs, 6.3),
            arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.4))
ax.text((cc + cs) / 2, 6.6, f"+{(cc - cs):.2f} V output swing recovered",
        ha="center", fontsize=9.5, color="#333333")
ax.set_xlabel("Output voltage  V$_{out}$  [V]")
ax.set_ylabel("Output current  I$_{out}$  [µA]")
ax.set_title("Figure 3 · NMOS current-mirror output characteristic — SKY130, I$_{ref}$ = 10 µA, 1.8 V")
ax.set_xlim(0, 1.8); ax.set_ylim(0, 11)
ax.legend(loc="lower right", bbox_to_anchor=(0.985, 0.045), framealpha=0.97)
ax.grid(alpha=0.25)

# zoom on the knee (upper-right, clear of legend + labels)
axins = ax.inset_axes([0.60, 0.55, 0.37, 0.37])
axins.plot(vc, ic, color=C_CASC, lw=2); axins.plot(vs, is_, color=C_SOOCH, lw=2)
axins.axhline(IREF, color="#888888", ls=":", lw=0.8)
axins.axvline(cc, color=C_CASC, ls="--", lw=0.9); axins.axvline(cs, color=C_SOOCH, ls="--", lw=0.9)
axins.set_xlim(0.2, 0.95); axins.set_ylim(9.5, 10.15)
axins.grid(alpha=0.3); axins.tick_params(labelsize=7)
axins.set_title("knee (zoom)", fontsize=8)
fig.tight_layout(); fig.savefig("doc/iv_compliance.png", dpi=140)
plt.close(fig)

# ---------- Figure 2: how each mirror spends the 1.8 V rail (output branch) ----------
fig, ax = plt.subplots(figsize=(7.4, 3.0))
VDD = 1.8
rows = [("2-stack\ncascode", cc, C_CASC, "5.5 MΩ"),
        ("Sooch\nwide-swing", cs, C_SOOCH, "26.3 MΩ")]
for y, (name, vmin, col, rout) in enumerate(rows):
    ax.barh(y, vmin, color="#d9d2c5", edgecolor="#b7ad9b", height=0.55)
    ax.barh(y, VDD - vmin, left=vmin, color=col, alpha=0.85, height=0.55)
    ax.text(vmin / 2, y, "headroom\nfor bias", ha="center", va="center", fontsize=8, color="#555555")
    ax.text(vmin + (VDD - vmin) / 2, y, f"usable output swing\n{VDD - vmin:.2f} V   (R$_{{out}}$ = {rout})",
            ha="center", va="center", fontsize=8.5, color="white", fontweight="bold")
    ax.text(vmin, y + 0.34, f"{vmin:.2f} V", ha="center", fontsize=8, color=col)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows])
ax.set_xlim(0, VDD); ax.set_xlabel("Output-node voltage budget on the 1.8 V rail  [V]")
ax.set_title("Figure 4 · Output rail budget — Sooch recovers ~0.39 V of swing + higher R$_{out}$", fontsize=11.5)
ax.invert_yaxis()
fig.tight_layout(); fig.savefig("doc/headroom_bars.png", dpi=140)
plt.close(fig)
print(f"cascode Vmin={cc:.3f}  sooch Vmin={cs:.3f}  recovered={cc-cs:.3f} V")
print("wrote doc/iv_compliance.png, doc/headroom_bars.png")
