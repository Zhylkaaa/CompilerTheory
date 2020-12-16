import AST
import SymbolTable
from termcolor import colored

class NodeVisitor(object):

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):  # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)

    def print_error(self, lineno, msg):
        print(colored(f'Error on line {lineno}: {msg}', 'red'))

    # simpler version of generic_visit, not so general
    # def generic_visit(self, node):
    #    for child in node.children:
    #        self.visit(child)


class TypeChecker(NodeVisitor):
    tensor_ops = ['.+', '.-', '.*', './']
    scalar_ops = ['+', '-', '*', '/', '<', '>', '==', '>=', '<=']
    numeric_types = ['int', 'float']

    ops_with_ret_type = {
        '+': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('float', 'float'): 'float',
            ('str', 'str'): 'str',
        },
        '-': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('float', 'float'): 'float',
        },
        '*': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('float', 'float'): 'float',
        },
        '/': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('float', 'float'): 'float',
        },
        '>': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'int',
            ('float', 'int'): 'int',
            ('float', 'float'): 'int',
        },
        '<': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'int',
            ('float', 'int'): 'int',
            ('float', 'float'): 'int',
        },

        '<=': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'int',
            ('float', 'int'): 'int',
            ('float', 'float'): 'int',
        },
        '>=': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'int',
            ('float', 'int'): 'int',
            ('float', 'float'): 'int',
        },
        '==': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'int',
            ('float', 'int'): 'int',
            ('float', 'float'): 'int',
        },
        '!=': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'int',
            ('float', 'int'): 'int',
            ('float', 'float'): 'int',
        },
        '.+': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('float', 'float'): 'float',
            ('str', 'str'): 'str',
        },
        '.-': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('float', 'float'): 'float',
        },
        '.*': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('float', 'float'): 'float',
        },
        './': {
            ('int', 'int'): 'int',
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('float', 'float'): 'float',
        },
    }

    def __init__(self):
        self.current_scope = SymbolTable.SymbolTable(None, 'program')

    def visit_BinExpr(self, node):
        type1, shape_or_val1 = self.visit(node.left)
        type2, shape_or_val2 = self.visit(node.right)
        op = node.op

        is_tensor1 = isinstance(shape_or_val1, tuple)
        is_tensor2 = isinstance(shape_or_val2, tuple)

        if is_tensor1 or is_tensor2:
            if is_tensor1 and not is_tensor2:
                self.print_error(node.lineno, "Can't add tensor to scalar")
            elif is_tensor2 and not is_tensor1:
                self.print_error(node.lineno, "Can't add scalar to tensor")
            else:  # working on tensors
                if (None not in shape_or_val1 and
                    None not in shape_or_val2 and
                    shape_or_val1 != shape_or_val2) or \
                        (len(shape_or_val1) != len(shape_or_val2)):
                    self.print_error(node.lineno, "tensors of incompatible shapes")
                elif None in shape_or_val1 or None in shape_or_val2:
                    for i, j in zip(shape_or_val1, shape_or_val2):
                        if i and j:
                            if i != j:
                                self.print_error(node.lineno, "tensors of incompatible shapes")
                                break

                if op not in self.tensor_ops:
                    self.print_error(node.lineno, f"{op} does not support tensor operations")
                elif (type1, type2) not in self.ops_with_ret_type[op]:
                    self.print_error(node.lineno, f"Can't perform {op} on {(type1, type2)}, incompatible types")
                else:
                    return self.ops_with_ret_type[op][(type1, type2)], shape_or_val1
        else:  # working with scalars
            if op not in self.scalar_ops:
                self.print_error(node.lineno, f"{op} does not support scalar operations")
            elif (type1, type2) not in self.ops_with_ret_type[op]:
                self.print_error(node.lineno, f"Can't perform {op} on {(type1, type2)}, incompatible types")
            else:
                return self.ops_with_ret_type[op][(type1, type2)], shape_or_val1

        return type1, shape_or_val1

    def visit_Variable(self, node):
        name = node.name
        index = node.index

        var = self.current_scope.get(name)
        if var is None:
            self.print_error(node.lineno, "Variable referenced before assignment")
            return "unknown", None

        var_type, var_shape_or_val = var.type

        if index is not None: # TODO: refactor? (use wraped Tuple in visit_index)
            if not isinstance(var_shape_or_val, tuple):
                self.print_error(node.lineno, "Scalar value does not support indexing")
            elif len(index.index) > len(var_shape_or_val):
                self.print_error(node.lineno, f"Index is bigger than {name} shape")
            else:
                for i, idx in enumerate(index.index):
                    t, value = self.visit(idx)
                    if t != 'int':
                        self.print_error(node.lineno, "Index should be integer number")
                    if isinstance(value, tuple):
                        self.print_error(node.lineno, "Vector or matrix can't be used as index")  # TODO: Or do it?

                    if isinstance(idx, AST.IntNum):
                        if var_shape_or_val[i] <= idx.value:
                            self.print_error(node.lineno, f"{idx.value} index out of {node.name} shape "
                              f"{'' if None in var_shape_or_val else var_shape_or_val}")

                if len(index.index) == len(var_shape_or_val):
                    return var_type, None  # it's a scalar
                else:  # it's tensor of lower dimension
                    return var_type, var_shape_or_val[len(index.index):]

        return var_type, var_shape_or_val

    def visit_Transpose(self, node):
        t, shape = self.visit(node)

        if not isinstance(shape, tuple):
            self.print_error(node.lineno, f"Can transpose Tensor, got: {node.__class__.__name__}")
            return t, shape

        if len(shape) == 1:
            new_shape = (1, shape[0])
        else:
            new_shape = (shape[1], shape[0])

        return t, new_shape

    def visit_Negation(self, node):
        t, shape_or_val = self.visit(node)

        if isinstance(shape_or_val, tuple):
            self.print_error(node.lineno, "Negation does not support tensors")

        if t not in self.numeric_types:
            self.print_error(node.lineno, "Negation does not support non-numeric values")

        return t, shape_or_val

    def visit_Tuple(self, node):
        types = []
        shapes = []

        for arg in node.args:
            t, shape_or_val = self.visit(arg)
            types.append(t)
            shapes.append(shape_or_val)
        return types, shapes

    def visit_Function(self, node):
        types, shapes = self.visit(node.args)

        if len(set(types)) > 1:
            self.print_error(node.lineno, f"expected int numbers or variables in arguments got {[t for t in types]}")

        shape = []
        for val in shapes:
            if isinstance(val, tuple):
                self.print_error(node.lineno, f"expected int numbers or variables in arguments got tensor")
                shape.append(None)
            else:
                shape.append(val)

        return "int", tuple(shape)

    def visit_Assignment(self, node):
        identifier = node.identifier
        assignment_type = node.assignment_type
        expr = node.expr

        if assignment_type[0] != '=':
            additional_expression = AST.BinExpr(assignment_type[0], identifier, expr)
            self.visit(additional_expression)
        else:
            t, shape_or_val = self.visit(expr)
            if not isinstance(shape_or_val, tuple):
                shape_or_val = None

            symbol = SymbolTable.VariableSymbol(identifier.name, (t, shape_or_val))
            self.current_scope.put(identifier.name, symbol)

    def visit_ForLoop(self, node):
        self.current_scope = self.current_scope.pushScope('for')
        self.visit(node.range)

        symbol = SymbolTable.VariableSymbol(node.identifier.name, ('int', None))
        self.current_scope.put(node.identifier.name, symbol)
        self.visit(node.instructions)

        self.current_scope = self.current_scope.popScope()

    def visit_Range(self, node):
        type1, shape_or_val1 = self.visit(node.start)
        type2, shape_or_val2 = self.visit(node.end)

        if type1 != 'int' or type2 != 'int':
            self.print_error(node.lineno, f"Range operator accepts (int, int), got {(type1, type2)}")

        if isinstance(shape_or_val1, tuple) or isinstance(shape_or_val2, tuple):
            self.print_error(node.lineno, "Range operator only works with scalar values")

    def check_condition(self, node, condition=None):
        if condition is None:
            condition = node.condition

        t, shape_or_val = self.visit(condition)

        if t != 'int':
            self.print_error(node.lineno, f"Condition should evaluate to int(bool), got {t}")
        if isinstance(shape_or_val, tuple):
            self.print_error(node.lineno, f"Condition should be a scalar")

    def visit_While(self, node):
        self.current_scope = self.current_scope.pushScope('while')

        self.check_condition(node)
        self.visit(node.instructions)

        self.current_scope = self.current_scope.popScope()

    def visit_IfElse(self, node):
        self.current_scope = self.current_scope.pushScope('if')

        self.check_condition(node)
        self.visit(node.then_instructions)

        self.current_scope = self.current_scope.popScope()

        if node.else_instructions:
            self.current_scope = self.current_scope.pushScope('else')
            self.visit(node.else_instructions)
            self.current_scope = self.current_scope.popScope()

    def visit_Instructions(self, node):
        for instruction in node.instructions:
            self.visit(instruction)

    def visit_Scope(self, node):
        self.current_scope = self.current_scope.pushScope('block')

        self.visit(node.instructions)

        self.current_scope = self.current_scope.popScope()

    def visit_Print(self, node):
        self.visit(node.args)

    def visit_Controlflow(self, node):

        if node.command in ['break', 'continue']:
            if self.current_scope.scope_name not in ['while', 'for']:
                self.print_error(node.lineno, f"{node.command} out of loop scope")

        if node.ret_val:
            self.visit(node.ret_val)

    def visit_IntNum(self, node):
        return 'int', node.value

    def visit_FloatNum(self, node):
        return 'float', node.value

    def visit_StringLiteral(self, node):
        return 'str', node.value

    def visit_Tensor(self, node):  # TODO: support more than 2-d matrix
        sizes = set()
        dtype = set()

        for elem in node.value:
            t, val_or_shape = self.visit(elem)
            if not isinstance(val_or_shape, tuple):
                val_or_shape = ()
            dtype.add(t)
            sizes.add(val_or_shape)

        if 'int' in dtype and 'float' in dtype:
            dtype.remove('int')

        if len(dtype) > 1:
            self.print_error(node.lineno, "Can only keep elements of the same type")

        if len(sizes) > 1:
            self.print_error(node.lineno, "Dimensions should be of the same shape")

        return dtype.pop(), (len(node.value), *sizes.pop())
