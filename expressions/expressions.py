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
            if isinstance(operand, Operator) and operand.precedence < self.precedence:
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
        if not isinstance(value, (int, float)):
            raise TypeError("Number must be an int or float.")
        super().__init__(value)


class Symbol(Terminal):
    def __init__(self, value):
        if not isinstance(value, str):
            raise TypeError("Symbol must be a string.")
        super().__init__(value)