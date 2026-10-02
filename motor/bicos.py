import math
from .geo import FolhaGeo, M, W, H, INK, GREY
from reportlab.lib.units import mm

from .figuras import cruza, sobrepoe as _sobrepoe, rotular, caminho_bico as build_path   # cruza: usada também por verificar.py
from .medidas import arco as arc_between, arco_bico as arco_marca, minutos, gms_rotulo

class Bico(FolhaGeo):
    def paralelas(self, yr, ys, x0=None, x1=None):
        c=self.c; x0=x0 or M+2*mm; x1=x1 or W-M-6*mm
        c.setStrokeColor(INK); c.setLineWidth(1)
        c.line(x0,yr,x1,yr); c.line(x0,ys,x1,ys)
        self._retas=[(x0,yr,x1,yr),(x0,ys,x1,ys)]
        c.setFont('AndB',10); c.setFillColor(INK); c.drawString(x1+1.5*mm,yr-1.2*mm,'r'); c.drawString(x1+1.5*mm,ys-1.2*mm,'s')
    def desenhar_bico(self, xa, xb, yr, ys, segs, marks, r=4.5*mm, size=9.5):
        """centraliza a poligonal entre xa e xb; marks: (índice do vértice, lado 'dir'/'esq' nas pontas, rótulo)"""
        c=self.c; pts,dirs=build_path((0,yr),segs,ys)
        xs=[p[0] for p in pts]; sh=(xa+xb)/2-(min(xs)+max(xs))/2
        pts=[(x+sh,y) for x,y in pts]
        if min(p[0] for p in pts)<xa-0.5 or max(p[0] for p in pts)>xb+0.5:
            raise ValueError('bico mais largo que o espaço: use direções mais íngremes ou segmentos menores')
        c.setStrokeColor(INK); c.setLineWidth(1)
        for i in range(len(pts)-1): c.line(*pts[i],*pts[i+1])
        proprias=[(*pts[i],*pts[i+1]) for i in range(len(pts)-1)]+getattr(self,'_retas',[])
        linhas=proprias+getattr(self,'_linhas_figuras',[])
        rotulos=getattr(self,'_ocupados',[]); vals={}
        for vi,which,lab in marks:
            x,y=pts[vi]
            s,e=arco_marca(dirs,vi,which); vals[vi]=minutos(e)
            rotular(c,x,y,s,e,lab if lab is not None else gms_rotulo(minutos(e)),linhas,rotulos,r=r,size=size)
        if hasattr(self,'_linhas_figuras'): self._linhas_figuras.extend(proprias)
        return vals
