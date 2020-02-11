# PySimplexPDF

Générateur de correction de problèmes d'optimisation linéaire avec l'algorithme du simplexe. Génère une solution détaillée en pdf.

## Prérequis

Avoir un générateur Latex/PDF. Sous Linux, `texlive` fait l'affaire : `sudo apt install texlive-full`.

Fonctionne avec Python 3.7 (développé sous environnement Anaconda)


### Librairies python

- `sympy`

- `pylatex`


## Utilisation

[DEV] `python simplex.py` -> génère un pdf `simplex_example.pdf`. Actuellement il faut modifier le programem linéaire directement dans `simplex.py`

## TODO

Gérer des entrées / sorties différentes :

1. lire pb depuis un fichier
2. configurer le nom de sortie
3. résoudre un batch de programmes linéaires
