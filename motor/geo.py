import math
from . import folha as K
from .folha import Folha, icon, INK, GREY, RULE, M, W, H
from reportlab.lib.units import mm

class FolhaGeo(Folha):
    MARCA='DEGRAU  ·  geometria'
    def page(self,code,unite,instr,icone,points=None):
        c=self.c
        c.setFont('Sans',6.3); c.setFillColor(GREY); c.drawString(M,H-M,self.MARCA)
        c.setFillColor(INK); c.setFont('AndB',15); c.drawString(M,H-M-7*mm,code)
        cw=c.stringWidth(code,'AndB',15)
        c.setFont('And',9.5); c.drawString(M+cw+4*mm,H-M-7*mm,unite)
        c.setFont('And',7.2); c.setFillColor(GREY)
        c.drawRightString(W-M,H-M-2*mm,'No caderno, anote:')
        c.drawRightString(W-M,H-M-6*mm,f'{code}  ·  início  ·  fim')
        c.setStrokeColor(INK); c.setLineWidth(.8); c.line(M,H-M-10*mm,W-M,H-M-10*mm)
        iy=H-M-17*mm
        icon(c,icone,M+4.2*mm,iy+1.2*mm)
        c.setFont('AndB',11); c.setFillColor(INK); c.drawString(M+11*mm,iy+0.6*mm,instr)
        if points: c.setFont('And',8); c.drawRightString(W-M,iy-4*mm,f'[{points}]')
        self.y=iy-10*mm
    # figura de ângulo: vértice (x,y), direções em graus
    def angulo(self,x,y,d1,d2,L=18*mm,nomes=None,marca='arco',rot=None,r=5*mm):
        c=self.c; c.setFillColor(INK); c.setStrokeColor(INK); c.setLineWidth(1)
        for d in (d1,d2):
            c.line(x,y,x+L*math.cos(math.radians(d)),y+L*math.sin(math.radians(d)))
        c.circle(x,y,.8*mm,fill=1,stroke=0)
        a,b=min(d1,d2),max(d1,d2)
        if marca=='reto':
            u=(math.cos(math.radians(a)),math.sin(math.radians(a))); v=(math.cos(math.radians(b)),math.sin(math.radians(b)))
            s=3*mm; p1=(x+u[0]*s,y+u[1]*s); p2=(x+(u[0]+v[0])*s,y+(u[1]+v[1])*s); p3=(x+v[0]*s,y+v[1]*s)
            c.setLineWidth(.7); c.line(*p1,*p2); c.line(*p2,*p3)
        elif marca=='arco':
            c.setLineWidth(.7); c.arc(x-r,y-r,x+r,y+r,a,b-a)
        if rot:
            m=math.radians((a+b)/2); c.setFont('And',9.5); c.setFillColor(INK)
            c.drawCentredString(x+(r+4*mm)*math.cos(m),y+(r+4*mm)*math.sin(m)-1.2*mm,rot)
        if nomes:
            c.setFont('AndB',10); c.setFillColor(INK)
            v,p,q=nomes
            c.drawString(x-3.2*mm,y-3.5*mm,v)
            for d,n in ((d1,p),(d2,q)):
                c.drawCentredString(x+(L+3*mm)*math.cos(math.radians(d)),y+(L+3*mm)*math.sin(math.radians(d))-1.2*mm,n)
    def raios(self,x,y,dirs,nomes,vert,L=20*mm):
        c=self.c; c.setFillColor(INK); c.setStrokeColor(INK); c.setLineWidth(1)
        for d,n in zip(dirs,nomes):
            c.line(x,y,x+L*math.cos(math.radians(d)),y+L*math.sin(math.radians(d)))
            c.setFont('AndB',10); c.drawCentredString(x+(L+3*mm)*math.cos(math.radians(d)),y+(L+3*mm)*math.sin(math.radians(d))-1.2*mm,n)
        c.circle(x,y,.8*mm,fill=1,stroke=0); c.setFillColor(INK); c.drawString(x-3.5*mm,y-3.5*mm,vert)
    def num(self,n,x,y):
        c=self.c; c.setFont('And',8.5); c.setFillColor(GREY); c.drawString(x,y,str(n))
    def texto(self,t,x,y,size=11):
        c=self.c; c.setFont('And',size); c.setFillColor(INK); c.drawString(x,y,t)
    def exemplo(self,h,linhas):
        c=self.c; y0=self.y
        c.setStrokeColor(K.LIGHT); c.setLineWidth(.8); c.roundRect(M,y0-h,W-2*M,h+4*mm,2*mm)
        c.setFont('AndB',9.5); c.setFillColor(INK); c.drawString(M+3*mm,y0-2*mm,'Exemplo')
        return y0
