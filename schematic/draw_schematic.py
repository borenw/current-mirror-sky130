#!/usr/bin/env python3
"""Annotated SVG schematics for both NMOS current mirrors.
Device W/L and the full ngspice DC operating point (Id, Vgs, Vds, Vth, Vov,
Vdsat, gm, ro, gm/Id) are annotated as a card next to every transistor; the
op-point numbers are read from op_points.json (produced by extract_op.py).
    PDK_ROOT=/path/to/pdk python3 extract_op.py   # -> op_points.json
    python3 draw_schematic.py                      # -> cm_cascode.svg / cm_sooch.svg
"""
import json, os
OP = json.load(open(os.path.join(os.path.dirname(__file__) or ".", "op_points.json")))
CASC="#C1440E"; SOOCH="#1B6CA8"; INK="#172B4D"; MUT="#5b6b7f"

# W/L per device (µm) for the label on each card
WL = {"cascode": {d: "2/0.5" for d in ("XM1","XM2","XM3","XM4")},
      "sooch":   {**{d: "2/0.5" for d in ("XM1","XM2","XM3","XM4")}, "XM5": "0.5/1.0"}}

def head(w,h,title,sub):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="Helvetica,Arial,sans-serif">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n'
            f'<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="4" refY="4.5" '
            f'orient="auto"><path d="M0,1 L8,4.5 L0,8 z" fill="{INK}"/></marker></defs>\n'
            f'<text x="{w/2}" y="30" font-size="19" font-weight="bold" fill="{INK}" '
            f'text-anchor="middle">{title}</text>\n'
            f'<text x="{w/2}" y="50" font-size="12.5" fill="{MUT}" text-anchor="middle">{sub}</text>\n')
def L(x1,y1,x2,y2,c=INK,w=1.7,arrow=False,dash=None):
    a=' marker-end="url(#ah)"' if arrow else ''
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{a}{d}/>\n'
def D(x,y,r=3.3,c=INK): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>\n'
def T(x,y,s,size=13,c=INK,anc="start",style="",w="normal"):
    st=f' font-style="{style}"' if style else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{c}" text-anchor="{anc}"{st} font-weight="{w}">{s}</text>\n'
def hop(x,y,r=7): return f'<path d="M{x-r},{y} A{r},{r} 0 0 1 {x+r},{y}" fill="none" stroke="{INK}" stroke-width="1.7"/>\n'
def rbox(x,y,w,h,fill,stroke,sw=1.2): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'
def gnd(x,y): return (L(x,y,x,y+12)+L(x-11,y+12,x+11,y+12)+L(x-7,y+17,x+7,y+17)+L(x-3,y+22,x+3,y+22))
def nodev(x,y,node,v,c,anc="start"): return T(x,y,node,12.5,c,anc=anc,w="bold")+T(x,y+15,v,12,c,anc=anc)

def nmos(cx,cy,name,name_side="right"):
    s =L(cx,cy-32,cx,cy-18)+L(cx,cy+18,cx,cy+32)+L(cx,cy-18,cx,cy+18,w=2.6)
    s+=L(cx-8,cy-15,cx-8,cy+15,w=2.6)+L(cx-30,cy,cx-8,cy)
    s+=L(cx,cy+32,cx-0.01,cy+22,arrow=True)
    lx = cx+12 if name_side=="right" else cx-40
    s+=T(lx,cy+5,name,15,w="bold")
    return s,(cx,cy-32),(cx,cy+32),(cx-30,cy)
def csrc(x,ytop,ybot,label):
    cy=(ytop+ybot)/2
    s =L(x,ytop,x,cy-15)+f'<circle cx="{x}" cy="{cy}" r="15" fill="none" stroke="{INK}" stroke-width="1.7"/>\n'
    s+=L(x,cy+8,x,cy-7,arrow=True)+L(x,cy+15,x,ybot)+T(x+21,cy+4,label,12.5,MUT,style="italic")
    return s

def fmtV(v): return f"{v:.2f} V"
def fmtRo(r): return f"{r/1e6:.2f} MΩ" if r>=1e6 else f"{r/1e3:.0f} kΩ"
CW,CH=196,100
def card(x,y,dev,op,wl,color,dev_xy,attach="left"):
    """op-point card for one device + dashed leader to the transistor at dev_xy."""
    reg="saturation" if op["Vds"]>=op["Vdsat"]-0.004 else "TRIODE"
    ax = x if attach=="left" else x+CW
    s = L(dev_xy[0],dev_xy[1],ax,y+CH/2,c=color,w=1.0,dash="3,3")+D(*dev_xy,r=2.6,c=color)
    s+= rbox(x,y,CW,CH,"#ffffff",color)
    s+= T(x+10,y+17,dev,14,color,w="bold")+T(x+CW-9,y+15,"W/L "+wl,10,MUT,anc="end")
    s+= T(x+CW-9,y+27,reg,9.5,(color if reg[0]=='s' else '#B00020'),anc="end")
    s+= L(x+9,y+23,x+CW-9,y+23,c=color,w=0.7)
    rows=[(f"Id = {op['Id']*1e6:.1f} µA", f"Vds = {fmtV(op['Vds'])}"),
          (f"Vgs = {fmtV(op['Vgs'])}",    f"Vth = {fmtV(op['Vth'])}"),
          (f"Vov = {fmtV(op['Vov'])}",    f"Vdsat = {fmtV(op['Vdsat'])}"),
          (f"gm = {op['gm']*1e6:.0f} µS",  f"ro = {fmtRo(op['ro'])}"),
          (f"gm/Id = {op['gm_id']:.1f} /V","")]
    yy=y+40
    for a,b in rows:
        s+=T(x+10,yy,a,10.5,INK)
        if b: s+=T(x+104,yy,b,10.5,INK)
        yy+=13.5
    return s

# ==================================================================
def cascode():
    op=OP["cascode"]; wl=WL["cascode"]
    W,H=1040,560
    s=head(W,H,"2-stack cascode NMOS current mirror  ·  4T",
           "SKY130 nfet_01v8  ·  I_ref = 10 µA  ·  VDD = 1.8 V  ·  TT 27 °C   (op point per device)")
    xin,xout=390,590; yvdd=95; ygnd=515; yT,yB=215,360
    s+=L(300,yvdd,680,yvdd)+T(300,yvdd-9,"VDD = 1.8 V",12,MUT)
    s+=csrc(xin,yvdd,150,"I_ref = 10 µA")
    m3,d3,s3,g3=nmos(xin,yT,"M3"); s+=m3
    m1,d1,s1,g1=nmos(xin,yB,"M1"); s+=m1
    m4,d4,s4,g4=nmos(xout,yT,"M4"); s+=m4
    m2,d2,s2,g2=nmos(xout,yB,"M2"); s+=m2
    s+=L(xin,150,*d3)+L(*s3,*d1)+L(*s1,xin,ygnd)
    s+=L(xout,150,*d4)+L(xout,150,xout+70,150)+L(xout+70,150,xout+70,183,arrow=True)
    s+=T(xout+80,150,"I_out",12.5,SOOCH,style="italic")+T(xout+80,166,"→ load",11,MUT)
    s+=L(*s4,*d2)+L(*s2,xout,ygnd)
    rc=g3[0]-16
    s+=L(*g3,rc,g3[1])+L(rc,g3[1],rc,165)+L(rc,165,xin,165)+D(xin,165)
    s+=L(*g4,rc,g4[1])+L(rc,g4[1],rc,g3[1])
    ybus=yB+55
    s+=L(*g1,g1[0]-30,g1[1])+L(g1[0]-30,g1[1],g1[0]-30,306)+L(g1[0]-30,306,xin,306)+D(xin,306)
    s+=L(g1[0]-30,g1[1],g1[0]-30,ybus)+L(g1[0]-30,ybus,g2[0],ybus)+hop(xin,ybus)+L(g2[0],ybus,g2[0],g2[1])
    s+=L(300,ygnd,680,ygnd)+D(xin,ygnd)+D(xout,ygnd)+gnd(490,ygnd)
    # node voltages
    s+=nodev(xin+14,158,"iin","1.66 V",CASC)
    s+=nodev(xin+14,300,"na","0.76 V",CASC)
    s+=nodev(xout+14,300,"nb","0.75 V",CASC)
    s+=nodev(xout+14,158,"vout","0.90 V",SOOCH)
    # op cards
    s+=card(20,150,"M3",op["XM3"],wl["XM3"],CASC,(g3[0],yT),"right")
    s+=card(20,345,"M1",op["XM1"],wl["XM1"],CASC,(g1[0],yB),"right")
    s+=card(824,150,"M4",op["XM4"],wl["XM4"],CASC,(xout+8,yT),"left")
    s+=card(824,345,"M2",op["XM2"],wl["XM2"],CASC,(xout+8,yB),"left")
    # footer headline
    s+=T(W/2,H-16,"V_out,min = V_t + 2V_ov = 0.72 V      R_out = 5.5 MΩ @ V_out=0.9 V      Σ(W·L) = 4.0 µm²   —   note M2 wastes ≈V_t (V_ds=V_gs) and M4 is starved (V_ds=0.15 V, r_o=60 kΩ)",
            11.5,INK,anc="middle",w="bold")
    open("cm_cascode.svg","w").write(s+"</svg>\n"); print("wrote cm_cascode.svg")

# ==================================================================
def sooch():
    op=OP["sooch"]; wl=WL["sooch"]
    W,H=1180,640
    s=head(W,H,"Sooch wide-swing cascode NMOS current mirror  ·  5T",
           "SKY130 nfet_01v8  ·  I_ref = 10 µA  ·  VDD = 1.8 V  ·  TT 27 °C   (op point per device)")
    xb,xin,xout=470,650,820; yvdd=95; ygnd=560; yT,yB=250,410
    s+=L(410,yvdd,900,yvdd)+T(410,yvdd-9,"VDD = 1.8 V",12,MUT)
    s+=csrc(xb,yvdd,d5top:=150,"I_ref")+csrc(xin,yvdd,150,"I_ref")
    m5,d5,s5,g5=nmos(xb,yT,"M5"); s+=m5
    m3,d3,s3,g3=nmos(xin,yT,"M3"); s+=m3
    m1,d1,s1,g1=nmos(xin,yB,"M1"); s+=m1
    m4,d4,s4,g4=nmos(xout,yT,"M4"); s+=m4
    m2,d2,s2,g2=nmos(xout,yB,"M2"); s+=m2
    s+=L(xb,d5top,*d5)+L(*s5,xb,ygnd)
    s+=L(g5[0],g5[1],g5[0],d5[1])+L(g5[0],d5[1],xb,d5[1])+D(xb,d5[1])
    s+=L(xin,150,*d3)+L(*s3,*d1)+L(*s1,xin,ygnd)
    s+=L(xout,150,*d4)+L(xout,150,xout+70,150)+L(xout+70,150,xout+70,185,arrow=True)
    s+=T(xout+80,150,"I_out",12.5,SOOCH,style="italic")+T(xout+80,166,"→ load",11,MUT)
    s+=L(*s4,*d2)+L(*s2,xout,ygnd)
    yn=205
    s+=L(xb,d5[1],xb,yn)+D(xb,yn)
    rc3=g3[0]-16; rc4=g4[0]-16
    s+=L(xb,yn,rc3,yn)+L(rc3,yn,rc3,g3[1])+L(rc3,g3[1],*g3)
    s+=L(rc3,yn,rc4,yn)+hop(xin,yn)+L(rc4,yn,rc4,g4[1])+L(rc4,g4[1],*g4)
    yg=yB+58; lane=xin-70
    s+=L(xin,175,lane,175)+D(xin,175)+L(lane,175,lane,yg)
    s+=L(lane,yg,g2[0],yg)+hop(xin,yg)+L(lane,yg,g1[0],yg)+L(g1[0],yg,*g1)+L(g2[0],yg,*g2)
    s+=L(410,ygnd,900,ygnd)
    for gx in (xb,xin,xout): s+=D(gx,ygnd)
    s+=gnd(560,ygnd)
    s+=nodev(xb+14,d5[1]-2,"ncas","1.02 V",SOOCH)
    s+=nodev(xin+14,150,"iin = ng","0.77 V",SOOCH)
    s+=nodev(xin+14,yB-40,"na","0.21 V",SOOCH)
    s+=nodev(xout+14,yB-40,"nb","0.21 V",SOOCH)
    s+=nodev(xout+14,158,"vout","0.90 V",SOOCH)
    # op cards: left column M5/M3/M1, right column M4/M2
    s+=card(20,120,"M5",op["XM5"],wl["XM5"],SOOCH,(g5[0],yT),"right")
    s+=card(20,300,"M3",op["XM3"],wl["XM3"],SOOCH,(g3[0],yT),"right")
    s+=card(20,470,"M1",op["XM1"],wl["XM1"],SOOCH,(g1[0],yB),"right")
    s+=card(964,250,"M4",op["XM4"],wl["XM4"],SOOCH,(xout+8,yT),"left")
    s+=card(964,430,"M2",op["XM2"],wl["XM2"],SOOCH,(xout+8,yB),"left")
    s+=T(W/2,H-16,"V_out,min = 2V_ov = 0.34 V      R_out = 26 MΩ @ V_out=0.9 V      Σ(W·L) = 4.5 µm²   —   M5 sets ncas=V_t+2V_ov so M1,M2 sit at V_ds≈V_dsat (just saturated); cascodes keep high r_o",
            11.5,INK,anc="middle",w="bold")
    open("cm_sooch.svg","w").write(s+"</svg>\n"); print("wrote cm_sooch.svg")

cascode(); sooch()
