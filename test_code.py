from lexer import lexer
from parser import Parser
from node_factory import NodeFactory

def test_minipython_code(code):
    print("=== Testing MiniPython Code ===")
    print("Input code:")
    print(code)
    print("\n=== Lexer Output ===")
    
    # Tokenize the code
    tokens = lexer(code)
    for token in tokens:
        print(f"Token: {token}")
    
    print("\n=== Parser Output ===")
    # Parse the tokens
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print("AST created successfully!")
        return ast
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return None

# Example MiniPython code to test
test_code = """
x = 10
y = "Hello World"
if x > 5:
    print(y)
    while x > 0:
        x = x - 1
        print(x)
else:
  print("x is too small")
"""

if __name__ == "__main__":
    # You can modify test_code here to try different examples
    ast = test_minipython_code(test_code) 