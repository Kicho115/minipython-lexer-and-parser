from ast_nodes import (
    ASTNode, NumberNode, StringNode, BooleanNode, IdentifierNode,
    BinOpNode, AssignNode, PrintNode, IfNode, WhileNode, BlockNode
)

class NodeFactory:
    @staticmethod
    def create(node_type, *args):
        """
        Factory method to create AST nodes
        node_type: string indicating the type of node to create
        args: arguments to pass to the node constructor
        """
        node_creators = {
            'number': lambda x: NumberNode(x),
            'string': lambda x: StringNode(x),
            'boolean': lambda x: BooleanNode(x),
            'identifier': lambda x: IdentifierNode(x),
            'binop': lambda left, op, right: BinOpNode(left, op, right),
            'assign': lambda target, value: AssignNode(target, value),
            'print': lambda value: PrintNode(value),
            'if': lambda condition, body, else_body=None: IfNode(condition, body, else_body),
            'while': lambda condition, body: WhileNode(condition, body),
            'block': lambda statements: BlockNode(statements)
        }

        if node_type not in node_creators:
            raise ValueError(f"Unknown node type: {node_type}")

        return node_creators[node_type](*args)
