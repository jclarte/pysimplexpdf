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

`python pysimplexpdf.py --infile pl.json --outfile pl_example.pdf` -> génère un pdf `pl_example.pdf`.

## Templates

Le fichier `config.json` contient lestemplates de texte à remplir dans les correction.

[TODO] DOC

## TODO

1. gérer les cas sans solution de base (pb auxilliare)
2. faire une version pour le simplexe tableau.
