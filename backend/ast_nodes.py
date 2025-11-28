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


class RangeNode(ASTNode):
    def __init__(self, start, stop, step=None):
        """
        range(stop) -> start=0, stop=stop, step=1
        range(start, stop) -> start=start, stop=stop, step=1
        range(start, stop, step) -> start=start, stop=stop, step=step
        """
        self.start = start
        self.stop = stop
        self.step = step if step is not None else NumberNode("1")
    
    def __str__(self):
        if self.step and not (isinstance(self.step, NumberNode) and self.step.value == 1):
            return f"range({self.start}, {self.stop}, {self.step})"
        else:
            return f"range({self.start}, {self.stop})"
    
    def to_tree(self, level=0):
        result = "  " * level + "RangeNode\n"
        result += "  " * (level + 1) + "start:\n"
        result += self.start.to_tree(level + 2) + "\n"
        result += "  " * (level + 1) + "stop:\n"
        result += self.stop.to_tree(level + 2) + "\n"
        if self.step and not (isinstance(self.step, NumberNode) and self.step.value == 1):
            result += "  " * (level + 1) + "step:\n"
            result += self.step.to_tree(level + 2) + "\n"
        return result

    def to_js(self, indent=0, context=None):
        # No se transpila directamente, se usa en ForNode
        return f"range({self.start.to_js(0, context)}, {self.stop.to_js(0, context)}, {self.step.to_js(0, context)})"


class ForNode(ASTNode):
    def __init__(self, variable, iterable, body):
        """
        variable: IdentifierNode (el nombre de la variable del bucle)
        iterable: RangeNode (por ahora solo soportamos range)
        body: lista de nodos (el cuerpo del bucle)
        """
        self.variable = variable
        self.iterable = iterable
        self.body = body
    
    def __str__(self):
        result = f"for {self.variable} in {self.iterable}:\n"
        for stmt in self.body:
            result += f"    {stmt}\n"
        return result
    
    def to_tree(self, level=0):
        result = "  " * level + "ForNode\n"
        result += "  " * (level + 1) + "variable:\n"
        result += self.variable.to_tree(level + 2) + "\n"
        result += "  " * (level + 1) + "iterable:\n"
        result += self.iterable.to_tree(level + 2) + "\n"
        result += "  " * (level + 1) + "body:\n"
        for stmt in self.body:
            result += stmt.to_tree(level + 2) + "\n"
        return result

    def to_js(self, indent=0, context=None):
        if context is None:
            context = {}

        indent_str = " " * (indent * 4)
        
        # Obtener el nombre de la variable
        var_name = self.variable.name if isinstance(self.variable, IdentifierNode) else str(self.variable)
        
        # Asumimos que iterable es un RangeNode
        if isinstance(self.iterable, RangeNode):
            start_js = self.iterable.start.to_js(0, context)
            stop_js = self.iterable.stop.to_js(0, context)
            step_js = self.iterable.step.to_js(0, context)
            
            # Determinar el operador de comparación
            # Si step es positivo: <, si es negativo: >
            # Por simplicidad, asumimos step positivo (lo más común)
            comp_op = "<"
            
            # Determinar el incremento
            if isinstance(self.iterable.step, NumberNode) and self.iterable.step.value == 1:
                increment = f"{var_name}++"
            else:
                increment = f"{var_name} += {step_js}"
            
            # Marcar la variable como declarada
            declared = context.setdefault("declared_vars", set())
            declared.add(var_name)
            
            # Generar el for de JavaScript
            header = f"{indent_str}for (let {var_name} = {start_js}; {var_name} {comp_op} {stop_js}; {increment}) {{"
            
            # Generar el cuerpo
            body_lines = [
                stmt.to_js(indent + 1, context) for stmt in self.body
            ]
            body_js = "\n".join(body_lines)
            
            return f"{header}\n{body_js}\n{indent_str}}}"
        else:
            raise NotImplementedError("Only range() is supported in for loops")


class FunctionDefNode(ASTNode):
    def __init__(self, name, params, body):
        """
        name: string (nombre de la función)
        params: lista de IdentifierNode (parámetros)
        body: lista de nodos (cuerpo de la función)
        """
        self.name = name
        self.params = params
        self.body = body
    
    def __str__(self):
        params_str = ", ".join(str(p) for p in self.params)
        result = f"def {self.name}({params_str}):\n"
        for stmt in self.body:
            result += f"    {stmt}\n"
        return result
    
    def to_tree(self, level=0):
        result = "  " * level + f"FunctionDefNode({self.name})\n"
        result += "  " * (level + 1) + "params:\n"
        for param in self.params:
            result += param.to_tree(level + 2) + "\n"
        result += "  " * (level + 1) + "body:\n"
        for stmt in self.body:
            result += stmt.to_tree(level + 2) + "\n"
        return result

    def to_js(self, indent=0, context=None):
        if context is None:
            context = {}

        indent_str = " " * (indent * 4)
        
        # Marcar la función como declarada en el contexto global
        declared = context.setdefault("declared_vars", set())
        declared.add(self.name)
        
        # Parámetros
        params_js = ", ".join(p.to_js(0, context) for p in self.params)
        
        # CREAR UN NUEVO CONTEXTO LOCAL PARA EL CUERPO DE LA FUNCIÓN
        # Los parámetros ya están declarados en el scope de la función
        local_context = {"declared_vars": set()}
        
        # Agregar los parámetros como variables ya declaradas en el scope local
        for param in self.params:
            if isinstance(param, IdentifierNode):
                local_context["declared_vars"].add(param.name)
        
        # Cuerpo de la función con el contexto local
        body_lines = [
            stmt.to_js(indent + 1, local_context) for stmt in self.body
        ]
        body_js = "\n".join(body_lines)
        
        return f"{indent_str}function {self.name}({params_js}) {{\n{body_js}\n{indent_str}}}"


class FunctionCallNode(ASTNode):
    def __init__(self, name, args):
        """
        name: string o IdentifierNode (nombre de la función)
        args: lista de expresiones (argumentos)
        """
        self.name = name
        self.args = args
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.name}({args_str})"
    
    def to_tree(self, level=0):
        result = "  " * level + f"FunctionCallNode({self.name})\n"
        result += "  " * (level + 1) + "args:\n"
        for arg in self.args:
            result += arg.to_tree(level + 2) + "\n"
        return result

    def to_js(self, indent=0, context=None):
        # Para llamadas a funciones que aparecen como expresiones
        name_str = self.name if isinstance(self.name, str) else self.name.to_js(0, context)
        args_js = ", ".join(arg.to_js(0, context) for arg in self.args)
        return f"{name_str}({args_js})"


class ReturnNode(ASTNode):
    def __init__(self, value=None):
        """
        value: expresión a retornar (puede ser None)
        """
        self.value = value
    
    def __str__(self):
        if self.value:
            return f"return {self.value}"
        return "return"
    
    def to_tree(self, level=0):
        result = "  " * level + "ReturnNode\n"
        if self.value:
            result += self.value.to_tree(level + 1) + "\n"
        return result

    def to_js(self, indent=0, context=None):
        indent_str = " " * (indent * 4)
        if self.value:
            value_js = self.value.to_js(0, context)
            return f"{indent_str}return {value_js};"
        return f"{indent_str}return;"