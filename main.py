from lexer import lexer
from parser import Parser
from node_factory import NodeFactory

def main():
    filename = "tester.py"

    with open(filename, "r") as f:
        code = f.read()

    print("=== Testing MiniPython Code ===")
    print("Input code:")
    print(code)
    print("\n=== Lexer Output ===")
    
    # Tokenize the code
    tokens = lexer(code)
    for token in tokens:
        print(f"Token: {token}")
    
    # Parse the tokens
    print("\n=== Parser Output ===")
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print("AST created successfully!")
        return ast
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return None

if __name__ == "__main__":
    main()