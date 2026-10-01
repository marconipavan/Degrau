import os, sys
RAIZ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,RAIZ)
SAIDA=os.path.join(RAIZ,'exemplos','pdf')
os.makedirs(SAIDA,exist_ok=True)
from motor.geo import FolhaGeo, M, W, H
import motor.folha as K
from reportlab.lib.units import mm
f=FolhaGeo(os.path.join(SAIDA,'G1_pacote01_folhas1-3.pdf'),'G1 — folhas 1 a 3')

# 1a — nomear
f.page('G1 1a','Reconhecer ângulos 1','Veja o exemplo. Escreva o nome de cada ângulo.','ecris','20 cada')
y0=f.exemplo(34*mm,None)
f.angulo(M+14*mm,y0-27*mm,0,50,nomes=('O','A','B'))
f.texto('ângulo AÔB',M+50*mm,y0-12*mm,12); f.texto('vértice: O',M+50*mm,y0-19*mm,11); f.texto('lados: OA e OB',M+50*mm,y0-26*mm,11)
f.c.setFont('And',8); f.c.setFillColor(K.GREY); f.c.drawString(M+50*mm,y0-32*mm,'O vértice fica sempre no meio do nome.')
base=y0-72*mm
pos=[(M+8*mm,base,0,70,('Q','P','R')),(M+75*mm,base,20,110,('M','N','T')),
     (M+8*mm,base-50*mm,0,140,('C','D','E')),(M+75*mm,base-50*mm,-30,45,('F','G','H'))]
for i,(x,y,a,b,n) in enumerate(pos):
    f.num(i+1,x-4*mm,y+22*mm); f.angulo(x+6*mm,y,a,b,nomes=n)
f.fim('G1 1a')

# 1b — classificar por valor
f.page('G1 1b','Reconhecer ângulos 1','Classifique: agudo (A), reto (R), obtuso (O) ou raso (Ra).','ecris','10 cada')
y0=f.exemplo(16*mm,None)
f.texto('35°  →  A   (menor que 90°)        90°  →  R',M+3*mm,y0-8*mm,10.5)
f.texto('120°  →  O   (entre 90° e 180°)     180°  →  Ra',M+3*mm,y0-14*mm,10.5)
vals=['40°','90°','150°','180°','89°','91°','10°','179°','60°','100°']
y=y0-30*mm
for i,v in enumerate(vals):
    col=i%2; row=i//2
    f.num(i+1,M+2*mm+col*62*mm,y-row*16*mm); f.texto(v,M+10*mm+col*62*mm,y-row*16*mm,16)
f.fim('G1 1b')

# 2a — classificar pela figura
f.page('G1 2a','Reconhecer ângulos 2','Classifique cada ângulo: A, R ou O.','ecris','15 cada')
figs=[(0,35,'arco'),(0,90,'reto'),(0,130,'arco'),(10,100,'reto'),(-20,40,'arco'),(0,160,'arco')]
for i,(a,b,mk) in enumerate(figs):
    col=i%2; row=i//2
    x=M+12*mm+col*62*mm; y=f.y-22*mm-row*42*mm
    f.num(i+1,x-9*mm,y+18*mm); f.angulo(x,y,a,b,marca=mk)
f.fim('G1 2a')

# 2b — contar/nomear ângulos com mesmo vértice
f.page('G1 2b','Reconhecer ângulos 2','Escreva todos os ângulos com vértice O.','ecris','10 cada')
y0=f.exemplo(34*mm,None)
f.raios(M+14*mm,y0-30*mm,[0,40,85],['A','B','C'],'O',L=18*mm)
f.texto('AÔB,  BÔC  e  AÔC',M+55*mm,y0-15*mm,12)
f.c.setFont('And',8.5); f.c.setFillColor(K.GREY); f.c.drawString(M+55*mm,y0-22*mm,'3 semirretas formam 3 ângulos.')
f.num(1,M+2*mm,y0-50*mm); f.raios(M+14*mm,y0-78*mm,[0,30,70,120],['P','Q','R','S'],'O',L=20*mm)
f.num(2,M+72*mm,y0-50*mm); f.raios(M+78*mm,y0-78*mm,[10,60,100,140,175],['A','B','C','D','E'],'O',L=18*mm)
f.c.setFont('And',8); f.c.setFillColor(K.GREY)
f.c.setFillColor(K.INK); f.c.setFont('And',10.5); f.c.drawString(M+72*mm,y0-100*mm,'Só diga quantos são. [40]')
f.fim('G1 2b')

# 3a — mistura por valor com contexto
f.page('G1 3a','Reconhecer ângulos 3','Qual é o tipo do ângulo? Responda A, R, O ou Ra.','ecris','10 cada')
items=['a metade de 180°','o dobro de 45°','o dobro de 60°','a metade de 90°','90° + 1°','180° − 1°','3 × 60°','o triplo de 25°','90° − 90°/2','2 × 90°']
for i,t in enumerate(items):
    f.num(i+1,M+2*mm,f.y-i*13*mm); f.texto(t,M+10*mm,f.y-i*13*mm,14)
f.fim('G1 3a')

# 3b — revisão
f.page('G1 3b','Reconhecer ângulos 3','Revisão: responda no caderno.','ecris','20 cada')
f.num(1,M+2*mm,f.y); f.texto('Qual é o vértice do ângulo XŶZ?',M+10*mm,f.y,12)
f.num(2,M+2*mm,f.y-40*mm); f.angulo(M+20*mm,f.y-55*mm,0,120,nomes=('K','L','J')); f.texto('Nome e tipo deste ângulo?',M+62*mm,f.y-45*mm,11)
f.num(3,M+2*mm,f.y-72*mm); f.texto('Um ângulo de 90° é chamado de ______ .',M+10*mm,f.y-72*mm,12)
f.num(4,M+2*mm,f.y-88*mm); f.texto('Quantos ângulos 5 semirretas de mesma origem',M+10*mm,f.y-88*mm,12)
f.texto('formam, ao todo?  (use a folha 2b)',M+10*mm,f.y-94*mm,12)
f.num(5,M+2*mm,f.y-110*mm); f.texto('O dobro de um ângulo agudo pode ser obtuso? (S/N)',M+10*mm,f.y-110*mm,12)
f.fim('G1 3b')
f.save()
