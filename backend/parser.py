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

        if token_type == 'DEF':
            return self.parse_function_def()

        elif token_type == 'RETURN':
            return self.parse_return()

        elif token_type == 'ID':
            # Puede ser asignación o llamada a función
            next_pos = self.pos + 1
            if next_pos < len(self.tokens) and self.tokens[next_pos][0] == 'LPAREN':
                # Es una llamada a función como statement
                name = value
                self.match('ID')
                self.match('LPAREN')
                args = self.parse_arguments()
                self.match('RPAREN')
                return NodeFactory.create('function_call', name, args)
            else:
                # Es una asignación: x = expr
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
        
        elif token_type == 'FOR':
            return self.parse_for()
            
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

    def parse_for(self):
        """
        Parsea: for variable in range(...):
        """
        self.match('FOR')
        
        # Obtener la variable del bucle
        token_type, var_name, line = self.current()
        if token_type != 'ID':
            raise SyntaxError(f"Expected variable name after 'for', got {token_type} at line {line}")
        variable = NodeFactory.create('identifier', var_name)
        self.match('ID')
        
        # Consumir 'in'
        self.match('IN')
        
        # Parsear range(...)
        iterable = self.parse_range()
        
        # Consumir ':'
        self.match('COLON')
        self.match('INDENT')

        # Parsear el cuerpo
        body = []
        while self.current()[0] != 'DEDENT' and self.current()[0] != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        if self.current()[0] == 'DEDENT':
            self.match('DEDENT')
        
        return NodeFactory.create('for', variable, iterable, body)

    def parse_range(self):
        """
        Parsea: range(stop) o range(start, stop) o range(start, stop, step)
        """
        self.match('RANGE')
        self.match('LPAREN')
        
        # Primer argumento
        arg1 = self.parse_expression()
        
        # Si hay coma, hay más argumentos
        if self.current()[0] == 'COMMA':
            self.match('COMMA')
            arg2 = self.parse_expression()
            
            # Si hay otra coma, hay un tercer argumento (step)
            if self.current()[0] == 'COMMA':
                self.match('COMMA')
                arg3 = self.parse_expression()
                self.match('RPAREN')
                # range(start, stop, step)
                return NodeFactory.create('range', arg1, arg2, arg3)
            else:
                self.match('RPAREN')
                # range(start, stop)
                return NodeFactory.create('range', arg1, arg2)
        else:
            self.match('RPAREN')
            # range(stop) -> start=0, stop=arg1
            return NodeFactory.create('range', NodeFactory.create('number', '0'), arg1)

    def parse_function_def(self):
        """
        Parsea: def nombre(param1, param2, ...):
        """
        self.match('DEF')
        
        # Nombre de la función
        token_type, func_name, line = self.current()
        if token_type != 'ID':
            raise SyntaxError(f"Expected function name after 'def', got {token_type} at line {line}")
        self.match('ID')
        
        # Parámetros
        self.match('LPAREN')
        params = []
        
        if self.current()[0] != 'RPAREN':
            # Primer parámetro
            token_type, param_name, line = self.current()
            if token_type != 'ID':
                raise SyntaxError(f"Expected parameter name, got {token_type} at line {line}")
            params.append(NodeFactory.create('identifier', param_name))
            self.match('ID')
            
            # Parámetros adicionales
            while self.current()[0] == 'COMMA':
                self.match('COMMA')
                token_type, param_name, line = self.current()
                if token_type != 'ID':
                    raise SyntaxError(f"Expected parameter name, got {token_type} at line {line}")
                params.append(NodeFactory.create('identifier', param_name))
                self.match('ID')
        
        self.match('RPAREN')
        self.match('COLON')
        self.match('INDENT')
        
        # Cuerpo de la función
        body = []
        while self.current()[0] != 'DEDENT' and self.current()[0] != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        if self.current()[0] == 'DEDENT':
            self.match('DEDENT')
        
        return NodeFactory.create('function_def', func_name, params, body)

    def parse_return(self):
        """
        Parsea: return o return expresión
        """
        self.match('RETURN')
        
        # Si lo siguiente no es un fin de línea, parsear la expresión
        if self.current()[0] not in ('DEDENT', 'EOF', 'INDENT'):
            expr = self.parse_expression()
            return NodeFactory.create('return', expr)
        else:
            return NodeFactory.create('return', None)

    def parse_arguments(self):
        """
        Parsea argumentos de una llamada a función: (arg1, arg2, ...)
        """
        args = []
        
        if self.current()[0] != 'RPAREN':
            # Primer argumento
            args.append(self.parse_expression())
            
            # Argumentos adicionales
            while self.current()[0] == 'COMMA':
                self.match('COMMA')
                args.append(self.parse_expression())
        
        return args

    def parse_expression(self):
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
            name = value
            self.match('ID')
            # Verificar si es una llamada a función
            if self.current()[0] == 'LPAREN':
                self.match('LPAREN')
                args = self.parse_arguments()
                self.match('RPAREN')
                return NodeFactory.create('function_call', name, args)
            else:
                return NodeFactory.create('identifier', name)
        elif token_type == 'LPAREN':
            self.match('LPAREN')
            expr = self.parse_expression()
            self.match('RPAREN')
            return expr
        else:
            raise SyntaxError(f"Unexpected token {token_type}")
