# Degrau — motor das folhas (A5, frente e verso, uma tarefa por página)
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import random, os

F=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fonts')+os.sep
pdfmetrics.registerFont(TTFont('And', F+'Andika-Regular.ttf'))
pdfmetrics.registerFont(TTFont('AndB', F+'Andika-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Sans', F+'Andika-Regular.ttf'))

W,H=A5
M=10*mm
INK=colors.HexColor('#1d1d1f'); GREY=colors.HexColor('#8a8f98'); LIGHT=colors.HexColor('#c9ccd2')
TRACE=colors.HexColor('#cfd3da'); ACC=colors.HexColor('#1f4e9c'); RULE=colors.HexColor('#b8bcc4')
LIMITE=M+8*mm   # nenhum bloco desce abaixo disto (o rodapé fica em M-3mm)
ESPACO=4*mm     # espaço depois de um bloco elástico

def icon(c,kind,x,y,r=4.2*mm):
    c.saveState(); c.setStrokeColor(INK); c.setFillColor(INK); c.setLineWidth(1)
    c.circle(x,y,r,stroke=1,fill=0)
    s=r*0.45
    if kind=='ouvir':      # alto-falante
        p=c.beginPath(); p.moveTo(x-s*1.1,y-s*0.45); p.lineTo(x-s*0.45,y-s*0.45); p.lineTo(x+s*0.25,y-s*1.0)
        p.lineTo(x+s*0.25,y+s*1.0); p.lineTo(x-s*0.45,y+s*0.45); p.lineTo(x-s*1.1,y+s*0.45); p.close(); c.drawPath(p,fill=1,stroke=0)
        c.arc(x+s*0.1,y-s*0.7,x+s*1.1,y+s*0.7,-50,100)
    elif kind=='escrever':     # lápis
        c.translate(x,y); c.rotate(45)
        c.rect(-s*1.2,-s*0.3,s*1.8,s*0.6,stroke=1,fill=0)
        p=c.beginPath(); p.moveTo(s*0.6,-s*0.3); p.lineTo(s*1.2,0); p.lineTo(s*0.6,s*0.3); p.close(); c.drawPath(p,fill=1,stroke=0)
    elif kind=='ligar':     # dois pontos ligados
        c.circle(x-s,y-s*0.5,s*0.28,fill=1,stroke=0); c.circle(x+s,y+s*0.5,s*0.28,fill=1,stroke=0)
        c.line(x-s,y-s*0.5,x+s,y+s*0.5)
    elif kind=='circular':   # oval
        c.ellipse(x-s*1.1,y-s*0.6,x+s*1.1,y+s*0.6,stroke=1,fill=0)
    elif kind=='ler':       # livro aberto
        c.line(x,y-s*0.8,x,y+s*0.8)
        c.rect(x-s*1.1,y-s*0.7,s*1.1,s*1.4,stroke=1,fill=0); c.rect(x,y-s*0.7,s*1.1,s*1.4,stroke=1,fill=0)
    c.restoreState()

class Folha:
    MARCA='DEGRAU  ·  français'
    def __init__(self,path,titre_doc):
        self.c=canvas.Canvas(path,pagesize=A5,invariant=1); self.c.setTitle(titre_doc); self.c.setAuthor('Degrau')
    def pagina(self,code,unite,instr,gloss,icone,points=None):
        c=self.c
        # cabeçalho
        c.setFillColor(INK); c.setFont('AndB',15); c.drawString(M,H-M-7*mm,code)
        cw=c.stringWidth(code,'AndB',15)
        fx0=W-M-52*mm; us=9.5
        while us>6.5 and c.stringWidth(unite,'And',us)>fx0-(M+cw+4*mm)-5*mm: us-=0.25
        c.setFont('And',us); c.setFillColor(INK); c.drawString(M+cw+4*mm,H-M-7*mm,unite)
        c.setFont('Sans',6.3); c.setFillColor(GREY); c.drawString(M,H-M,self.MARCA)
        # campos
        fx=W-M-52*mm; fy=H-M-1.5*mm
        c.setFont('And',7.5); c.setFillColor(INK)
        c.drawString(fx,fy,'Nom'); c.setStrokeColor(RULE); c.setLineWidth(.5); c.line(fx+8*mm,fy-1,W-M,fy-1)
        c.drawString(fx,fy-4.5*mm,'Date'); c.drawString(fx+8*mm,fy-4.5*mm,'      /       /')
        c.drawString(fx,fy-9*mm,'Début'); c.drawString(fx+10*mm,fy-9*mm,'     :'); c.drawString(fx+27*mm,fy-9*mm,'Fin'); c.drawString(fx+34*mm,fy-9*mm,'     :')
        c.setStrokeColor(INK); c.setLineWidth(.8); c.line(M,H-M-12*mm,W-M,H-M-12*mm)
        # instrução
        iy=H-M-19*mm
        icon(c,icone,M+4.2*mm,iy+1.2*mm)
        c.setFont('AndB',11.5); c.setFillColor(INK); c.drawString(M+11*mm,iy+1.8*mm,instr)
        if gloss:
            c.setFont('And',7.5); c.setFillColor(GREY); c.drawString(M+11*mm,iy-2.2*mm,gloss)
        if points:
            c.setFont('And',8); c.setFillColor(INK)
            if M+11*mm+c.stringWidth(instr,'AndB',11.5)>W-M-c.stringWidth(f'[{points}]','And',8)-3*mm:
                c.drawRightString(W-M,iy-2.2*mm,f'[{points}]')
            else: c.drawRightString(W-M,iy+1.8*mm,f'[{points}]')
        self.y=iy-10*mm
    def fim(self,code):
        c=self.c; c.setFont('And',7); c.setFillColor(GREY); c.drawRightString(W-M,M-3*mm,code); c.showPage()

    # ---------- tipos de exercício ----------
    # Blocos elásticos (itens espaçados) recebem a altura disponível e usam
    # passo = min(máximo, altura/n); sem altura, ocupam até o LIMITE.
    # Abaixo do mínimo os itens se sobrepõem: erro em vez de desenhar.
    def _passo(self,n,maximo,altura,minimo):
        altura=self.y-LIMITE if altura is None else altura
        step=altura/n if maximo is None else min(maximo,altura/n)
        if step<minimo: raise ValueError(f'não cabe: {n} itens pedem pelo menos {n*minimo/mm:.0f} mm, há {altura/mm:.0f} mm')
        return step
    def _avanca(self,n,step): self.y-=n*step+ESPACO
    def palavras(self,itens,cols=2,size=19,altura=None):
        c=self.c; colw=(W-2*M)/cols; nl=-(-len(itens)//cols); rowh=self._passo(nl,24*mm,altura,14*mm)
        for i,(fr,pt) in enumerate(itens):
            col=i%cols; row=i//cols
            x=M+col*colw+2*mm; y=self.y-row*rowh
            c.setFont('And',7.5); c.setFillColor(GREY); c.drawString(x,y,f'{i+1}')
            c.setFont('And',size); c.setFillColor(INK); c.drawString(x+5*mm,y-3*mm,fr)
            c.setFont('And',8); c.setFillColor(GREY); c.drawString(x+5*mm,y-8.5*mm,pt)
        self._avanca(nl,rowh)
    def ligar(self,pares,seed=1,altura=None):
        c=self.c; rnd=random.Random(seed); dir_=[p[1] for p in pares]; rnd.shuffle(dir_)
        step=self._passo(len(pares),None,altura,9*mm)
        for i,(fr,_) in enumerate(pares):
            y=self.y-i*step
            c.setFont('And',15); c.setFillColor(INK); c.drawString(M+2*mm,y,fr)
            c.circle(M+52*mm,y+1.6*mm,1.1*mm,fill=1,stroke=0)
            c.circle(W-M-48*mm,y+1.6*mm,1.1*mm,fill=1,stroke=0)
            c.setFont('And',12); c.drawString(W-M-44*mm,y,dir_[i])
        self._avanca(len(pares),step)
    def circular(self,linhas,altura=None):
        c=self.c; step=self._passo(len(linhas),17*mm,altura,9*mm)
        for i,opts in enumerate(linhas):
            y=self.y-i*step
            c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+1*mm,y,f'{i+1}')
            colw=(W-2*M-10*mm)/len(opts)
            for j,o in enumerate(opts):
                c.setFont('And',15); c.setFillColor(INK); c.drawString(M+10*mm+j*colw,y,o)
        self._avanca(len(linhas),step)
    def copiar(self,mots,size=20,altura=None):
        c=self.c; step=self._passo(len(mots),19*mm,altura,10*mm)
        for i,m in enumerate(mots):
            y=self.y-i*step
            c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+1*mm,y,f'{i+1}')
            c.setFont('And',size); c.setFillColor(TRACE); c.drawString(M+7*mm,y,m)
            w=c.stringWidth(m,'And',size)
            c.setStrokeColor(RULE); c.setLineWidth(.6); c.line(M+7*mm,y-2*mm,M+7*mm+w,y-2*mm)
            c.line(M+w+14*mm,y-2*mm,W-M,y-2*mm)
        self._avanca(len(mots),step)
    def frases(self,frases,size=15,gloss=None,altura=None):
        c=self.c; step=self._passo(len(frases),19*mm,altura,11*mm if gloss else 8*mm)
        for i,f in enumerate(frases):
            y=self.y-i*step
            c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+1*mm,y,f'{i+1}')
            c.setFont('And',size); c.setFillColor(INK); c.drawString(M+7*mm,y,f)
            if gloss:
                c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+7*mm,y-5*mm,gloss[i])
        self._avanca(len(frases),step)
    def banco(self,mots):
        c=self.c; bw=W-2*M; bh=11*mm
        c.setStrokeColor(INK); c.setLineWidth(.7); c.roundRect(M,self.y-bh+4*mm,bw,bh,2*mm)
        c.setFont('And',13); c.setFillColor(INK)
        gap=bw/len(mots)
        for i,m in enumerate(mots): c.drawCentredString(M+gap*(i+.5),self.y-3.5*mm,m)
        self.y-=bh+6*mm
    def lacunas(self,frases,size=14,altura=None):
        c=self.c; step=self._passo(len(frases),18*mm,altura,10*mm)
        for i,f in enumerate(frases):
            y=self.y-i*step; x=M+7*mm
            c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+1*mm,y,f'{i+1}')
            partes=f.split('___')
            for k,p in enumerate(partes):
                c.setFont('And',size); c.setFillColor(INK); c.drawString(x,y,p); x+=c.stringWidth(p,'And',size)
                if k<len(partes)-1:
                    c.setStrokeColor(INK); c.setLineWidth(.7); c.rect(x+1*mm,y-2.2*mm,28*mm,8*mm); x+=30*mm
        self._avanca(len(frases),step)
    def leitura(self,linhas,fois=3,size=14):
        c=self.c; y=self.y
        c.setFont('And',9); c.setFillColor(INK); c.drawString(M,y,'Lu à voix haute :')
        for k in range(fois):
            c.setStrokeColor(INK); c.setLineWidth(.7); c.rect(M+30*mm+k*9*mm,y-1*mm,5*mm,5*mm)
        y-=10*mm
        for l in linhas:
            c.setFont('And',size); c.setFillColor(INK); c.drawString(M+2*mm,y,l); y-=8.5*mm
        self.y=y
    def verdadeiro_falso(self,frases,size=13.5,altura=None):
        c=self.c; step=self._passo(len(frases),15*mm,altura,8*mm)
        for i,f in enumerate(frases):
            y=self.y-i*step
            c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+1*mm,y,f'{i+1}')
            c.setFont('And',size); c.setFillColor(INK); c.drawString(M+7*mm,y,f)
            c.setFont('AndB',13); c.drawString(W-M-18*mm,y,'V'); c.drawString(W-M-8*mm,y,'F')
        self._avanca(len(frases),step)
    def ditado(self,n,num0=1,titre=None,gloss=None):
        c=self.c
        if titre:
            icon(c,'ouvir',M+4.2*mm,self.y+1.2*mm)
            c.setFont('AndB',11.5); c.setFillColor(INK); c.drawString(M+11*mm,self.y+1.8*mm,titre)
            if gloss: c.setFont('And',7.5); c.setFillColor(GREY); c.drawString(M+11*mm,self.y-2.2*mm,gloss)
            self.y-=12*mm
        for i in range(n):
            y=self.y-i*14*mm
            c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+1*mm,y,f'{num0+i}')
            c.setStrokeColor(RULE); c.setLineWidth(.6); c.line(M+7*mm,y-2*mm,W-M,y-2*mm)
        self.y-=n*14*mm
    def save(self): self.c.save()

from reportlab.lib.utils import simpleSplit
def _wrap(c,txt,font,size,x,y,width,lead):
    for l in simpleSplit(txt,font,size,width):
        c.drawString(x,y,l); y-=lead
    return y
def texto(self,paras,size=12,lead=None,box=False):
    c=self.c; lead=lead or size*1.55; x=M+2*mm; w=W-2*M-4*mm
    y0=self.y; y=self.y
    c.setFont('And',size); c.setFillColor(INK)
    for p in paras:
        y=_wrap(c,p,'And',size,x+(3*mm if box else 0),y,w-(6*mm if box else 0),lead)-lead*0.35
    if box:
        b=y+lead*0.35-1*mm; t=y0+size*0.85+2.5*mm
        c.setStrokeColor(INK); c.setLineWidth(.7); c.roundRect(M,b,W-2*M,t-b,2*mm)
        self.y=b-9*mm
    else: self.y=y-3*mm
def exemplo_frase(self,titre,phrase,decomp,size=11):
    c=self.c; x=M+3*mm; w=W-2*M-6*mm; y0=self.y; y=self.y
    c.setFont('AndB',9.5); c.setFillColor(INK); c.drawString(x,y,titre); y-=6*mm
    c.setFont('And',size); y=_wrap(c,phrase,'And',size,x,y,w,size*1.45)-1.5*mm
    for d in decomp:
        c.setFont('And',size-0.5); y=_wrap(c,d,'And',size-0.5,x+4*mm,y,w-4*mm,size*1.4)
    c.setStrokeColor(LIGHT); c.setLineWidth(.8); c.roundRect(M,y+1*mm,W-2*M,y0-y+4*mm,2*mm)
    self.y=y-6*mm
def perguntas(self,qs,size=11,lignes=2,num0=1):
    c=self.c; x=M+7*mm; w=W-M-x
    for i,(q,nl) in enumerate(qs):
        nl=nl or lignes
        c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+1*mm,self.y,f'{num0+i}')
        c.setFont('And',size); c.setFillColor(INK)
        y=_wrap(c,q,'And',size,x,self.y,w,size*1.4)
        for k in range(nl):
            y-=6.5*mm; c.setStrokeColor(RULE); c.setLineWidth(.6); c.line(x,y,W-M,y)
        self.y=y-6*mm
def subinstrucao(self,icone,txt,points=None):
    c=self.c
    icon(c,icone,M+4.2*mm,self.y+1.2*mm)
    c.setFont('AndB',10.5); c.setFillColor(INK); c.drawString(M+11*mm,self.y+0.6*mm,txt)
    if points: c.setFont('And',8); c.drawRightString(W-M,self.y+0.6*mm,f'[{points}]')
    self.y-=9*mm
def ordenar(self,frases,size=11):
    c=self.c
    for f in frases:
        c.setStrokeColor(INK); c.setLineWidth(.7); c.rect(M+1*mm,self.y-1.5*mm,6*mm,6*mm)
        c.setFont('And',size); c.setFillColor(INK); c.drawString(M+10*mm,self.y,f); self.y-=9*mm
for _n in ['texto','exemplo_frase','perguntas','subinstrucao','ordenar']: setattr(Folha,_n,globals()[_n])

def decompor(self,num,phrase,parts,size=11):
    c=self.c; x=M+7*mm; w=W-M-x
    c.setFont('And',8); c.setFillColor(GREY); c.drawString(M+1*mm,self.y,str(num))
    c.setFont('And',size); c.setFillColor(INK)
    y=_wrap(c,phrase,'And',size,x,self.y,w,size*1.4)-2.5*mm
    for p in parts:
        c.setFont('And',size-0.5); c.drawString(x+3*mm,y,p)
        pw=c.stringWidth(p,'And',size-0.5)
        c.setStrokeColor(RULE); c.setLineWidth(.6); c.line(x+3*mm+pw+1.5*mm,y-1*mm,W-M,y-1*mm)
        y-=9*mm
    self.y=y-3*mm
Folha.decompor=decompor

