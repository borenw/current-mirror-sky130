#!/usr/bin/env python3
"""Annotated SVG schematics for both NMOS current mirrors.
Device sizes (W/L) and the ngspice DC operating point (node voltages + key
Vgs / Vds) are baked in as annotations.  Outputs cm_cascode.svg / cm_sooch.svg.
    python3 draw_schematic.py
"""
CASC="#C1440E"; SOOCH="#1B6CA8"; INK="#172B4D"; MUT="#5b6b7f"

def header(w,h,title,sub):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="Helvetica,Arial,sans-serif">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n'
            f'<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="4" refY="4.5" '
            f'orient="auto"><path d="M0,1 L8,4.5 L0,8 z" fill="{INK}"/></marker></defs>\n'
            f'<text x="{w/2}" y="30" font-size="19" font-weight="bold" fill="{INK}" '
            f'text-anchor="middle">{title}</text>\n'
            f'<text x="{w/2}" y="50" font-size="12.5" fill="{MUT}" '
            f'text-anchor="middle">{sub}</text>\n')

def L(x1,y1,x2,y2,c=INK,w=1.7,arrow=False):
    a=' marker-end="url(#ah)"' if arrow else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{a}/>\n'
def D(x,y): return f'<circle cx="{x}" cy="{y}" r="3.3" fill="{INK}"/>\n'
def T(x,y,s,size=13,c=INK,anc="start",style="",w="normal"):
    st=f' font-style="{style}"' if style else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{c}" text-anchor="{anc}"{st} font-weight="{w}">{s}</text>\n'
def hop(x,y,r=7):
    """horizontal wire hops over a vertical crossing at (x,y)."""
    return f'<path d="M{x-r},{y} A{r},{r} 0 0 1 {x+r},{y}" fill="none" stroke="{INK}" stroke-width="1.7"/>\n'

def nmos(cx,cy,name,lbl_dx=12):
    s =L(cx,cy-32,cx,cy-18)
    s+=L(cx,cy+18,cx,cy+32)
    s+=L(cx,cy-18,cx,cy+18,w=2.6)               # channel bar
    s+=L(cx-8,cy-15,cx-8,cy+15,w=2.6)           # gate bar
    s+=L(cx-30,cy,cx-8,cy)                       # gate stub
    s+=L(cx,cy+32,cx-0.01,cy+22,arrow=True)     # source arrow
    s+=T(cx+lbl_dx,cy+5,name,size=15,w="bold")
    return s,(cx,cy-32),(cx,cy+32),(cx-30,cy)

def csrc(x,ytop,ybot,label):
    cy=(ytop+ybot)/2
    s =L(x,ytop,x,cy-15)
    s+=f'<circle cx="{x}" cy="{cy}" r="15" fill="none" stroke="{INK}" stroke-width="1.7"/>\n'
    s+=L(x,cy+8,x,cy-7,arrow=True)
    s+=L(x,cy+15,x,ybot)
    s+=T(x+21,cy+4,label,size=12.5,c=MUT,style="italic")
    return s
def gnd(x,y):
    return (L(x,y,x,y+12)+L(x-11,y+12,x+11,y+12)+L(x-7,y+17,x+7,y+17)+L(x-3,y+22,x+3,y+22))
def volt(x,y,node,v,c,anc="start"):
    return T(x,y,node,size=12.5,c=c,w="bold",anc=anc)+T(x,y+15,v,size=12,c=c,anc=anc)
def box(x,y,w,h,fill,stroke):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>\n'

# ==================================================================
#  STANDARD ("2-STACK") CASCODE  — 4T
# ==================================================================
def cascode():
    W,H=820,540
    s=header(W,H,"2-stack cascode NMOS current mirror  ·  4T",
             "SKY130 nfet_01v8  ·  I_ref = 10 µA  ·  VDD = 1.8 V  ·  TT 27 °C")
    xin,xout=250,430; yvdd=95; ygnd=490; yT,yB=200,335
    s+=L(150,yvdd,500,yvdd); s+=T(150,yvdd-9,"VDD = 1.8 V",12,MUT)
    s+=csrc(xin,yvdd,150,"I_ref = 10 µA")
    m3,d3,s3,g3=nmos(xin,yT,"M3"); s+=m3
    m1,d1,s1,g1=nmos(xin,yB,"M1"); s+=m1
    m4,d4,s4,g4=nmos(xout,yT,"M4"); s+=m4
    m2,d2,s2,g2=nmos(xout,yB,"M2"); s+=m2
    # input branch
    s+=L(xin,150,*d3); s+=L(*s3,*d1); s+=L(*s1,xin,ygnd)
    # output branch (vout -> load)
    s+=L(xout,150,*d4)
    s+=L(xout,150,xout+70,150)+L(xout+70,150,xout+70,183,arrow=True)
    s+=T(xout+80,150,"I_out",12.5,SOOCH,style="italic")+T(xout+80,166,"→ load",11,MUT)
    s+=L(*s4,*d2); s+=L(*s2,xout,ygnd)
    # cascode gates (M3,M4) diode-tied to iin (top node)
    rc=g3[0]-16
    s+=L(*g3,rc,g3[1])+L(rc,g3[1],rc,165)+L(rc,165,xin,165); s+=D(xin,165)
    s+=L(*g4,rc,g4[1])+L(rc,g4[1],rc,g3[1])
    # bottom gates (M1,M2) diode-tied to na ; M2 gate routed BELOW the row
    yb_bus=yB+55
    s+=L(*g1,g1[0]-30,g1[1])+L(g1[0]-30,g1[1],g1[0]-30,306)+L(g1[0]-30,306,xin,306); s+=D(xin,306)
    s+=L(g1[0]-30,g1[1],g1[0]-30,yb_bus)                     # down to bottom bus
    s+=L(g1[0]-30,yb_bus,g2[0],yb_bus)                       # across (crosses M1 source wire)
    s+=hop(xin,yb_bus)                                       # hop over M1 source-to-gnd wire
    s+=L(g2[0],yb_bus,g2[0],g2[1])                           # up to M2 gate
    # ground
    s+=L(150,ygnd,500,ygnd)+D(xin,ygnd)+D(xout,ygnd)+gnd(340,ygnd)
    # node voltages
    s+=volt(xin+14,158,"iin","1.66 V",CASC)
    s+=volt(xin+14,298,"na","0.76 V",CASC)
    s+=volt(xout+14,298,"nb","0.75 V",CASC)
    s+=volt(xout+14,158,"vout","0.90 V",SOOCH)
    # right-hand annotation box
    bx=560
    s+=box(bx,150,240,120,"#fbf3ee",CASC)
    s+=T(bx+14,175,"All devices",12.5,INK,w="bold")+T(bx+120,175,"W/L = 2 / 0.5 µm",12.5,CASC,w="bold")
    s+=T(bx+14,200,"M3,M4 gates biased at 2·V_gs,",11.5,INK)
    s+=T(bx+14,216,"so M2 sits at V_ds = V_gs = 0.75 V",11.5,CASC)
    s+=T(bx+14,232,"(≈V_t of headroom wasted); M4 has",11.5,INK)
    s+=T(bx+14,248,"only V_ds = 0.15 V → r_o ≈ 60 kΩ.",11.5,CASC)
    s+=box(bx,285,240,66,"#f4f0ea",MUT)
    s+=T(bx+14,308,"V_out,min = V_t + 2V_ov = 0.72 V",12.5,INK,w="bold")
    s+=T(bx+14,330,"R_out = 5.5 MΩ   (@ V_out = 0.9 V)",12.5,INK,w="bold")
    s+="</svg>\n"
    open("cm_cascode.svg","w").write(s); print("wrote cm_cascode.svg")

# ==================================================================
#  SOOCH WIDE-SWING CASCODE — 5T
# ==================================================================
def sooch():
    W,H=980,560
    s=header(W,H,"Sooch wide-swing cascode NMOS current mirror  ·  5T",
             "SKY130 nfet_01v8  ·  I_ref = 10 µA  ·  VDD = 1.8 V  ·  TT 27 °C")
    xb,xin,xout=180,430,600; yvdd=90; ygnd=525; yT,yB=250,390
    s+=L(120,yvdd,660,yvdd); s+=T(120,yvdd-9,"VDD = 1.8 V",12,MUT)
    s+=csrc(xb,yvdd,d5top:=150,"I_ref")
    s+=csrc(xin,yvdd,150,"I_ref")
    # devices
    m5,d5,s5,g5=nmos(xb,yT,"M5"); s+=m5            # bias diode
    m3,d3,s3,g3=nmos(xin,yT,"M3"); s+=m3
    m1,d1,s1,g1=nmos(xin,yB,"M1"); s+=m1
    m4,d4,s4,g4=nmos(xout,yT,"M4"); s+=m4
    m2,d2,s2,g2=nmos(xout,yB,"M2"); s+=m2
    # bias leg: Iref -> ncas (M5 drain=gate) -> gnd ; M5 diode tie
    s+=L(xb,d5top,*d5); s+=L(*s5,xb,ygnd)
    s+=L(g5[0],g5[1],g5[0],d5[1])+L(g5[0],d5[1],xb,d5[1]); s+=D(xb,d5[1])   # gate->drain
    # input leg: Iref -> iin(=M3 drain=ng) -> na -> M1 -> gnd
    s+=L(xin,150,*d3); s+=L(*s3,*d1); s+=L(*s1,xin,ygnd)
    # output leg: vout -> M4 -> nb -> M2 -> gnd
    s+=L(xout,150,*d4)
    s+=L(xout,150,xout+70,150)+L(xout+70,150,xout+70,185,arrow=True)
    s+=T(xout+80,150,"I_out",12.5,SOOCH,style="italic")+T(xout+80,166,"→ load",11,MUT)
    s+=L(*s4,*d2); s+=L(*s2,xout,ygnd)
    # ---- ncas bus: from M5-drain vertical across to cascode gate rails ----
    yn=205
    s+=L(xb,d5[1],xb,yn); s+=D(xb,yn)              # tap ncas down to bus level
    rc3=g3[0]-16; rc4=g4[0]-16
    s+=L(xb,yn,rc3,yn)                             # bus xb -> M3 gate rail
    s+=L(rc3,yn,rc3,g3[1])+L(rc3,g3[1],*g3)        # drop to M3 gate
    s+=L(rc3,yn,rc4,yn); s+=hop(xin,yn)            # bus to M4 rail, hop over iin lead
    s+=L(rc4,yn,rc4,g4[1])+L(rc4,g4[1],*g4)        # drop to M4 gate
    # ---- ng bus: iin (M3 drain) -> gates of M1,M2 (routed below the bottom row) ----
    yg=yB+58; lane=xin-70
    s+=L(xin,175,lane,175); s+=D(xin,175)          # tap iin (top node) to left lane
    s+=L(lane,175,lane,yg)                         # down lane (plain crossings w/ ncas bus & na)
    s+=L(lane,yg,g2[0],yg); s+=hop(xin,yg)         # bottom bus to M2 gate rail, hop over M1 source
    s+=L(lane,yg,g1[0],yg)+L(g1[0],yg,*g1)         # up to M1 gate
    s+=L(g2[0],yg,*g2)                             # up to M2 gate
    # ground
    s+=L(120,ygnd,660,ygnd)
    for gx in (xb,xin,xout): s+=D(gx,ygnd)
    s+=gnd(390,ygnd)
    # node voltages
    s+=volt(xb+14,d5[1]-2,"ncas","1.02 V",SOOCH)
    s+=volt(xin+14,150,"iin = ng","0.77 V",SOOCH)
    s+=volt(xin+14,yB-40,"na","0.21 V",SOOCH)
    s+=volt(xout+14,yB-40,"nb","0.21 V",SOOCH)
    s+=volt(xout+14,158,"vout","0.90 V",SOOCH)
    # annotation box (right)
    bx=720
    s+=box(bx,150,250,132,"#eef4f9",SOOCH)
    s+=T(bx+14,175,"M1–M4",12.5,INK,w="bold")+T(bx+90,175,"W/L = 2 / 0.5 µm",12.5,SOOCH,w="bold")
    s+=T(bx+14,193,"M5 (bias)",12.5,INK,w="bold")+T(bx+90,193,"W/L = 0.5 / 1.0 µm",12.5,SOOCH,w="bold")
    s+=T(bx+14,216,"M5 sets ncas = V_t + 2V_ov, so the",11.5,INK)
    s+=T(bx+14,232,"bottom pair sits at V_ds ≈ V_dsat",11.5,SOOCH)
    s+=T(bx+14,248,"= 0.21 V (just saturated). Cascodes",11.5,INK)
    s+=T(bx+14,264,"M3,M4 keep V_ds ≈ 0.6 V → high r_o.",11.5,SOOCH)
    s+=box(bx,297,250,66,"#eaeef2",MUT)
    s+=T(bx+14,320,"V_out,min = 2V_ov = 0.34 V",12.5,INK,w="bold")
    s+=T(bx+14,342,"R_out = 26 MΩ   (@ V_out = 0.9 V)",12.5,INK,w="bold")
    s+="</svg>\n"
    open("cm_sooch.svg","w").write(s); print("wrote cm_sooch.svg")

cascode(); sooch()
