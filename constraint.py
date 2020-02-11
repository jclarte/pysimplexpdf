

import re
from itertools import chain, count
from math import inf

import sympy

class Constraint:

    l_part = None
    r_part = None
    comp = None
    variables = list()
    substitutions = {}

    def __init__(self, l_part, comp, r_part):
        self.l_part = sympy.sympify(l_part)
        self.r_part = sympy.sympify(r_part)
        self.comp = comp
        self.variables = sorted(set(filter(lambda x:isinstance(x, sympy.Symbol), chain(self.l_part.atoms(), self.r_part.atoms()))), key=lambda v:v.name)
        self.substitutions = {}

    def __str__(self):
        return str(self.l_part) + {
            'LEQ' : r"""\leq""",
            'EQ' : r"""=""",
            'GEQ' : r"""\geq""",
            }[self.comp] + str(self.r_part)

    def canonize(self):
        scalar = self.get_scalar()

        lin_part = self.r_part - scalar[1]
        self.l_part -= lin_part
        self.r_part -= lin_part
        self.l_part -= scalar[0]
        self.r_part -= scalar[0]


        if self.comp == "GEQ":
            self.l_part *= -1
            self.r_part *= -1
            self.comp = "LEQ"

    def set_variables(self, variables):
        self.variables = variables

    def add_deviation(self, deviation_variable):

        self.l_part += deviation_variable
        if deviation_variable not in self.variables:
            self.variables.append(deviation_variable)
        self.deviation_variable = deviation_variable
        self.comp = "EQ"

    def in_base(self, base_variable=None):
        if base_variable is None:
            base_variable = self.deviation_variable
        l_coeff, r_coeff = self.get_coeff(base_variable)
        coeff = l_coeff - r_coeff

        self.l_part, self.r_part = base_variable, (self.r_part - self.l_part + coeff*base_variable) / (coeff)
        # print(str(self.l_part) + "=" + str(self.r_part))

    def var_constraint(self, out_variable):
        return Constraint(self.r_part.subs([(var, 0) for var in filter(lambda v:v!=out_variable, self.variables)]), "GEQ", 0)

    def subs(self, variable, expression):
        self.substitutions[variable] = expression

    def apply_subs(self):
        self.l_part = self.l_part.subs([(k,v) for k, v in self.substitutions.items()])
        self.r_part = self.r_part.subs([(k,v) for k, v in self.substitutions.items()])
        self.substitutions = {}

    def latex(self):
        COMP = {
            'LEQ' : r"""\leq""",
            'EQ' : r"""=""",
            'GEQ' : r"""\geq""",
            }
        return sympy.latex(self.l_part) + COMP[self.comp] + sympy.latex(self.r_part)

    def std_latex_array(self, out_var=None):
        l_scalar, r_scalar = self.get_scalar()

        l_part = []
        r_part = [sympy.latex(r_scalar)]

        for variable in self.variables:

            l_coeff, r_coeff = self.get_coeff(variable)
            substitution = self.substitutions.get(variable, variable)

            if l_coeff != 0:
                l_part.append(sympy.latex(sympy.Mul(l_coeff, substitution, evaluate=False)))

            if r_coeff < 0:
                r_part.append("-")
                r_part.append(sympy.latex(sympy.Mul(-r_coeff, substitution, evaluate=False)))
            elif r_coeff > 0:
                r_part.append("+")
                r_part.append(sympy.latex(sympy.Mul(r_coeff, substitution, evaluate=False)))
            elif out_var:
                if variable in out_var:
                    r_part += ["", ""]
                else:
                    pass
            else:
                r_part += ["", ""]

        l_part = " & ".join(l_part)
        r_part = " & ".join(r_part)

        comp = {
            'LEQ' : r"""\leq""",
            'EQ' : r"""=""",
            'GEQ' : r"""\geq""",
            }[self.comp]

        return l_part + " & " + comp + " & " + r_part + r"""\\"""

    def latex_array(self):
        l_scalar, r_scalar = self.get_scalar()

        l_part = [sympy.latex(l_scalar)] if l_scalar != 0 else []
        r_part = [sympy.latex(r_scalar)]

        for variable in self.variables:

            l_coeff, r_coeff = self.get_coeff(variable)
            substitution = self.substitutions.get(variable, variable)

            if l_coeff != 0:
                l_part.append(sympy.latex(sympy.Mul(l_coeff, substitution, evaluate=False)))
            else:
                l_part.append("")

            if r_coeff != 0:
                r_part.append(sympy.latex(sympy.Mul(r_coeff, substitution, evaluate=False)))

        l_part = " & + & ".join(l_part)
        r_part = " & + & ".join(r_part)

        comp = {
            'LEQ' : r"""\leq""",
            'EQ' : r"""=""",
            'GEQ' : r"""\geq""",
            }[self.comp]

        return l_part + " & " + comp + " & " + r_part + r"""\\"""




    def get_coeff(self, variable):
        return self._get_coeff(self.l_part, variable), self._get_coeff(self.r_part, variable)

    @classmethod
    def _get_coeff(cls, expression, variable):

        assert cls._is_linear_part(expression)

        coeff = None
        if expression == variable:
            return 1
        elif isinstance(expression, sympy.mul.Mul):
            if variable in expression.args:
                return expression.subs(variable, 1)
        elif isinstance(expression, sympy.add.Add):
            coeff = 0
            for arg in expression.args:
                coeff += cls._get_coeff(arg, variable)
            return coeff

        return 0

    @staticmethod
    def _has_symbols(expression):
        return any([e.is_symbol for e in expression.atoms()])

    @staticmethod
    def _nb_symbols(expression):
        return len(list(filter(lambda x:isinstance(x, sympy.Symbol), expression.atoms())))

    @classmethod
    def _is_linear_part(cls, part):

        if part.is_number or part.is_symbol:
            return True
        elif isinstance(part, sympy.mul.Mul):
            # works if only 1 arg got symbols (avoid quadratic)
            if sum([cls._has_symbols(arg) for arg in part.args]) > 1:
                return False

            return all([cls._is_linear_part(arg) for arg in part.args])

        elif isinstance(part, sympy.add.Add):
            return all([cls._is_linear_part(arg) for arg in part.args])

        return False

    def _get_scalar(self, expression):
        return expression.subs([(k, 0) for k in self.variables])

    def get_scalar(self):
        return self._get_scalar(self.l_part), self._get_scalar(self.r_part)
