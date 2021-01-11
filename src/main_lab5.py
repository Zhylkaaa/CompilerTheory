import sys
import ply.yacc as yacc
import Mparser
from TreePrinter import TreePrinter
from TypeChecker import TypeChecker
from Interpreter import Interpreter


if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "lab5/triangle.m"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    parser = Mparser.parser
    text = file.read()

    ast = parser.parse(text, lexer=Mparser.scanner, tracking=True)
    if not parser.errorok:
        sys.exit()

    #ast.printTree()

    # Below code shows how to use visitor
    typeChecker = TypeChecker()
    typeChecker.visit(ast)   # or alternatively ast.accept(typeChecker)

    if typeChecker.error_count == 0:
        ast.accept(Interpreter())

    # in future
    # ast.accept(OptimizationPass1())
    # ast.accept(OptimizationPass2())
    # ast.accept(CodeGenerator())