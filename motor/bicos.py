import math
from .geo import FolhaGeo, M, W, H, INK, GREY
from reportlab.lib.units import mm

def build_path(P, segs, ys):
    pts=[P]; dirs=[]
    x,y=P
    for i,(d,L) in enumerate(segs):
        dx,dy=math.cos(math.radians(d)),math.sin(math.radians(d))
        if i==len(segs)-1: L=(ys-y)/dy
        x,y=x+dx*L,y+dy*L; pts.append((x,y)); dirs.append(d)
    return pts,dirs

def arc_between(a,b):
    a%=360; b%=360; d=(b-a)%360
    return (a,d) if d<=180 else (b,360-d)

class Bico(FolhaGeo):
    def paralelas(self, yr, ys, x0=None, x1=None):
        c=self.c; x0=x0 or M+2*mm; x1=x1 or W-M-6*mm
        c.setStrokeColor(INK); c.setLineWidth(1)
        c.line(x0,yr,x1,yr); c.line(x0,ys,x1,ys)
        c.setFont('AndB',10); c.setFillColor(INK); c.drawString(x1+1.5*mm,yr-1.2*mm,'r'); c.drawString(x1+1.5*mm,ys-1.2*mm,'s')
    def zig(self, xa, xb, yr, ys, segs, marks, r=4.5*mm, size=9.5):
        """centraliza a poligonal entre xa e xb; marks: (índice do vértice, lado 'dir'/'esq' nas pontas, rótulo)"""
        c=self.c; pts,dirs=build_path((0,yr),segs,ys)
        xs=[p[0] for p in pts]; sh=(xa+xb)/2-(min(xs)+max(xs))/2
        pts=[(x+sh,y) for x,y in pts]
        c.setStrokeColor(INK); c.setLineWidth(1)
        for i in range(len(pts)-1): c.line(*pts[i],*pts[i+1])
        vals={}
        for vi,which,lab in marks:
            x,y=pts[vi]
            if vi==0:
                a=0 if which=='dir' else 180; b=dirs[0]
            elif vi==len(pts)-1:
                a=0 if which=='dir' else 180; b=dirs[-1]+180
            else:
                a=dirs[vi-1]+180; b=dirs[vi]
            s,e=arc_between(a,b); vals[vi]=round(e)
            c.setLineWidth(.7); c.arc(x-r,y-r,x+r,y+r,s,e)
            m=math.radians(s+e/2); txt=lab if lab is not None else f'{round(e)}°'
            tw=c.stringWidth(txt,'And',size)
            rr=r+2.8*mm+0.5*tw*abs(math.cos(m))+ (1.2*mm if e<35 else 0)
            c.setFont('And',size); c.setFillColor(INK)
            c.drawCentredString(x+rr*math.cos(m),y+rr*math.sin(m)-1.3*mm,txt)
        return vals
