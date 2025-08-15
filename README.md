# minipython-lexer-and-parser

A simple lexical and syntax analyzer for a reduced version of Python (MiniPython), built for a Theory of Automata course. It checks code correctness and reports syntax errors without using external libraries.

## Live Demo

You can try the application online without running it locally: [https://minipython-lexer-and-parser-3gdn.vercel.app/](https://minipython-lexer-and-parser-3gdn.vercel.app/)

**Note:** The first time you use the compiler, it may take a moment to start up since we're using the free tier hosting.

## How to Run

This application requires two terminals - one for the frontend and one for the backend.

### Terminal 1 - Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Terminal 2 - Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app
```

The backend will be available at `http://localhost:8000`

Make sure both services are running before using the application.
