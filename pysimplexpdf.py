
import re
import argparse
import time

from simplex import load_from_json, multi_solve

parser = argparse.ArgumentParser(description="Générateur de solutions de programmes linéaires avec l'algorithme du simplexe, au format pdf.")
parser.add_argument("--infile", "-i", help="fichier json contenant les programmes linéaires à résoudre.")
parser.add_argument("--outfile", "-o", help="nom du fichier pdf de sortie", default=None)

args = parser.parse_args()

data = load_from_json(args.infile)

assert not args.outfile or args.outfile[-4:] == ".pdf"
assert args.infile[-5:] == ".json"

prefix = args.outfile[:-4] if args.outfile else args.infile[:-5]

start_time = time.time()
multi_solve(data, name=prefix)
delta_time = time.time() - start_time

print(f"PDF generated in {delta_time:.2f}s")
