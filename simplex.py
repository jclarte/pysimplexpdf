"""
petit script d'implémentation de la méthode du simplexe avec visualisation

"""

import re
from itertools import chain, count
from math import inf
import json

import sympy

from pylatex import Document, Section, Subsection
from pylatex.utils import NoEscape
from pylatex.basic import NewLine

from constraint import Constraint
from linear_program import LinProg

# VARIABLE_PATTERN = re.compile(r"""[a-zA-Z]+_?[0-9]*""")
# # COEFF_PATTERN = re.compile()

def load_from_json(filename):
    """
    load lienar programs from json fils. Simple is json.pl
    """
    all_pl = []
    with open(filename, 'r') as f:
        pl_data = json.load(f)

    for pl in pl_data:
        variables = [sympy.Symbol(v) for v in pl["variables"]]
        utility = sympy.sympify(pl["utility"])

        constraints = []
        for c in pl["constraints"]:
            if "<=" in c:
                l_part, r_part = c.split("<=")
                comp = "LEQ"
            elif ">=" in c:
                l_part, r_part = c.split(">=")
                comp = "GEQ"
            else:
                l_part, r_part = c.split("=")
                comp = "EQ"
            l_part = sympy.sympify(l_part.strip())
            r_part = sympy.sympify(r_part.strip())
            constraint_variables = set(filter(lambda x:isinstance(x, sympy.Symbol), chain(l_part.atoms(), r_part.atoms())))
            if constraint_variables.issubset(set(variables)):
                constraints.append((l_part, comp, r_part))
            else:
                raise SyntaxError(f"undeclared variable found while parsing constraint on line {line}")

        optimizer = pl["optimizer"]
        title = pl["title"],
        description = pl["description"]

        from pprint import pprint
        pprint({
            "variables" : variables,
            "utility" : utility,
            "optimizer" : optimizer,
            "constraints" : constraints,
            })

        new_prog = LinProg()
        new_prog.from_dict({
            "variables" : variables,
            "utility" : utility,
            "optimizer" : optimizer,
            "constraints" : constraints,
            })
        all_pl.append(new_prog)

    return all_pl


def parse_linear_program(multiline_string):

    print(multiline_string)

    variables = []
    utility = None
    optimizer = None
    constraints = []
    state = 'init'
    for idx, line in enumerate(multiline_string.split('\n')):

        if line.strip() == '':
            continue
        elif state == 'init':

            if "var:" in line:
                for variable in line.split("var:")[1].split(","):
                    variables.append(sympy.Symbol(variable.strip()))
            elif "max" in line:
                utility = sympy.sympify(line.split("=")[1])
                optimizer = "max"
            elif "min" in line:
                utility = sympy.sympify(line.split("=")[1])
                optimizer = "min"
            elif "sc" in line:
                state = 'constraints'
        else:
            if "<=" in line:
                l_part, r_part = line.split("<=")
                comp = "LEQ"
            elif ">=" in line:
                l_part, r_part = line.split(">=")
                comp = "GEQ"
            else:
                l_part, r_part = line.split("=")
                comp = "EQ"
            l_part = sympy.sympify(l_part.strip())
            r_part = sympy.sympify(r_part.strip())
            constraint_variables = set(filter(lambda x:isinstance(x, sympy.Symbol), chain(l_part.atoms(), r_part.atoms())))


            if constraint_variables.issubset(set(variables)):
                constraints.append((l_part, comp, r_part))
            else:
                raise SyntaxError(f"undeclared variable found while parsing constraint on line {line}")

    return {
        "variables" : variables,
        "utility" : utility,
        "optimizer" : optimizer,
        "constraints" : constraints,
        }




def multi_solve(pl_list, doc=None):
    if doc is None:
        doc = Document(geometry_options={"margin" : "1.5cm"})

    for pl in pl_list:
        lin_prog_solve(pl, doc=doc)

    doc.generate_pdf('simplex_example', clean_tex=False)



def lin_prog_solve(lin_prog, doc=None, generate_pdf=False):

    if doc is None:
        doc = Document(geometry_options={"margin" : "1.5cm"})

    with doc.create(Section("Résolution de programme linéaire")):

        with doc.create(Subsection("Problème initial")):

            latex = lin_prog.to_latex()
            doc.append(NoEscape(latex))

        with doc.create(Subsection("Forme canonique")):
            lin_prog.canonical_form()
            latex = lin_prog.to_latex()
            doc.append(NoEscape(latex))

        with doc.create(Subsection("Forme standard")):
            lin_prog.pre_standard_form()
            latex = lin_prog.to_latex()
            doc.append(NoEscape(latex))


            lin_prog.standard_form()
            latex = lin_prog.to_latex()
            doc.append(NoEscape(latex))

        with doc.create(Subsection("Solution de base")):

            lin_prog.set_base()
            doc.append(NoEscape("\nLa solution de base est la suivante : \n\n" + lin_prog.view_solution()))

        in_var = lin_prog.get_incoming_variable()
        nb_iter = 0

        while in_var is not None:
            nb_iter += 1

            with doc.create(Subsection(f"{nb_iter}e itération du simplexe")):

                doc.append(NoEscape("\nLa variable qui entre dans la base est : $" + sympy.latex(in_var) + "$"))
                doc.append(NoEscape("\nLes contraintes sur la variable sont :"))

                constraints, std_constraints, pivot_idx = lin_prog.get_pivot_line(in_var)

                prefix = r"""
                \[
                \begin{array}{lll}"""

                suffix = r"""
                \end{array}
                \]"""

                doc.append(NoEscape(prefix))
                for constraint, std_constraint in zip(constraints, std_constraints):
                    doc.append(NoEscape(constraint.latex() + r""" & \rightarrow & """ + std_constraint.latex() + r"""\\"""))
                doc.append(NoEscape(suffix))

                doc.append(NoEscape("\nLa contrainte la plus forte est $" + std_constraints[pivot_idx].latex() + "$"))
                doc.append(NoEscape("\nQui correspond à la ligne $" + lin_prog.constraints[pivot_idx].latex() + "$"))

                lin_prog.set_in_base(in_var, pivot_idx)
                latex = lin_prog.to_latex()
                doc.append(NoEscape(latex))

                lin_prog.apply_subs()
                latex = lin_prog.to_latex()
                doc.append(NoEscape(latex))

                in_var = lin_prog.get_incoming_variable()

        doc.append(NoEscape("\nLe problème est résolu."))
    if generate_pdf:
        doc.generate_pdf('simplex_example', clean_tex=False)
    else:
        return doc

if __name__ == '__main__':

    import sys

    data = load_from_json(sys.argv[1])

    multi_solve(data)
