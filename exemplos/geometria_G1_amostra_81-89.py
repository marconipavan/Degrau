import os, sys
RAIZ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,RAIZ)
SAIDA=os.path.join(RAIZ,'exemplos','pdf')
os.makedirs(SAIDA,exist_ok=True)
from motor.bicos import Bico, M, W, H, GREY, INK
from reportlab.lib.units import mm
f=Bico(os.path.join(SAIDA,'G1_amostra_folhas81-89.pdf'),'G1 — amostra 81 a 89')
gab={}
def fig(yr, ys, x, segs, marks, pw=None):
    return f.zig((x,yr),segs,yr,ys,marks)

# ---------- 81a ----------
f.page('G1 81a','O bizu dos bicos 1','Veja o exemplo. Calcule x.  (r // s)','ecris','25 cada')
y0=f.exemplo(46*mm,None)
yr,ys=y0-10*mm,y0-40*mm
f.paralelas(yr,ys,M+3*mm,M+62*mm)
f.zig(M+3*mm,M+62*mm,yr,ys,[(-30,22*mm),(-140,0)],[(0,'dir',None),(1,None,'x'),(2,'dir',None)])
f.texto('bico para a direita:',M+70*mm,y0-14*mm,10.5)
f.texto('x = 30° + 40° = 70°',M+70*mm,y0-21*mm,11.5)
f.c.setFont('And',8.5); f.c.setFillColor(GREY)
f.c.drawString(M+70*mm,y0-29*mm,'O ângulo do bico é a soma'); f.c.drawString(M+70*mm,y0-33.5*mm,'dos ângulos nas paralelas.')
ex=[(-35,-140),(-50,-145),(-30,-130),(-45,-135)]
for i,(d1,d2) in enumerate(ex):
    col=i%2; row=i//2
    bx=M+col*65*mm; by=y0-62*mm-row*48*mm
    yr,ys=by,by-30*mm
    f.num(i+1,bx+1*mm,yr+4*mm); f.paralelas(yr,ys,bx+4*mm,bx+58*mm)
    v=f.zig(bx+4*mm,bx+58*mm,yr,ys,[(d1,18*mm),(d2,0)],[(0,'dir',None),(1,None,'x'),(2,'dir',None)])
    gab[f'81a-{i+1}']=v[1]
f.fim('G1 81a')

# ---------- 81b ----------
f.page('G1 81b','O bizu dos bicos 1','Agora o x está na paralela. Calcule x.','ecris','25 cada')
ex=[(-40,-145,'p'),(-55,-150,'q'),(-30,-135,'p'),(-40,-130,'q')]
for i,(d1,d2,alvo) in enumerate(ex):
    col=i%2; row=i//2
    bx=M+col*65*mm; by=f.y-8*mm-row*55*mm
    yr,ys=by,by-32*mm
    f.num(i+1,bx+1*mm,yr+4*mm); f.paralelas(yr,ys,bx+4*mm,bx+58*mm)
    marks=[(0,'dir','x' if alvo=='p' else None),(1,None,None),(2,'dir','x' if alvo=='q' else None)]
    v=f.zig(bx+4*mm,bx+58*mm,yr,ys,[(d1,18*mm),(d2,0)],marks)
    gab[f'81b-{i+1}']=v[0] if alvo=='p' else v[2]
f.fim('G1 81b')

# ---------- 85a ----------
f.page('G1 85a','O bizu dos bicos 5','Dois bicos. Veja o exemplo e calcule x.','ecris','25 cada')
y0=f.exemplo(56*mm,None)
yr,ys=y0-8*mm,y0-50*mm
f.paralelas(yr,ys,M+3*mm,M+62*mm)
f.zig(M+3*mm,M+62*mm,yr,ys,[(-20,18*mm),(-150,18*mm),(-40,0)],[(0,'dir',None),(1,None,None),(2,None,None),(3,'esq',None)])
f.texto('abrem para a esquerda:',M+68*mm,y0-12*mm,10); f.texto('50° + 40° = 90°',M+72*mm,y0-17.5*mm,10.5)
f.texto('abrem para a direita:',M+68*mm,y0-24*mm,10); f.texto('20° + 70° = 90°',M+72*mm,y0-29.5*mm,10.5)
f.texto('as duas somas são iguais',M+68*mm,y0-36*mm,10)
f.c.setFont('And',8.5); f.c.setFillColor(GREY)
f.c.drawString(M+68*mm,y0-42*mm,'Olhe para onde cada ângulo abre.')
ex=[((-25,-145,-40),2),((-30,-150,-50),1),((-20,-140,-45),3),((-35,-150,-40),0)]
for i,((a,b,cc),alvo) in enumerate(ex):
    col=i%2; row=i//2
    bx=M+col*65*mm; by=y0-70*mm-row*50*mm
    yr,ys=by,by-38*mm
    f.num(i+1,bx+1*mm,yr+4*mm); f.paralelas(yr,ys,bx+4*mm,bx+58*mm)
    marks=[(0,'dir',None),(1,None,None),(2,None,None),(3,'esq',None)]
    marks=[(vi,w,('x' if vi==alvo else None)) for vi,w,_ in marks]
    v=f.zig(bx+4*mm,bx+58*mm,yr,ys,[(a,15*mm),(b,15*mm),(cc,0)],marks,size=8.8)
    gab[f'85a-{i+1}']=v[alvo]
f.fim('G1 85a')

# ---------- 85b ----------
f.page('G1 85b','O bizu dos bicos 5','Calcule x. Some os ângulos de cada lado.','ecris','25 cada')
ex=[((-30,-150,-40),1),((-20,-150,-35),2),((-40,-140,-35),0),((-25,-150,-50),3)]
for i,((a,b,cc),alvo) in enumerate(ex):
    col=i%2; row=i//2
    bx=M+col*65*mm; by=f.y-6*mm-row*58*mm
    yr,ys=by,by-42*mm
    f.num(i+1,bx+1*mm,yr+4*mm); f.paralelas(yr,ys,bx+4*mm,bx+58*mm)
    marks=[(vi,w,('x' if vi==alvo else None)) for vi,w in [(0,'dir'),(1,None),(2,None),(3,'esq')]]
    v=f.zig(bx+4*mm,bx+58*mm,yr,ys,[(a,15*mm),(b,15*mm),(cc,0)],marks,size=8.8)
    gab[f'85b-{i+1}']=v[alvo]
f.fim('G1 85b')

# ---------- 89a ----------
f.page('G1 89a','O bizu dos bicos 9','Monte a equação e calcule x.','ecris','50 cada')
# figura 1: valores reais 20 (P), 50 (V1), 70 (V2), 40 (Q) -> rótulos em x com x=15? escolher: 20=x+5, 50=3x+5, 70=5x-5, 40 = 2x+10  (x=15)
yr,ys=f.y-4*mm,f.y-50*mm
f.num(1,M+1*mm,yr+4*mm); f.paralelas(yr,ys,M+6*mm,W-M-40*mm)
v=f.zig(M+6*mm,W-M-40*mm,yr,ys,[(-20,20*mm),(-150,20*mm),(-40,0)],[(0,'dir','x + 5°'),(1,None,'3x + 5°'),(2,None,'5x − 5°'),(3,'esq','2x + 10°')],size=9.5)
gab['89a-1']=15; assert v=={0:20,1:50,2:70,3:40},v
# figura 2: um bico, valores 35 (P), 80 (V), 45 (Q): 2x+5=35 -> x=15; 5x+5=80; 3x=45
yr,ys=f.y-72*mm,f.y-108*mm
f.num(2,M+1*mm,yr+4*mm); f.paralelas(yr,ys,M+6*mm,W-M-40*mm)
v=f.zig(M+6*mm,W-M-40*mm,yr,ys,[(-35,22*mm),(-135,0)],[(0,'dir','3x + 5°'),(1,None,'8x'),(2,'dir','4x + 5°')],size=9.5)
assert v=={0:35,1:80,2:45},v; gab['89a-2']=10
f.fim('G1 89a')

# ---------- 89b ----------
f.page('G1 89b','O bizu dos bicos 9','Questão de prova. Marque a alternativa.','ecris','100')
f.c.setFont('And',11); f.c.setFillColor(INK)
for k,l in enumerate(['Na figura, as retas r e s são paralelas.','O valor de x é:']):
    f.c.drawString(M+2*mm,f.y-k*6*mm,l)
yr,ys=f.y-20*mm,f.y-72*mm
f.paralelas(yr,ys,M+6*mm,W-M-30*mm)
# valores reais: 25 (P), 55 (V1), 80 (V2 esq), 50 (Q) -> checagem: dir: V1 55 + Q? calcular pela geometria
v=f.zig(M+6*mm,W-M-30*mm,yr,ys,[(-25,20*mm),(-150,22*mm),(-50,0)],[(0,'dir','x'),(1,None,'2x + 5°'),(2,None,'80°'),(3,'esq','2x')],size=9.5)
assert v=={0:25,1:55,2:80,3:50},v; gab['89b']='C (25°)'
f.c.setFont('And',12); f.c.setFillColor(INK)
alts=['(A) 15°','(B) 20°','(C) 25°','(D) 30°']
for k,a in enumerate(alts): f.c.drawString(M+4*mm+k*31*mm,ys-16*mm,a)
f.fim('G1 89b')
f.save()
print('gabarito:',gab)
