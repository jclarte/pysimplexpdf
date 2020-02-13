

import re
from itertools import chain, count
from math import inf

import sympy

from constraint import Constraint

class LinProg:
    """
    classe permettant de contenir un programme d'optimisation linéaire et de le résoudre
    le format des donnée est le suivant :
    UTILITY = une liste de coefficients de la fonctions utilité
    """

    title = ""
    description = ""

    utility = None
    variables = []
    optimizer = None
    constraints = []
    comments = ""
    standard = False
    current_solution = {}
    base = None
    out = None

    def from_dict(self, dictionnary):
        self.title = dictionnary.get("title", "")
        self.description = dictionnary.get("description", "")
        self.utility = dictionnary["utility"]
        self.utility_constraint = Constraint("z", "EQ", self.utility)
        self.variables = dictionnary["variables"]
        self.optimizer = dictionnary["optimizer"]
        self.constraints = [Constraint(*constraint) for constraint in dictionnary["constraints"]]
        for constraint in self.constraints:
            constraint.set_variables(self.variables)
        self.comments = "Forme initiale du problème."
        self.standard = False

    def to_latex(self, comments=False):

        COMP = {
            'LEQ' : r"""\leq""",
            'EQ' : r"""=""",
            'GEQ' : r"""\geq""",
            }

        prefix = r"""
        \[
        \left\{
                \begin{array}{"""

        prefix += "cc"*(len(self.variables)+2) + "}"

        suffix1 = r"""
                \end{array}
        \right.
        \]
        \["""

        suffix2 = r"""\]"""

        lines = [prefix]

        if self.standard:
            for constraint in self.constraints:
                lines.append(constraint.std_latex_array(out_var=self.out))

            # import pdb; pdb.set_trace()
            utility_line = "z & = & "
            utility = self.utility_constraint
            if utility.get_scalar()[1] == 0:
                skip = True
            else:
                skip = False
                utility_line += sympy.latex(utility.get_scalar()[1])
            for variable in self.variables:
                var_coeff = utility.get_coeff(variable)[1]
                substitution = utility.substitutions.get(variable, variable)
                if var_coeff > 0:
                    if skip:
                        utility_line += " &  & " + sympy.latex(sympy.Mul(var_coeff, substitution, evaluate=False))
                        skip = False
                    else:
                        utility_line += " & + & " + sympy.latex(sympy.Mul(var_coeff, substitution, evaluate=False))
                elif var_coeff < 0:
                    utility_line += " & - & " + sympy.latex(sympy.Mul(-var_coeff, substitution, evaluate=False))
                    skip = False


            lines.append(utility_line)
            lines.append(suffix1)

        else:
            for constraint in self.constraints:
                lines.append(constraint.latex_array())
            lines.append(suffix1)
            lines.append(self.optimizer + " z="+sympy.latex(self.utility))
        lines.append(suffix2)
        if self.current_solution:
            lines.append(self.view_solution())
        if comments:
            return "\n".join([self.comments] + lines)
        else:
            return "\n".join(lines)

    def canonical_form(self,
                       to_max="Minimiser une fonction, c'est maximiser son inverse : on multiplie $z$ par -1.\n",
                       comment="On transforme les $\\geq$ en $\\leq$ en multipliant chaque membre par -1.\n"
                       ):
        """
        transform into canonical form
        """

        if self.optimizer == "min":
            self.utility *= -1
            self.utility_constraint = Constraint("z", "EQ", self.utility)
            self.optimizer = "max"
            self.comments = to_max
        else:
            self.comments = ""

        for constraint in self.constraints:
            # pass all sclars to r_part and all varibales to l_part
            constraint.canonize()

        self.comments += comment


    def get_new_var(self):
        for idx in count(1):
            if sympy.Symbol(f"x_{idx}") in self.variables:
                continue
            else:
                return sympy.Symbol(f"x_{idx}")

    def pre_standard_form(self, comment="On introduit les variables d'écart."):

        for constraint in filter(lambda c:c.comp == "LEQ", self.constraints):
            new_var = self.get_new_var()


            self.variables.append(new_var)

            constraint.add_deviation(new_var)

        for constraint in self.constraints:
            constraint.set_variables(self.variables)

        self.utility_constraint.set_variables(self.variables)

        self.comments = comment

    def standard_form(self, comment="On passe les variables d'écart sur la partie gauche : ce sont les variables de base.\nLes autres membres sont sur la partie droite : ce sont les scalaires et les variables hors base."):

        for constraint in self.constraints:
            constraint.in_base()

        self.standard = True
        self.comments = comment

    def set_base(self, comment="On initialise la solution de base."):

        base_var = [constraint.deviation_variable for constraint in self.constraints]
        out_var = [var for var in filter(lambda v:v not in base_var, self.variables)]
        solution = {var:0 for var in out_var}

        # check if out_var set to 0 is a solution
        for constraint in self.constraints:
            if constraint.get_scalar()[1] < 0:
                raise NotImplementedError("can't solve problems not satisfying 0 sol")
            solution[constraint.l_part] = constraint.get_scalar()[1]

        self.base = base_var
        self.out = out_var
        self.current_solution = solution

        self.comments = comment

    def update_solution(self):
        self.current_solution = {var:0 for var in self.out}

        # check if out_var set to 0 is a solution
        for constraint in self.constraints:
            self.current_solution[constraint.l_part] = constraint.get_scalar()[1]

    def view_solution(self):
        return " ; ".join([f"${var} = {self.current_solution[var]}$" for var in self.variables]) + "\n"

    def get_incoming_variable(self):
        """
        check utility function to find best candidate
        """
        best_value = 0
        best_var = None
        for var in self.out:
            value = Constraint._get_coeff(self.utility, var)
            if value > best_value:
                best_var = var
                best_value = value

        return best_var

    def get_pivot_line(self, variable):
        var_constraints = list()
        std_var_constraints = list()
        best_value = inf
        best_index = -1
        for idx, constraint in enumerate(self.constraints):
            var_constraint = constraint.var_constraint(variable)
            var_constraints.append(constraint.var_constraint(variable))
            var_constraint.canonize()

            coeff = var_constraint.get_coeff(variable)[0]

            if coeff > 0:
                var_constraint.l_part /= coeff
                var_constraint.r_part /= coeff

                if var_constraint.r_part < best_value:
                    best_value = var_constraint.r_part
                    best_index = idx
            else:
                var_constraint = Constraint(variable, "GEQ", 0)
            std_var_constraints.append(var_constraint)



        return var_constraints, std_var_constraints, best_index

    def set_in_base(self, variable, idx, comment="\nOn fait entrer la variable ${variable}$ dans la base."):
        out_var = self.constraints[idx].l_part
        self.constraints[idx].in_base(variable)
        for idx_constraint, constraint in enumerate(self.constraints):
            if idx_constraint == idx:
                continue
            constraint.substitutions[variable] = self.constraints[idx].r_part
        self.utility_constraint = Constraint("z", "EQ", self.utility)
        self.utility_constraint.set_variables(self.variables)
        self.utility_constraint.substitutions[variable] = self.constraints[idx].r_part
        self.utility = self.utility_constraint.r_part
        self.comments = comment.format(variable=variable, idx=idx)
        self.out.remove(variable)
        self.out.append(out_var)
        self.base.append(variable)
        self.base.remove(out_var)
        self.update_solution()


    def apply_subs(self, comment="\nOn développe et on réduit."):
        for constraint in self.constraints:
            constraint.apply_subs()
        self.utility_constraint.apply_subs()

        self.utility = self.utility_constraint.r_part
        self.update_solution()
        self.comments = comment
