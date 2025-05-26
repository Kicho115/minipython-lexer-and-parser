class ASTNode:
    def to_tree(self, level=0):
        return "  " * level + self.__class__.__name__

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = int(value)
    
    def __str__(self):
        return str(self.value)
    
    def to_tree(self, level=0):
        return "  " * level + f"NumberNode({self.value})"

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return f'"{self.value}"'
    
    def to_tree(self, level=0):
        return "  " * level + f"StringNode({self.value})"

class BooleanNode(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def to_tree(self, level=0):
        return "  " * level + f"BooleanNode({self.value})"

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def to_tree(self, level=0):
        return "  " * level + f"IdentifierNode({self.name})"

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def __str__(self):
        return f"({self.left} {self.op} {self.right})"
    
    def to_tree(self, level=0):
        result = "  " * level + f"BinOpNode({self.op})\n"
        result += self.left.to_tree(level + 1) + "\n"
        result += self.right.to_tree(level + 1)
        return result

class AssignNode(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value
    
    def __str__(self):
        return f"{self.target} = {self.value}"
    
    def to_tree(self, level=0):
        result = "  " * level + "AssignNode\n"
        result += self.target.to_tree(level + 1) + "\n"
        result += self.value.to_tree(level + 1)
        return result

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return f"print({self.value})"
    
    def to_tree(self, level=0):
        result = "  " * level + "PrintNode\n"
        result += self.value.to_tree(level + 1)
        return result

class IfNode(ASTNode):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body
    
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

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
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
