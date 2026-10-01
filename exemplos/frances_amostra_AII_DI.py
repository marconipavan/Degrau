import os, sys
RAIZ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,RAIZ)
SAIDA=os.path.join(RAIZ,'exemplos','pdf')
os.makedirs(SAIDA,exist_ok=True)
from motor.folha import Folha as Feuille
from reportlab.lib.units import mm
f=Feuille(os.path.join(SAIDA,'Amostra_niveis_AII_e_DI.pdf'),'Amostra — AII 64 e DI 112')

f.page('AII 64a','Écrire de mémoire 7','Lis le texte deux fois, puis cache-le.',None,'lis')
f.texte(["Le premier jour, Rafael est arrivé à l'école à huit heures. Il a cherché la salle B12 pendant vingt minutes. Enfin, une étudiante l'a aidé. Elle s'appelle Camille et elle vient de Lyon.",
 "Ensemble, ils sont entrés dans la salle. Le professeur a regardé sa montre et il a souri : « Vous êtes en retard, mais bienvenue ! »"],size=13,box=True)
f.sousinstr('ordre' if False else 'ecris','Numérote les phrases dans l\'ordre de l\'histoire.','10 chacun')
f.ordre(['Camille a aidé Rafael.','Le professeur a souri.','Rafael a cherché la salle B12.','Ils sont entrés dans la salle.'],size=12)
f.fim('AII 64a')

f.page('AII 64b','Écrire de mémoire 7','Sans regarder le texte, réponds.',None,'ecris','15 chacun')
f.questions([("À quelle heure Rafael est-il arrivé à l'école ?",1),("Pendant combien de temps a-t-il cherché la salle ?",1),
 ("Qui l'a aidé ? D'où vient-elle ?",2),("Qu'est-ce que le professeur a fait ?",2)],size=12)
f.fim('AII 64b')

f.page('DI 112a','Analyse de phrases complexes 12','Lis l\'exemple, puis décompose chaque phrase.',None,'ecris','10 chacun')
f.exemple('Exemple',"L'avion que Rafael a pris hier, qui venait de Paris, est arrivé en retard à cause du brouillard.",
 ["(a) Rafael a pris un avion hier.","(b) L'avion venait de Paris.","(c) L'avion est arrivé en retard.","(d) Il y avait du brouillard."])
f.decompose(1,"Camille, dont le frère travaille chez Airbus, pense que Rafael devrait postuler à un stage.",["(a) Le frère de Camille","(b) Camille pense que"])
f.decompose(2,"Bien qu'il soit fatigué, Rafael relit le rapport que son professeur lui a demandé.",["(a) Rafael est","(b) Son professeur lui a demandé","(c) Rafael"])
f.fim('DI 112a')

f.page('DI 112b','Analyse de phrases complexes 12','Lis le paragraphe, puis réponds aux questions.',None,'lis')
f.texte(["Toulouse est souvent appelée la capitale européenne de l'aéronautique. C'est ici qu'Airbus assemble une grande partie de ses avions, et plusieurs écoles d'ingénieurs y forment chaque année des milliers d'étudiants. Pourtant, la ville ne vit pas seulement de l'industrie : le centre historique, construit en briques roses, attire de nombreux touristes, ce qui lui a donné le surnom de « Ville rose ». Pour Rafael, qui est arrivé il y a six mois, c'est ce mélange qui rend Toulouse unique. Il pense que, s'il obtient son diplôme ici, il pourra travailler dans une entreprise dont les avions volent partout dans le monde."],size=10.5,box=True)
f.questions([("Donne deux raisons pour lesquelles Toulouse est la « capitale de l'aéronautique ». [20]",2),
 ("D'où vient le surnom « Ville rose » ? [20]",1),
 ("Réécris la dernière phrase en deux phrases simples. [30]",2)],size=10.5)
f.fim('DI 112b')
f.save()
