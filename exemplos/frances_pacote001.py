import os, sys
RAIZ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,RAIZ)
SAIDA=os.path.join(RAIZ,'exemplos','pdf')
os.makedirs(SAIDA,exist_ok=True)
from motor.folha import Folha as Feuille
f=Feuille(os.path.join(SAIDA,'Pacote_001_6A_1-5.pdf'),'Pacote 1 — 6A 1 a 5')
m1=[('bonjour','olá, bom dia'),('merci','obrigado'),('un avion','um avião'),('une ville','uma cidade'),('la France','a França'),('un étudiant','um estudante')]
m2=[('content','contente'),('fatigué','cansado'),('brésilien','brasileiro'),('dans','dentro de, em'),('mais','mas'),('arriver','chegar')]

f.page('6A 1a','Mots familiers 1','Écoute et répète.','Ouça e repita cada palavra em voz alta.','ecoute'); f.mots(m1); f.fim('6A 1a')
f.page('6A 1b','Mots familiers 1','Relie.','Ligue cada palavra ao seu sentido.','relie','10 chacun'); f.relie(m1,seed=3); f.fim('6A 1b')
f.page('6A 2a','Mots familiers 2','Écoute et répète.','Ouça e repita cada palavra em voz alta.','ecoute'); f.mots(m2); f.fim('6A 2a')
f.page('6A 2b','Mots familiers 2','Relie.','Ligue cada palavra ao seu sentido.','relie','10 chacun'); f.relie(m2,seed=7); f.fim('6A 2b')
f.page('6A 3a','Mots familiers 3','Écoute et entoure.','Ouça e circule a palavra que você ouvir.','entoure','10 chacun')
f.entoure([['merci','mais','une ville'],['arriver','un avion','dans'],['content','un étudiant','la France'],['bonjour','brésilien','fatigué'],['une ville','mais','merci'],['dans','la France','content']]); f.fim('6A 3a')
f.page('6A 3b','Mots familiers 3','Recopie.','Passe o lápis sobre a palavra e depois copie na linha.','ecris','5 chacun')
f.recopie(['bonjour','merci','un avion','une ville','fatigué','brésilien']); f.fim('6A 3b')
f.page('6A 4a','Expressions 1','Écoute et répète.','Ouça e repita cada frase em voz alta.','ecoute')
f.phrases(['Je m\'appelle Rafael.','Je suis brésilien.','Je suis étudiant.','Je suis fatigué.','Bienvenue à Toulouse !','Merci !'],size=16,
 gloss=['Eu me chamo Rafael.','Sou brasileiro.','Sou estudante.','Estou cansado.','Bem-vindo a Toulouse!','Obrigado!']); f.fim('6A 4a')
f.page('6A 4b','Expressions 1','Complète avec les mots de la boîte.','Complete com as palavras do quadro.','ecris','10 chacun')
f.banque(['suis','m\'appelle','Bienvenue','avion','ville'])
f.trous(['Je ___ Rafael.','Je ___ étudiant.','Je suis dans un ___ .','Toulouse est une ___ .','« ___ à Toulouse ! »']); f.fim('6A 4b')
f.page('6A 5a','Petite histoire 1','Écoute, puis lis à voix haute.','Ouça e depois leia em voz alta três vezes. Marque um quadrinho a cada leitura.','lis')
f.lecture(['Bonjour ! Je m\'appelle Rafael.','Je suis brésilien et je suis étudiant.','Je suis dans un avion.','L\'avion arrive à Toulouse.',
 'Toulouse est une ville en France.','Je suis content, mais je suis fatigué.','L\'hôtesse : « Bienvenue à Toulouse ! »','Rafael : « Merci ! »'],size=13.5); f.fim('6A 5a')
f.page('6A 5b','Petite histoire 1','Vrai ou faux ? Entoure V ou F.','Verdadeiro ou falso? Circule V ou F.','entoure','10 chacun')
f.vraifaux(['Rafael est français.','L\'avion arrive à Toulouse.','Toulouse est en France.','Rafael est fatigué.'])
f.dictee(2,titre='Écoute et écris.   [30 chacun]',gloss='Ouça cada frase e escreva o que ouviu.'); f.fim('6A 5b')
f.save()
