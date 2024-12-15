import numbers
from functools import singledispatch


class Expression():

    def __init__(self, *operands):
        self.operands = operands

    def __add__(self, other):
        return Add(self, self._ensure_expression(other))

    def __sub__(self, other):
        return Sub(self, self._ensure_expression(other))

    def __mul__(self, other):
        return Mul(self, self._ensure_expression(other))

    def __truediv__(self, other):
        return Div(self, self._ensure_expression(other))

    def __pow__(self, other):
        return Pow(self, self._ensure_expression(other))

    def __radd__(self, other):
        return Add(self._ensure_expression(other), self)

    def __rsub__(self, other):
        return Sub(self._ensure_expression(other), self)

    def __rmul__(self, other):
        return Mul(self._ensure_expression(other), self)

    def __rtruediv__(self, other):
        return Div(self._ensure_expression(other), self)

    def __rpow__(self, other):
        return Pow(self._ensure_expression(other), self)

    @staticmethod
    def _ensure_expression(value):
        if isinstance(value, Expression):
            return value
        return Number(value)


class Operator(Expression):
    precedence = None
    symbol = None

    def __str__(self):
        def format_operand(operand):
            if isinstance(operand, Operator) and \
                    operand.precedence < self.precedence:
                return f"({operand})"
            return str(operand)
        return f" {self.symbol} ".join(map(format_operand, self.operands))


class Add(Operator):
    precedence = 1
    symbol = "+"


class Sub(Operator):
    precedence = 1
    symbol = "-"


class Mul(Operator):
    precedence = 2
    symbol = "*"


class Div(Operator):
    precedence = 2
    symbol = "/"


class Pow(Operator):
    precedence = 3
    symbol = "^"


class Terminal(Expression):
    precedence = 4

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class Number(Terminal):
    def __init__(self, value):
        if not isinstance(value, numbers.Number):
            raise TypeError("Number must be an int or float.")
        super().__init__(value)


class Symbol(Terminal):
    def __init__(self, value):
        if not isinstance(value, str):
            raise TypeError("Symbol must be a string.")
        super().__init__(value)


def postvisitor(expr, fn, **kwargs):
    stack = []
    visited = {}
    stack.append(expr)
    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)

        if unvisited_children:
            stack.append(e)
            stack.extend(unvisited_children)
        else:
            visited[e] = fn(e, *(visited[o] for o in e.operands), **kwargs)

    return visited[expr]


@singledispatch
def differentiate(expr, *o, var=None):
    raise TypeError(f"Cannot differentiate expressions of type {type(expr)}")


@differentiate.register(Number)
def _(expr, *o, var=None):
    return Number(0)


@differentiate.register(Symbol)
def _(expr, *o, var=None):
    return Number(1 if expr.value == var else 0)


@differentiate.register(Add)
def _(expr, *o, var=None):
    return Add(*o)


@differentiate.register(Sub)
def _(expr, *o, var=None):
    return Sub(*o)


@differentiate.register(Mul)
def _(expr, *o, var=None):
    u, v = expr.operands
    du_dx, dv_dx = o
    return Add(Mul(du_dx, v), Mul(u, dv_dx))


@differentiate.register(Div)
def _(expr, *o, var=None):
    u, v = expr.operands
    du_dx, dv_dx = o
    return Div(Sub(Mul(du_dx, v), Mul(u, dv_dx)), Pow(v, Number(2)))


@differentiate.register(Pow)
def _(expr, *o, var=None):
    u, v = expr.operands
    du_dx, dv_dx = o
    return Mul(Mul(v, Pow(u, Sub(v, Number(1)))), du_dx)
