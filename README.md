# PySimplexPDF

Générateur de correction de problèmes d'optimisation linéaire avec l'algorithme du simplexe. Génère une solution détaillée en pdf.

## Prérequis

Avoir un générateur Latex/PDF. Sous Linux, `texlive` fait l'affaire : `sudo apt install texlive-full`.

Fonctionne avec Python 3.7 (développé sous environnement Anaconda)


### Librairies python

- `sympy`

- `pylatex`


## Utilisation

Les programmes linéaires à résoudre doivent être au format json : une liste de problèmes sous la forme :

```json
{
  "title" : "titre",
  "description" : "description du problème",
  "variables" : ["liste des variables de décision"],
  "utility" : "la fonction à optimiser",
  "optimizer" :"max ou min",
  "constraints" : ["liste des contraintes"]
}
```

Un exemple de fichier est contenu dans `pl.json`.

`python simplex.py pl.json` -> génère un pdf `simplex_example.pdf`.

## TODO

Gérer des entrées / sorties différentes :

1. configurer le nom de sortie
2. customiser le texte depuis un json
3. mettre du argparse dans l'entrée
4. gérer les cas sans solution de base (pbb auxilliare)
5. faire une version pour le simplexe tableau.
