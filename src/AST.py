class Node(object):
    def __init__(self):
        self.lineno = None

    def accept(self, visitor):
        return visitor.visit(self)


class IntNum(Node):
    def __init__(self, value):
        super().__init__()
        self.value = int(value)


class FloatNum(Node):
    def __init__(self, value):
        super().__init__()
        self.value = float(value)


class StringLiteral(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value


class Tensor(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value


class Index(Node):
    def __init__(self, index):
        super().__init__()
        self.index = index


class Variable(Node):
    def __init__(self, name, index=None):
        super().__init__()
        self.name = name
        self.index = index


class BinExpr(Node):
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right


class Transpose(Node):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr


class Negation(Node):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr


class Tuple(Node):
    def __init__(self, args):
        self.args = args


class Function(Node):
    def __init__(self, function_name, args):
        super().__init__()
        self.function_name = function_name
        self.args = args


class Assignment(Node):
    def __init__(self, identifier, assignment_type, expr):
        super().__init__()
        self.identifier = identifier
        self.assignment_type = assignment_type
        self.expr = expr


class ForLoop(Node):
    def __init__(self, identifier, range, instructions):
        super().__init__()
        self.identifier = identifier
        self.range = range
        self.instructions = instructions


class Range(Node):
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end


class While(Node):
    def __init__(self, condition, instructions):
        super().__init__()
        self.condition = condition
        self.instructions = instructions


class IfElse(Node):
    def __init__(self, condition, then_instructions, else_instructions=None):
        super().__init__()
        self.condition = condition
        self.then_instructions = then_instructions
        self.else_instructions = else_instructions


class Instructions(Node):
    def __init__(self, instructions):
        super().__init__()
        self.instructions = instructions


class Scope(Node):
    def __init__(self, instructions):
        super().__init__()
        self.instructions = instructions


class Print(Node):
    def __init__(self, args):
        super().__init__()
        self.args = args


class Controlflow(Node):
    def __init__(self, command, ret_val=None):
        super().__init__()
        self.command = command
        self.ret_val = ret_val
# ...
# fill out missing classes
# ...


class Error(Node):
    def __init__(self):
        super().__init__()
        pass
