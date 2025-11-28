import Head from "next/head";
import { Geist, Geist_Mono } from "next/font/google";
import dynamic from "next/dynamic";
import { useState } from "react";
import styles from "@/styles/Home.module.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
});

export default function Home() {
  const [code, setCode] = useState("# Write your code here...");
  const [tokens, setTokens] = useState<string[]>([]);
  const [ast, setAst] = useState<string>("");
  const [jsCode, setJsCode] = useState<string>("");
  const [executionOutput, setExecutionOutput] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setCode(value);
    }
  };

  const executeJavaScript = (code: string) => {
    try {
      // Capturar console.log
      const logs: string[] = [];
      const originalLog = console.log;

      console.log = (...args: any[]) => {
        logs.push(args.map((arg) => String(arg)).join(" "));
      };

      // Ejecutar código
      // eslint-disable-next-line no-eval
      const result = eval(code);

      // Restaurar console.log
      console.log = originalLog;

      if (logs.length > 0) {
        setExecutionOutput(logs.join("\n"));
      } else if (result !== undefined) {
        setExecutionOutput(String(result));
      } else {
        setExecutionOutput("✓ Execution completed successfully (no output)");
      }
    } catch (error) {
      setExecutionOutput(`❌ Error: ${error}`);
    }
  };

  const handleCompile = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        process.env.NEXT_PUBLIC_API_URL + "/compile",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ code }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        setExecutionOutput(errorData.detail || "Error: Could not compile code");
        setTokens([]);
        setAst("");
        setJsCode("");
        return;
      }

      const data = await response.json();

      // Actualizar estados
      setTokens(data.tokens || []);
      setAst(data.ast || "No AST generated");
      setJsCode(data.javascript || data.js || "No JavaScript generated");

      // Ejecutar automáticamente el código JavaScript
      if (data.javascript || data.js) {
        executeJavaScript(data.javascript || data.js);
      }
    } catch (error) {
      console.error("Error:", error);
      setExecutionOutput("Error: Could not connect to the compiler server");
      setTokens([]);
      setAst("");
      setJsCode("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Mini Python Compiler</title>
        <meta
          name="description"
          content="A mini Python compiler with lexer and parser"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div
        className={`${styles.page} ${geistSans.variable} ${geistMono.variable}`}
      >
        <main className={styles.main}>
          <h1 className={styles.title}>🐍 Intérprete Web Python a JavaScript</h1>

          {/* Editor de Python - Arriba */}
          <div className={styles.editorSection}>
            <div className={styles.sectionHeader}>
              <span className={styles.headerIcon}></span>
              Python Code
            </div>
            <div className={styles.editorWrapper}>
              <MonacoEditor
                defaultLanguage="python"
                theme="vs-dark"
                value={code}
                onChange={handleEditorChange}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: "on",
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </div>
          </div>

          {/* Secciones de output - Abajo en grid de 3 columnas */}
          <div className={styles.outputGrid}>
            {/* Tokens */}
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <span className={styles.headerIcon}></span>
                Tokens
              </div>
              <pre className={styles.sectionContent}>
                {tokens.length > 0
                  ? tokens.join("\n")
                  : "No tokens generados aún..."}
              </pre>
            </div>

            {/* AST */}
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <span className={styles.headerIcon}></span>
                AST (Abstract Syntax Tree)
              </div>
              <pre className={styles.sectionContent}>
                {ast || "No AST generado aún..."}
              </pre>
            </div>

            {/* JavaScript Code */}
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <span className={styles.headerIcon}></span>
                JavaScript Code
              </div>
              <pre className={styles.sectionContent}>
                {jsCode || "No código JavaScript generado aún..."}
              </pre>
            </div>
          </div>

          {/* Botón Compile & Run */}
          <button
            className={styles.compileButton}
            onClick={handleCompile}
            disabled={isLoading}
          >
            {isLoading ? "Compilando..." : "Compilar y Ejecutar"}
          </button>

          {/* Output de Ejecución */}
          <div className={styles.executionSection}>
            <div className={styles.sectionHeader}>
              <span className={styles.headerIcon}></span>
              Resultado de la Ejecución
            </div>
            <pre className={styles.executionOutput}>
              {executionOutput || "Click 'Compilar y Ejecutar' para ver el resultado..."}
            </pre>
          </div>
        </main>
      </div>
    </>
  );
}
