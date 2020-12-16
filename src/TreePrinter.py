from __future__ import print_function
import AST


def addToClass(cls):

    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator


class TreePrinter:

    @addToClass(AST.Node)
    def printTree(self, indent=0):
        raise Exception("printTree not defined in class " + self.__class__.__name__)


    @addToClass(AST.IntNum)
    def printTree(self, indent=0):
        prefix = '|  '*indent
        print(f'{prefix}{self.value}')

    @addToClass(AST.FloatNum)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(f'{prefix}{self.value}')

    @addToClass(AST.StringLiteral)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(f'{prefix}{self.value}')

    @addToClass(AST.Tensor)
    def printTree(self, indent=0):
        print(self.lineno)
        prefix = '|  ' * indent

        print(prefix + 'VECTOR')
        for idx, row in enumerate(self.value):
            row.printTree(indent=indent+1)

    @addToClass(AST.Index)
    def printTree(self, indent=0):
        for i in self.index:
            i.printTree(indent=indent)

    @addToClass(AST.Variable)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        if self.index:
            print(prefix + 'REF')
            print(prefix + '|  ' + self.name)
            self.index.printTree(indent=indent+1)
        else:
            print(prefix + self.name)

    @addToClass(AST.BinExpr)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + self.op)
        self.left.printTree(indent=indent+1)
        self.right.printTree(indent=indent+1)

    @addToClass(AST.Transpose)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + 'TRANSPOSE')
        self.expr.printTree(indent=indent+1)

    @addToClass(AST.Negation)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + 'NEGATION')
        self.expr.printTree(indent=indent+1)

    @addToClass(AST.Function)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + self.function_name)
        self.args.printTree(indent=indent+1)

    @addToClass(AST.Assignment)
    def printTree(self, indent=0):
        print(self.lineno)
        prefix = '|  ' * indent
        print(prefix + self.assignment_type)
        self.identifier.printTree(indent=indent+1)
        self.expr.printTree(indent=indent+1)

    @addToClass(AST.ForLoop)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + 'FOR')
        self.identifier.printTree(indent=indent+1)
        self.range.printTree(indent=indent+1)
        self.instructions.printTree(indent=indent+1)

    @addToClass(AST.Range)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + 'RANGE')
        self.start.printTree(indent=indent+1)
        self.end.printTree(indent=indent+1)

    @addToClass(AST.While)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + 'WHILE')
        self.condition.printTree(indent=indent+1)
        self.instructions.printTree(indent=indent+1)

    @addToClass(AST.IfElse)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + 'IF')
        self.condition.printTree(indent=indent+1)
        print(prefix + 'THEN')
        self.then_instructions.printTree(indent=indent+1)
        if self.else_instructions:
            print(prefix + 'ELSE')
            self.else_instructions.printTree(indent=indent+1)

    @addToClass(AST.Instructions)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        for instruction in self.instructions:
            instruction.printTree(indent=indent)

    @addToClass(AST.Scope)
    def printTree(self, indent=0):
        self.instructions.printTree(indent=indent)

    @addToClass(AST.Tuple)
    def printTree(self, indent=0):
        for arg in self.args:
            arg.printTree(indent=indent)

    @addToClass(AST.Print)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + 'PRINT')
        self.args.printTree(indent=indent+1)

    @addToClass(AST.Controlflow)
    def printTree(self, indent=0):
        prefix = '|  ' * indent
        print(prefix + self.command)
        if self.ret_val:
            self.ret_val.printTree(indent=indent+1)

    @addToClass(AST.Error)
    def printTree(self, indent=0):
        pass
        # fill in the body


    # define printTree for other classes
    # ...
