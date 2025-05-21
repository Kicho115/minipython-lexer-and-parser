class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = int(value)

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

class BooleanNode(ASTNode):
    def __init__(self, value):
        self.value = value

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class AssignNode(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

class IfNode(ASTNode):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements
