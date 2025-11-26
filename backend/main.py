from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from lexer import Lexer
from parser import Parser
import traceback
import re
from transpiler import Transpiler

app = FastAPI(
    title="Mini Python Compiler API",
    description="API for compiling and parsing Python-like code",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str

def format_error_message(error, code):
    # Extract the line number from the error message if it exists
    line_match = re.search(r'line (\d+)', str(error))
    line_number = int(line_match.group(1)) if line_match else None
    
    # Get the specific line of code
    code_lines = code.split('\n')
    error_line = code_lines[line_number - 1] if line_number and line_number <= len(code_lines) else None
    
    # Build the error message
    error_msg = f"Error in line {line_number}:\n" if line_number else "Error:\n"
    if error_line:
        error_msg += f"\n{error_line}\n"
        # Add a position indicator if it's a syntax error
        if "SyntaxError" in str(error):
            error_msg += " " * (len(error_line) - len(error_line.lstrip())) + "^\n"
    error_msg += f"\n{str(error)}"
    
    return error_msg

@app.post("/compile")
async def compile_code(input: CodeInput):
    try:
        # Use the lexer to tokenize the code
        tokens = Lexer(input.code)  # Returns tokens directly
        
        # Use the parser to analyze the tokens
        parser = Parser(tokens)
        ast = parser.parse()

        # Transpile AST to JavaScript
        transpiler = Transpiler(ast)
        js_code = transpiler.transpile()
        
        return {
            "output": str(ast),
            "tokens": [str(token) for token in tokens],
            "ast": ast.to_tree(),
            "js": js_code
        }
    except Exception as e:
        error_msg = format_error_message(e, input.code)
        print(error_msg)  # Print to server logs
        raise HTTPException(status_code=400, detail=error_msg)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Mini Python Compiler API",
        "docs": "/docs",
        "endpoints": {
            "/compile": "POST - Compile and parse Python-like code"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
