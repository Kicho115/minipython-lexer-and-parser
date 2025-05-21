from node_factory import NodeFactory

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.indent_stack = [0]

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '', -1)

    def match(self, *expected_types):
        token_type, value, line = self.current()
        if token_type in expected_types:
            self.pos += 1
            return (token_type, value)
        raise SyntaxError(f"Expected {expected_types}, got {token_type} at line {line}")

    def parse(self):
        statements = []
        while self.current()[0] != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return NodeFactory.create('block', statements)

    def parse_statement(self):
        token_type, value, line = self.current()

        if token_type == 'ID':
            # x = expr
            target = NodeFactory.create('identifier', value)
            self.match('ID')
            self.match('ASSIGN')
            expr = self.parse_expression()
            return NodeFactory.create('assign', target, expr)

        elif token_type == 'PRINT':
            self.match('PRINT')
            self.match('LPAREN')
            expr = self.parse_expression()
            self.match('RPAREN')
            return NodeFactory.create('print', expr)

        elif token_type == 'IF':
            return self.parse_if()
            
        elif token_type == 'WHILE':
            return self.parse_while()
            
        elif token_type == 'INDENT':
            self.match('INDENT')
            return None
            
        elif token_type == 'DEDENT':
            self.match('DEDENT')
            return None

        elif token_type == 'EOF':
            return None

        else:
            raise SyntaxError(f"Unexpected token {token_type} at line {line}")

    def parse_if(self):
        self.match('IF')
        condition = self.parse_expression()
        self.match('COLON')
        self.match('INDENT')

        body = []
        while self.current()[0] != 'DEDENT' and self.current()[0] != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        if self.current()[0] == 'DEDENT':
            self.match('DEDENT')
        
        # Check for else clause
        else_body = None
        if self.current()[0] == 'ELSE':
            self.match('ELSE')
            self.match('COLON')
            self.match('INDENT')
            
            else_body = []
            while self.current()[0] != 'DEDENT' and self.current()[0] != 'EOF':
                stmt = self.parse_statement()
                if stmt:
                    else_body.append(stmt)
                
            if self.current()[0] == 'DEDENT':
                self.match('DEDENT')
            
        return NodeFactory.create('if', condition, body, else_body)

    def parse_while(self):
        self.match('WHILE')
        condition = self.parse_expression()
        self.match('COLON')
        self.match('INDENT')

        body = []
        while self.current()[0] != 'DEDENT' and self.current()[0] != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        if self.current()[0] == 'DEDENT':
            self.match('DEDENT')
        return NodeFactory.create('while', condition, body)

    def parse_expression(self):
        # Comparaciones como x > 3 o a == b
        left = self.parse_arith_expression()

        while self.current()[0] in ('GT', 'LT', 'EQ', 'NEQ', 'GTE', 'LTE'):
            op = self.match('GT', 'LT', 'EQ', 'NEQ', 'GTE', 'LTE')[0]
            right = self.parse_arith_expression()
            left = NodeFactory.create('binop', left, op, right)

        return left

    def parse_arith_expression(self):
        left = self.parse_term()
        while self.current()[0] in ('PLUS', 'MINUS'):
            op = self.match('PLUS', 'MINUS')[0]
            right = self.parse_term()
            left = NodeFactory.create('binop', left, op, right)
        return left

    def parse_term(self):
        left = self.parse_factor()

        while self.current()[0] in ('MULT', 'DIV'):
            op = self.match('MULT', 'DIV')[0]
            right = self.parse_factor()
            left = NodeFactory.create('binop', left, op, right)

        return left

    def parse_factor(self):
        token_type, value, _ = self.current()

        if token_type == 'NUMBER':
            self.match('NUMBER')
            return NodeFactory.create('number', value)
        elif token_type == 'STRING':
            self.match('STRING')
            return NodeFactory.create('string', value)
        elif token_type in ('TRUE', 'FALSE'):
            self.match(token_type)
            return NodeFactory.create('boolean', value)
        elif token_type == 'ID':
            self.match('ID')
            return NodeFactory.create('identifier', value)
        elif token_type == 'LPAREN':
            self.match('LPAREN')
            expr = self.parse_expression()
            self.match('RPAREN')
            return expr
        else:
            raise SyntaxError(f"Unexpected token {token_type}")
