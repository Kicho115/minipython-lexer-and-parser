# This import is fo
import re

# List of keywords and symbols
KEYWORDS = {'if': 'IF', 'while': 'WHILE', 'print': 'PRINT', 'True': 'TRUE', 'False': 'FALSE' , 'else' : 'ELSE'}
SYMBOLS = {
    '=': 'ASSIGN',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULT',
    '/': 'DIV',
    '==': 'EQ',
    '!=': 'NEQ',
    '>': 'GT',
    '<': 'LT',
    '>=': 'GTE',
    '<=': 'LTE',
    ':': 'COLON',
    '(': 'LPAREN',
    ')': 'RPAREN'
}

def lexer(code):
    tokens = []
    lines = code.split('\n')
    indent_stack = [0]

    
    for line_num, line in enumerate(lines, start=1):

        # Skip empty lines
        if not line.strip():
            continue

        # Ignore everything after a comment
        comment_index = line.find('#')
        if comment_index != -1:
            line = line[:comment_index]

        # Handle indentation
        indent = len(line) - len(line.lstrip(' '))
        
        # Add DEDENT tokens if current indent is less than previous
        while indent < indent_stack[-1]:
            tokens.append(('DEDENT', '', line_num))
            indent_stack.pop()
            
        # Add INDENT token if current indent is greater than previous
        if indent > indent_stack[-1]:
            tokens.append(('INDENT', '', line_num))
            indent_stack.append(indent)

        # Process the rest of the line
        line = line.strip()

        i = 0
        while i < len(line):
            c = line[i]

            # Ignore whitespace between tokens
            # Skip to the next line
            if c.isspace():
                i += 1
                continue

            # String literals
            if c == '"' or c == "'":
                quote = c
                start = i + 1
                i += 1
                while i < len(line) and line[i] != quote:
                    if line[i] == '\\' and i + 1 < len(line):
                        i += 2  # Skip escaped character
                    else:
                        i += 1
                if i >= len(line):
                    tokens.append(('ERROR', 'Unterminated string', line_num))
                    break
                tokens.append(('STRING', line[start:i], line_num))
                i += 1
                continue

            # Keywords, identifiers
            if c.isalpha():
                start = i
                while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                word = line[start:i]
                token_type = KEYWORDS.get(word, 'ID')
                tokens.append((token_type, word, line_num))
                continue

            # Numbers
            if c.isdigit():
                start = i
                while i < len(line) and line[i].isdigit():
                    i += 1
                tokens.append(('NUMBER', line[start:i], line_num))
                continue

            # 2-character operators (==, !=, >=, <=)
            if i + 1 < len(line) and line[i:i+2] in SYMBOLS:
                tokens.append((SYMBOLS[line[i:i+2]], line[i:i+2], line_num))
                i += 2
                continue

            # 1-character operators
            if c in SYMBOLS:
                tokens.append((SYMBOLS[c], c, line_num))
                i += 1
                continue

            # Unrecognized character
            tokens.append(('ERROR', c, line_num))
            i += 1
    
    # Add EOF token at the end
    tokens.append(('EOF', '', len(lines)))
    return tokens
