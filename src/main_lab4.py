import sys
import ply.yacc as yacc
import Mparser
from TreePrinter import TreePrinter
from TypeChecker import TypeChecker

if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "lab4/example3.m"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(1)

    parser = Mparser.parser
    text = file.read()

    ast = parser.parse(text, lexer=Mparser.scanner, tracking=True)

    # Below code shows how to use visitor
    typeChecker = TypeChecker()
    typeChecker.visit(ast)   # or alternatively ast.accept(typeChecker)
