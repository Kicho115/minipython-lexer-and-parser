# ast_nodes.py

class ASTNode:
    def to_tree(self, level=0):
        return "  " * level + self.__class__.__name__

    def to_js(self, indent=0, context=None):
        """
        Genera el código JavaScript equivalente a este nodo.
        indent: nivel de indentación (en bloques)
        context: diccionario para compartir información (por ejemplo variables declaradas)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement to_js()")


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = int(value)
    
    def __str__(self):
        return str(self.value)
    
    def to_tree(self, level=0):
        return "  " * level + f"NumberNode({self.value})"

    def to_js(self, indent=0, context=None):
        return str(self.value)


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return f'"{self.value}"'
    
    def to_tree(self, level=0):
        return "  " * level + f"StringNode({self.value})"

    def to_js(self, indent=0, context=None):
        # Nota: aquí podrías escapar comillas si quieres ser más estricto
        return f'"{self.value}"'


class BooleanNode(ASTNode):
    def __init__(self, value):
        # en el lexer viene como 'True' / 'False'
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def to_tree(self, level=0):
        return "  " * level + f"BooleanNode({self.value})"

    def to_js(self, indent=0, context=None):
        if self.value in (True, "True"):
            return "true"
        else:
            return "false"


class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def to_tree(self, level=0):
        return "  " * level + f"IdentifierNode({self.name})"

    def to_js(self, indent=0, context=None):
        return self.name


class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op          # 'PLUS', 'MINUS', 'GT', 'EQ', etc.
        self.right = right
    
    def __str__(self):
        # Opcional: mostrar el operador real en lugar del token
        op_str = self._op_to_symbol(self.op)
        return f"({self.left} {op_str} {self.right})"
    
    def to_tree(self, level=0):
        result = "  " * level + f"BinOpNode({self.op})\n"
        result += self.left.to_tree(level + 1) + "\n"
        result += self.right.to_tree(level + 1)
        return result

    def _op_to_symbol(self, op):
        mapping = {
            'PLUS': '+',
            'MINUS': '-',
            'MULT': '*',
            'DIV': '/',
            'GT': '>',
            'LT': '<',
            'EQ': '==',
            'NEQ': '!=',
            'GTE': '>=',
            'LTE': '<=',
        }
        return mapping.get(op, op)

    def to_js(self, indent=0, context=None):
        op_symbol = self._op_to_symbol(self.op)
        left_js = self.left.to_js(0, context)
        right_js = self.right.to_js(0, context)
        return f"({left_js} {op_symbol} {right_js})"


class AssignNode(ASTNode):
    def __init__(self, target, value):
        self.target = target  # IdentifierNode
        self.value = value
    
    def __str__(self):
        return f"{self.target} = {self.value}"
    
    def to_tree(self, level=0):
        result = "  " * level + "AssignNode\n"
        result += self.target.to_tree(level + 1) + "\n"
        result += self.value.to_tree(level + 1)
        return result

    def to_js(self, indent=0, context=None):
        if context is None:
            context = {}

        declared = context.setdefault("declared_vars", set())

        # Sólo soportamos asignación a identificadores en este mini-lenguaje
        if isinstance(self.target, IdentifierNode):
            name = self.target.name
        else:
            name = self.target.to_js(0, context)

        value_js = self.value.to_js(0, context)
        indent_str = " " * (indent * 4)

        if name not in declared:
            declared.add(name)
            return f"{indent_str}let {name} = {value_js};"
        else:
            return f"{indent_str}{name} = {value_js};"


class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return f"print({self.value})"
    
    def to_tree(self, level=0):
        result = "  " * level + "PrintNode\n"
        result += self.value.to_tree(level + 1)
        return result

    def to_js(self, indent=0, context=None):
        indent_str = " " * (indent * 4)
        value_js = self.value.to_js(0, context)
        # Python print() -> console.log()
        return f"{indent_str}console.log({value_js});"


class IfNode(ASTNode):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body            # lista de nodos
        self.else_body = else_body  # lista de nodos o None
    
    def __str__(self):
        result = f"if {self.condition}:\n"
        for stmt in self.body:
            result += f"    {stmt}\n"
        if self.else_body:
            result += "else:\n"
            for stmt in self.else_body:
                result += f"    {stmt}\n"
        return result
    
    def to_tree(self, level=0):
        result = "  " * level + "IfNode\n"
        result += "  " * (level + 1) + "condition:\n"
        result += self.condition.to_tree(level + 2) + "\n"
        result += "  " * (level + 1) + "body:\n"
        for stmt in self.body:
            result += stmt.to_tree(level + 2) + "\n"
        if self.else_body:
            result += "  " * (level + 1) + "else_body:\n"
            for stmt in self.else_body:
                result += stmt.to_tree(level + 2) + "\n"
        return result

    def to_js(self, indent=0, context=None):
        if context is None:
            context = {}

        indent_str = " " * (indent * 4)
        cond_js = self.condition.to_js(0, context)

        body_lines = [
            stmt.to_js(indent + 1, context) for stmt in self.body
        ]
        body_js = "\n".join(body_lines)

        code = f"{indent_str}if ({cond_js}) {{\n{body_js}\n{indent_str}}}"

        if self.else_body is not None:
            else_lines = [
                stmt.to_js(indent + 1, context) for stmt in self.else_body
            ]
            else_js = "\n".join(else_lines)
            code += f" else {{\n{else_js}\n{indent_str}}}"

        return code


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body  # lista de nodos
    
    def __str__(self):
        result = f"while {self.condition}:\n"
        for stmt in self.body:
            result += f"    {stmt}\n"
        return result
    
    def to_tree(self, level=0):
        result = "  " * level + "WhileNode\n"
        result += "  " * (level + 1) + "condition:\n"
        result += self.condition.to_tree(level + 2) + "\n"
        result += "  " * (level + 1) + "body:\n"
        for stmt in self.body:
            result += stmt.to_tree(level + 2) + "\n"
        return result

    def to_js(self, indent=0, context=None):
        if context is None:
            context = {}

        indent_str = " " * (indent * 4)
        cond_js = self.condition.to_js(0, context)

        body_lines = [
            stmt.to_js(indent + 1, context) for stmt in self.body
        ]
        body_js = "\n".join(body_lines)

        return f"{indent_str}while ({cond_js}) {{\n{body_js}\n{indent_str}}}"


class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    
    def __str__(self):
        return "\n".join(str(stmt) for stmt in self.statements)
    
    def to_tree(self, level=0):
        result = "  " * level + "BlockNode\n"
        for stmt in self.statements:
            result += stmt.to_tree(level + 1) + "\n"
        return result

    def to_js(self, indent=0, context=None):
        # Context compartido para todo el programa
        if context is None:
            context = {"declared_vars": set()}

        lines = [
            stmt.to_js(indent, context) for stmt in self.statements
        ]
        return "\n".join(lines)
