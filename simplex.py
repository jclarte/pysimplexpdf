"""
petit script d'implémentation de la méthode du simplexe avec visualisation

"""

import re
from itertools import chain, count
from math import inf

import sympy

from pylatex import Document, Section, Subsection
from pylatex.utils import NoEscape
from pylatex.basic import NewLine

from constraint import Constraint
from linear_program import LinProg

# VARIABLE_PATTERN = re.compile(r"""[a-zA-Z]+_?[0-9]*""")
# # COEFF_PATTERN = re.compile()

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






def lin_prog_solve(lin_prog):

    doc = Document(geometry_options={"margin" : "1.5cm"})
    parsed_pl = parse_linear_program(lin_prog)

    with doc.create(Section("Résolution de programme linéaire")):

        with doc.create(Subsection("Problème initial")):
            pl = LinProg()
            pl.from_dict(parsed_pl)
            latex = pl.to_latex()
            doc.append(NoEscape(latex))

        with doc.create(Subsection("Forme canonique")):
            pl.canonical_form()
            latex = pl.to_latex()
            doc.append(NoEscape(latex))

        with doc.create(Subsection("Forme standard")):
            pl.pre_standard_form()
            latex = pl.to_latex()
            doc.append(NoEscape(latex))


            pl.standard_form()
            latex = pl.to_latex()
            doc.append(NoEscape(latex))

        with doc.create(Subsection("Solution de base")):

            pl.set_base()
            doc.append(NoEscape("\nLa solution de base est la suivante : \n\n" + pl.view_solution()))

        in_var = pl.get_incoming_variable()
        nb_iter = 0

        while in_var is not None:
            nb_iter += 1

            with doc.create(Subsection(f"{nb_iter}e itération du simplexe")):

                doc.append(NoEscape("\nLa variable qui entre dans la base est : $" + sympy.latex(in_var) + "$"))
                doc.append(NoEscape("\nLes contraintes sur la variable sont :"))

                constraints, std_constraints, pivot_idx = pl.get_pivot_line(in_var)

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
                doc.append(NoEscape("\nQui correspond à la ligne $" + pl.constraints[pivot_idx].latex() + "$"))

                pl.set_in_base(in_var, pivot_idx)
                latex = pl.to_latex()
                doc.append(NoEscape(latex))

                pl.apply_subs()
                latex = pl.to_latex()
                doc.append(NoEscape(latex))

                in_var = pl.get_incoming_variable()

        doc.append(NoEscape("\nLe problème est résolu."))
    doc.generate_pdf('simplex_example', clean_tex=False)


if __name__ == '__main__':

    # PL = """
    # var: x_1, x_2
    # max z = 1000*x_1 + 1200*x_2
    # sc
    # 10*x_1 + 5*x_2 <= 200
    # 2*x_1 + 3*x_2 <=60
    # x_1 <= 34
    # x_2 <= 14
    # """

    PL = """
    var: x_1, x_2
    max z = x_1 + 2*x_2
    sc
    x_1 <= 10
    x_2 <= 10
    x_1 + x_2 <= 15
    """

    lin_prog_solve(PL)
