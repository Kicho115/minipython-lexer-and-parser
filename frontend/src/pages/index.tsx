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
const MonacoEditor = dynamic(
  () => import("@monaco-editor/react"),
  { ssr: false }
);

export default function Home() {
  const [code, setCode] = useState("# Write your code here...");
  const [output, setOutput] = useState("");

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setCode(value);
    }
  };

  const handleCompile = async () => {
    try {
      const response = await fetch("http://localhost:8000/compile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        setOutput(errorData.detail || "Error: Could not compile code");
        return;
      }

      const data = await response.json();
      
      // Formatear la salida para mostrar tokens y AST
      const output = `=== Tokens ===\n${data.tokens.join('\n')}\n\n=== AST ===\n${data.ast}`;
      setOutput(output);
    } catch (error) {
      setOutput("Error: Could not connect to the compiler server");
    }
  };

  return (
    <>
      <Head>
        <title>Mini Python Compiler</title>
        <meta name="description" content="A mini Python compiler with lexer and parser" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={`${styles.page} ${geistSans.variable} ${geistMono.variable}`}>
        <main className={styles.main}>
          <h1 className={styles.title}>Mini Python Compiler</h1>
          <div className={styles.editorContainer}>
            <div className={styles.editorWrapper}>
              <div className={styles.inputHeader}>Input</div>
              <MonacoEditor
                defaultLanguage="python"
                theme="vs-dark"
                value={code}
                onChange={handleEditorChange}
                options={{
                  minimap: { enabled: true },
                  fontSize: 14,
                  lineNumbers: "on",
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </div>
            <div className={styles.outputWrapper}>
              <div className={styles.outputHeader}>Output</div>
              <pre className={styles.output}>{output}</pre>
            </div>
          </div>
          <button className={styles.compileButton} onClick={handleCompile}>
            Compile & Run
          </button>
        </main>
      </div>
    </>
  );
}
