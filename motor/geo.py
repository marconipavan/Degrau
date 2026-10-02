import math
from reportlab.lib.utils import simpleSplit
from . import folha as K
from .folha import Folha, icon, INK, GREY, RULE, M, W, H, LIMITE, ESPACO
from reportlab.lib.units import mm
from .medidas import arco
from .figuras import rotular, desenhar_cruzadas, desenhar_transversal, escala_bico, nome_do_vertice, Medidor, sobrepoe

# estilos de texto no quadro de exemplo e nas células: (tamanho, cor)
ESTILOS = {'normal': (10.5, INK), 'destaque': (12, INK), 'nota': (8.5, GREY)}
EXTRA_MAX_TEXTO = 8 * mm     # grade só de texto não se espalha além disto por linha


def _dir(d): return math.cos(math.radians(d)), math.sin(math.radians(d))


def _caixa(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


class FolhaGeo(Folha):
    MARCA='DEGRAU  ·  geometria'
    def pagina(self,code,unite,instr,icone,points=None,bloco=None):
        c=self.c
        c.setFont('Sans',6.3); c.setFillColor(GREY); c.drawString(M,H-M,self.MARCA)
        c.setFillColor(INK); c.setFont('AndB',15); c.drawString(M,H-M-7*mm,code)
        cw=c.stringWidth(code,'AndB',15)
        c.setFont('And',9.5); c.drawString(M+cw+4*mm,H-M-7*mm,unite)
        c.setFont('And',7.2); c.setFillColor(GREY)
        # o código do bloco vai para o formulário; folha avulsa (exemplos) não tem bloco
        c.drawRightString(W-M,H-M-2*mm,f'Bloco {bloco}  ·  no caderno, anote:' if bloco else 'No caderno, anote:')
        c.drawRightString(W-M,H-M-6*mm,f'{code}  ·  início  ·  fim')
        c.setStrokeColor(INK); c.setLineWidth(.8); c.line(M,H-M-10*mm,W-M,H-M-10*mm)
        iy=H-M-17*mm
        icon(c,icone,M+4.2*mm,iy+1.2*mm)
        c.setFont('AndB',11); c.setFillColor(INK); c.drawString(M+11*mm,iy+0.6*mm,instr)
        if points: c.setFont('And',8); c.drawRightString(W-M,iy-4*mm,f'[{points}]')
        self.y=iy-10*mm
        self._ocupados=[]   # rótulos já escritos na página: os seguintes desviam deles
        self._linhas_figuras=[]   # linhas das figuras já desenhadas (rótulo de uma figura não encosta na vizinha)
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
    def semirretas(self,x,y,dirs,nomes,vert,L=20*mm,marcas=(),tracejadas=()):
        """marcas: [[P, Q, arco|reto|~, rótulo]] entre as semirretas P e Q; tracejadas: nomes desenhados tracejados"""
        c=self.c; c.setFillColor(INK); c.setStrokeColor(INK); c.setLineWidth(1)
        linhas=[]; ocupados=getattr(self,'_ocupados',[])
        for d,n in zip(dirs,nomes):
            seg=(x,y,x+L*math.cos(math.radians(d)),y+L*math.sin(math.radians(d)))
            if n in tracejadas: c.setDash(2,1.5)
            c.line(*seg); c.setDash(); linhas.append(seg)
            c.setFont('AndB',10); tw=c.stringWidth(n,'AndB',10)
            for extra in (3,6.5,10):   # semirretas muito próximas: o nome vai um pouco mais para fora
                px,py=x+(L+extra*mm)*math.cos(math.radians(d)),y+(L+extra*mm)*math.sin(math.radians(d))-1.2*mm
                cx=(px-tw/2-0.5*mm,py-0.5*mm,px+tw/2+0.5*mm,py+3.5*mm)
                if not any(sobrepoe(cx,o) for o in ocupados): break
            c.drawCentredString(px,py,n); ocupados.append(cx)
        c.circle(x,y,.8*mm,fill=1,stroke=0)
        nome_do_vertice(c,x,y,vert,dirs,linhas,padrao=(x-3.5*mm,y-3.5*mm))
        direcao=dict(zip(nomes,dirs))
        for i,m in enumerate(marcas):
            p,q,tipo=m[0],m[1],m[2] if len(m)>2 else None
            rot=m[3] if len(m)>3 else None
            ini,ab=arco(direcao[p],direcao[q])
            if tipo=='reto':
                u=_dir(ini); v=_dir(ini+ab); s=3*mm
                c.setStrokeColor(INK); c.setLineWidth(.7)
                c.line(x+u[0]*s,y+u[1]*s,x+(u[0]+v[0])*s,y+(u[1]+v[1])*s); c.line(x+(u[0]+v[0])*s,y+(u[1]+v[1])*s,x+v[0]*s,y+v[1]*s)
            rotular(c,x,y,ini,ab,rot,linhas,ocupados,r=(5+1.5*i)*mm,arco_visivel=(tipo!='reto' and (tipo=='arco' or rot is not None)))
    def num(self,n,x,y):
        c=self.c; c.setFont('And',8.5); c.setFillColor(GREY); c.drawString(x,y,str(n))

    # ---------- figuras: medir e desenhar dentro de um retângulo ----------
    # fig = {'angulo': {...}} | {'semirretas': {...}} | {'bico': {...}}; medidas em mm no YAML

    def _caixa_desenhada(self,tipo,d,largura,numero):
        """caixa da figura desenhada num Medidor: vértice em (0, 0) ou, nas largas, topo em 0 e início em x = 0"""
        c,oc=self.c,getattr(self,'_ocupados',None)
        self.c,self._ocupados=Medidor(),[]
        try:
            if tipo=='transversal': desenhar_transversal(self.c,0,0,largura,d,numero=numero,size=d.get('tamanho',9.5),ocupados=self._ocupados)
            else: self._desenhar_no_vertice(tipo,d,0,0)
            return self.c.caixa
        finally:
            self.c,self._ocupados=c,oc

    def medir_figura(self,fig,largura,numero=True):
        tipo,d=next(iter(fig.items()))
        if tipo=='bico': return largura,((6 if numero else 2)+d['altura']*escala_bico(d,largura)+2)*mm
        x0,y0,x1,y1=self._caixa_desenhada(tipo,d,largura,numero)
        if tipo=='transversal': return largura,max(0,y1)-y0+1*mm   # rótulos acima do topo também contam
        return x1-x0,y1-y0

    def _desenhar_no_vertice(self,tipo,d,vx,vy):
        if tipo=='angulo':
            a,b=d['direcoes']
            self.angulo(vx,vy,a,b,L=d.get('comprimento',18)*mm,nomes=d.get('nomes'),marca=d.get('marca','arco'),rot=d.get('rotulo'))
        elif tipo=='cruzadas':
            desenhar_cruzadas(self.c,vx,vy,d,size=d.get('tamanho',9.5),ocupados=getattr(self,'_ocupados',None))
        else:
            self.semirretas(vx,vy,d['direcoes'],d['nomes'],d['vertice'],L=d.get('comprimento',20)*mm,
                            marcas=d.get('marcas',()),tracejadas=d.get('tracejadas',()))

    def desenhar_figura(self,fig,x,y_topo,largura,numero=True):
        """desenha a figura com o topo em y_topo, centralizada em [x, x+largura].
        Devolve os ângulos calculados (bico) ou None."""
        tipo,d=next(iter(fig.items()))
        if tipo=='bico':
            k=escala_bico(d,largura)
            yr=y_topo-(6 if numero else 2)*mm; ys=yr-d['altura']*mm*k
            x0,x1=x+4*mm,x+largura-6*mm
            self.paralelas(yr,ys,x0,x1)
            segs=[(a,L*mm*k) for a,L in d['segmentos']]
            marks=[tuple(m) for m in d['marcas']]
            return self.desenhar_bico(x0,x1,yr,ys,segs,marks,size=d.get('tamanho',9.5))
        bx0,by0,bx1,by1=self._caixa_desenhada(tipo,d,largura,numero)
        if tipo=='transversal':
            desenhar_transversal(self.c,x,y_topo-max(0,by1),largura,d,numero=numero,size=d.get('tamanho',9.5),
                                 ocupados=getattr(self,'_ocupados',None),linhas_pagina=getattr(self,'_linhas_figuras',None)); return None
        self._desenhar_no_vertice(tipo,d,x+(largura-(bx1-bx0))/2-bx0,y_topo-by1)
        return None

    # ---------- texto com estilos ----------
    def _linhas(self,textos,largura,tamanho=None):
        out=[]
        for t in textos:
            estilo,s=('normal',t) if isinstance(t,str) else next(iter(t.items()))
            size,cor=ESTILOS[estilo]
            if tamanho and estilo=='normal': size=tamanho
            # linha que cabe vai como está (a quebra automática junta espaços usados para alinhar)
            ls=[s] if self.c.stringWidth(s,'And',size)<=largura else simpleSplit(s,'And',size,largura)
            for l in ls: out.append((size,cor,l))
        return out
    def _altura_linhas(self,linhas): return sum(s*1.45 for s,_,_ in linhas)
    def _desenhar_linhas(self,linhas,x,y_topo):
        y=y_topo
        for size,cor,l in linhas:
            y-=size*1.1; self.c.setFont('And',size); self.c.setFillColor(cor); self.c.drawString(x,y,l); y-=size*0.35
        return y

    # ---------- blocos ----------
    def exemplo_figura(self,titulo,textos,figura=None):
        """quadro de exemplo: figura à esquerda, texto à direita; altura medida pelo conteúdo"""
        c=self.c; topo=self.y-5*mm; x=M+3*mm; larg=W-2*M-6*mm
        fw,fh=(0,0)
        if figura:
            fw,fh=self.medir_figura(figura,62*mm,numero=False)
        tx=x+fw+6*mm if figura else x
        linhas=self._linhas(textos,M+3*mm+larg-tx)
        th=self._altura_linhas(linhas)
        h=max(fh,th)
        if figura: self.desenhar_figura(figura,x,topo-(h-fh)/2,fw,numero=False)
        self._desenhar_linhas(linhas,tx,topo-(h-th)/2)
        base=topo-h-3*mm
        c.setStrokeColor(K.LIGHT); c.setLineWidth(.8); c.roundRect(M,base,W-2*M,self.y+4*mm-base,2*mm)
        c.setFont('AndB',9.5); c.setFillColor(INK); c.drawString(M+3*mm,self.y-2*mm,titulo)
        self.y=base-4*mm

    LARGAS=('bico','transversal')   # ocupam a largura da célula (paralelas de ponta a ponta)

    def _celula(self,it,larg,tamanho):
        """medidas de um item da grade: figura, texto (ao lado ou abaixo) e, numa questão de prova,
        enunciado em cima, figura no meio e alternativas embaixo"""
        fig={k:v for k,v in it.items() if k in ('angulo','semirretas','bico','cruzadas','transversal')} or None
        if fig and len(fig)>1: raise ValueError('item com mais de uma figura')
        larga=bool(fig) and next(iter(fig)) in self.LARGAS
        txt=[it['texto']] if 'texto' in it else []
        questao='alternativas' in it
        em_cima=larga and bool(txt) and not questao   # figura larga com enunciado: texto em cima, na linha do número
        fw,fh=(self.medir_figura(fig,larg,numero=not em_cima) if larga else self.medir_figura(fig,larg-6*mm)) if fig else (0,0)
        cabe_ao_lado=bool(txt) and fig and self.c.stringWidth(txt[0],'And',tamanho)+fw+16*mm<=larg
        ao_lado=bool(fig and txt and (larg>=100*mm or cabe_ao_lado) and not larga and not questao)
        tl=larg-8*mm-(fw+6*mm if ao_lado else 0)
        linhas=self._linhas(txt,tl,tamanho)
        th=self._altura_linhas(linhas)
        if ao_lado: h=max(fh,th+4*mm)
        elif em_cima: h=th+1*mm+fh
        elif questao:
            nl=-(-len(it['alternativas'])//self._colunas_alternativas(it['alternativas'],larg))
            h=th+3*mm+(fh+2*mm if fig else 0)+3*mm+6*mm*nl
        else: h=fh+(th+2*mm if txt else 0)
        return dict(fig=fig,fw=fw,fh=fh,linhas=linhas,th=th,ao_lado=ao_lado,larga=larga,em_cima=em_cima,
                    alternativas=it.get('alternativas'),h=max(h,6*mm))

    def _colunas_alternativas(self,itens,larg,tamanho=11):
        textos=[f'({chr(65+k)}) {a}' for k,a in enumerate(itens)]
        maior=max(self.c.stringWidth(s,'And',tamanho) for s in textos)+3*mm
        for cols in (len(itens),2,1):
            if maior<=(larg-10*mm)/cols: return cols
        return 1

    def _alternativas_em(self,itens,x,y,larg,tamanho=11):
        """alternativas numa linha; se não couberem, em 2 colunas ou uma por linha. Devolve a altura usada."""
        cols=self._colunas_alternativas(itens,larg,tamanho); passo=(larg-10*mm)/cols; c=self.c
        c.setFont('And',tamanho); c.setFillColor(INK)
        for k,a in enumerate(itens):
            c.drawString(x+8*mm+(k%cols)*passo,y-(k//cols)*6*mm,f'({chr(65+k)}) {a}')

    def grade(self,itens,colunas=2,tamanho=12,altura=None):
        """itens numerados em colunas; as linhas dividem a altura disponível"""
        larg=(W-2*M)/colunas
        cel=[self._celula(it,larg,tamanho) for it in itens]
        linhas=[list(range(i,min(i+colunas,len(itens)))) for i in range(0,len(itens),colunas)]
        hs=[max(cel[i]['h'] for i in l) for l in linhas]
        altura=self.y-LIMITE-ESPACO if altura is None else altura
        extra=(altura-sum(hs))/len(linhas)
        if extra<0: raise ValueError(f'não cabe: a grade pede {sum(hs)/mm:.0f} mm, há {altura/mm:.0f} mm')
        if all(c['fig'] is None for c in cel): extra=min(extra,EXTRA_MAX_TEXTO)
        y=self.y
        for l,h in zip(linhas,hs):
            acima=min(extra/2,6*mm); y-=acima   # um pouco de ar acima de cada linha; o resto vai abaixo
            for j,i in enumerate(l):
                c=cel[i]; x=M+j*larg; fig,lin=c['fig'],c['linhas']
                self.num(i+1,x+1*mm,y-3*mm)
                def figura_em(topo):
                    if c['larga']: self.desenhar_figura(fig,x,topo,larg)
                    else: self.desenhar_figura(fig,x+6*mm,topo,c['fw'] if c['ao_lado'] else larg-6*mm)
                if c['alternativas'] is not None:      # questão: enunciado, figura, alternativas
                    yy=self._desenhar_linhas(lin,x+8*mm,y-3*mm+lin[0][0]*1.1) if lin else y-3*mm
                    if fig: figura_em(yy-1*mm); yy-=c['fh']+2*mm
                    self._alternativas_em(c['alternativas'],x,yy-5*mm,larg)
                    continue
                if c['em_cima']:
                    yy=self._desenhar_linhas(lin,x+8*mm,y-3*mm+lin[0][0]*1.1)
                    self.desenhar_figura(fig,x,yy-1*mm,larg,numero=False)
                    continue
                if fig: figura_em(y if c['larga'] else y-1*mm)
                if lin:
                    if c['ao_lado']: self._desenhar_linhas(lin,x+8*mm+c['fw']+6*mm,y-1*mm)
                    elif fig: self._desenhar_linhas(lin,x+8*mm,y-c['fh']-1*mm)
                    else: self._desenhar_linhas(lin,x+8*mm,y-3*mm+lin[0][0]*1.1)   # 1ª linha de base = a do número
            y-=h+extra-acima
        self.y=y-ESPACO

    def figura(self,fig):
        w,h=self.medir_figura(fig,W-2*M,numero=False)
        v=self.desenhar_figura(fig,M,self.y,W-2*M,numero=False)
        self.y-=h+4*mm
        return v

    def alternativas(self,itens,tamanho=12):
        c=self.c; passo=(W-2*M)/len(itens)
        c.setFont('And',tamanho); c.setFillColor(INK)
        for k,a in enumerate(itens): c.drawString(M+2*mm+k*passo,self.y-4*mm,f'({chr(65+k)}) {a}')
        self.y-=12*mm
