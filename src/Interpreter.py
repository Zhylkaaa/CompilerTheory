import AST
import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys
import operator
import numpy as np

sys.setrecursionlimit(10000)


class Interpreter(object):
    operator_mapping = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '.+': operator.add,
        '.-': operator.sub,
        '.*': operator.mul,
        './': operator.truediv,
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
    }

    def error(self, msg, lineno):
        raise RuntimeError(f'{msg}, line {lineno}')

    def eval_expr(self, op, left, right):
        return self.operator_mapping[op](left, right)

    def __init__(self):
        self.memory_stack = MemoryStack()

    @on('node')
    def visit(self, node):
        pass

    @when(AST.Node)
    def visit(self, node):
        self.error(f'InterpreterFatalError: can\'t execute instruction of type {node.__class__.__name__}', node.lineno)

    @when(AST.BinExpr)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        if node.op == '/' and r2 == 0:
            self.error('ArithmeticError: Division by zero', node.lineno)
        try:
            ret = self.eval_expr(node.op, r1, r2)
            return ret
        except Exception as e:
            self.error(e, node.lineno)

    @when(AST.Assignment)
    def visit(self, node):
        r = node.expr.accept(self)
        idf = node.identifier

        if idf.index is None:  # working with simple variable
            if node.assignment_type == '=':
                value = r
            else:
                try:
                    left = self.memory_stack.get(idf.name)
                except KeyError:
                    self.error(f'NameError: name {idf.name} used before assignment', node.lineno)
                value = self.eval_expr(node.assignment_type[:-1], left, r)

            self.memory_stack.set(idf.name, value)
            return value
        else:  # variable with indexes
            index = idf.index.accept(self)
            var_name = idf.name
            try:
                var_value = self.memory_stack.get(var_name)
            except KeyError:
                self.error(f'{var_name} does not declared in this scope', node.lineno)

            if all([isinstance(i, int) for i in index]) and index > var_value.shape:
                self.error(f'{index} index is greater than {var_name} shape {var_value.shape}', node.lineno)

            if node.assignment_type == '=':
                value = r
            else:
                try:
                    value = self.eval_expr(node.assignment_type[:-1], var_value[index], r)
                except Exception as e:
                    self.error(f'InternalInterpreterError: {e}', node.lineno)
            var_value[index] = value
            return value

    @when(AST.Index)
    def visit(self, node):
        idx = []
        for el in node.index:
            ev_el = el.accept(self)
            if not (isinstance(ev_el, int) or isinstance(ev_el, range)):
                self.error('index element is not of int or range type', node.lineno)
            idx.append(ev_el)
        return tuple(idx)

    @when(AST.Variable)
    def visit(self, node):
        try:
            var_value = self.memory_stack.get(node.name)
        except KeyError:
            self.error(f'{node.name} does not declared in this scope', node.lineno)

        if node.index:
            index = node.index.accept(self)

            if all([isinstance(i, int) for i in index]) and index > var_value.shape:
                self.error(f'{index} index is greater than {node.name} shape {var_value.shape}', node.lineno)

            return var_value[index]
        return var_value

    @when(AST.Transpose)
    def visit(self, node):
        #TODO: check for scalars??
        expr = node.expr.accept(self)
        return np.transpose(expr)

    @when(AST.Negation)
    def visit(self, node):
        expr = node.expr.accept(self)
        return -expr

    @when(AST.Tuple)
    def visit(self, node):
        t = []
        for arg in node.args:
            t.append(arg.accept(self))
        return tuple(t)

    @when(AST.Function)
    def visit(self, node):
        args = node.args.accept(self)
        if node.function_name == 'eye':
            return np.eye(args[0])
        return {
            'ones': np.ones,
            'zeros': np.zeros
        }[node.function_name](args)

    @when(AST.While)
    def visit(self, node):
        r = None
        self.memory_stack.push(Memory('while'))
        try:
            while node.condition.accept(self):
                try:
                    r = node.instructions.accept(self)
                except ContinueException:
                    pass
        except BreakException:
            pass
        finally:
            self.memory_stack.pop()
        return r

    @when(AST.Range)
    def visit(self, node):
        start = node.start.accept(self)
        end = node.end.accept(self)

        if not (isinstance(start, int) and isinstance(end, int)):
            self.error('range only support int values', node.lineno)
        else:
            return range(start, end)

    @when(AST.ForLoop)
    def visit(self, node):
        ret = None
        r = node.range.accept(self)
        iterator_name = node.identifier.name
        self.memory_stack.push(Memory('for'))
        try:
            for i in r:
                self.memory_stack.set(iterator_name, i)
                try:
                    ret = node.instructions.accept(self)
                except ContinueException:
                    pass
        except BreakException:
            pass
        finally:
            self.memory_stack.pop()
        return ret

    @when(AST.IfElse)
    def visit(self, node):
        cond = node.condition.accept(self)
        if cond:
            self.memory_stack.push(Memory('then'))
            try:
                node.then_instructions.accept(self)
            finally:
                self.memory_stack.pop()
        elif node.else_instructions:
            self.memory_stack.push(Memory('else'))
            try:
                node.else_instructions.accept(self)
            finally:
                self.memory_stack.pop()

    @when(AST.Instructions)
    def visit(self, node):
        for instruction in node.instructions:
            try:
                instruction.accept(self)
            except ReturnValueException as e:
                value = e
                if e is None or e == 0:
                    exit_code = 0
                elif not isinstance(value, int):
                    print(f'Returned value: {value}')
                    exit_code = -1
                else:
                    exit_code = value
                sys.exit(exit_code)

    @when(AST.Scope)
    def visit(self, node):
        self.memory_stack.push(Memory('scope'))
        try:
            node.instructions.accept(self)
        finally:
            self.memory_stack.pop()

    @when(AST.Print)
    def visit(self, node):
        args = node.args.accept(self)
        return print(' '.join([str(arg) for arg in args]))

    @when(AST.Controlflow)
    def visit(self, node):
        if node.command == 'break':
            raise BreakException()
        elif node.command == 'continue':
            raise ContinueException()
        elif node.command == 'return':
            value = node.ret_val.accept(self) if node.ret_val else None
            raise ReturnValueException(value)

    @when(AST.IntNum)
    def visit(self, node):
        return node.value

    @when(AST.FloatNum)
    def visit(self, node):
        return node.value

    @when(AST.StringLiteral)
    def visit(self, node):
        return node.value

    @when(AST.Tensor)
    def visit(self, node):
        v = []
        for el in node.value:
            v.append(el.accept(self))
        return np.array(v)
