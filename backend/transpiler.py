# transpiler.py

from ast_nodes import ASTNode, BlockNode

class Transpiler:
    """
    Transpilador de nuestro mini-Python a JavaScript.
    Recibe el AST y usa los métodos to_js() de cada nodo.
    """
    def __init__(self, ast_root: ASTNode):
        self.ast_root = ast_root

    def transpile(self) -> str:
        # El AST raíz es un BlockNode con la lista de statements
        context = {"declared_vars": set()}
        return self.ast_root.to_js(indent=0, context=context)


def transpile(ast_root: ASTNode) -> str:
    """
    Función de conveniencia, por si prefieres no usar la clase.
    """
    t = Transpiler(ast_root)
    return t.transpile()
