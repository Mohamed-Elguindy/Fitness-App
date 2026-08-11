"use client";

import { useEffect, useState, useRef } from "react";

interface AgentTerminalProps {
  streamUrl: string;
  requestBody: any;
  onComplete: (data: any) => void;
  token?: string | null;
}

export default function AgentTerminal({ streamUrl, requestBody, onComplete, token }: AgentTerminalProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [isDone, setIsDone] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // We cannot easily send POST body or Authorization header with native EventSource.
    // So we use fetch to stream the response manually.
    let abortController = new AbortController();

    const startStreaming = async () => {
      try {
        setLogs(["> connecting to AgenticFit core..."]);
        
        const response = await fetch(streamUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { "Authorization": `Bearer ${token}` } : {})
          },
          body: JSON.stringify(requestBody),
          signal: abortController.signal
        });

        if (!response.ok) {
          setLogs(prev => [...prev, `> ERROR: Server returned ${response.status}`]);
          setIsDone(true);
          return;
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        
        if (!reader) return;

        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          
          // Split by SSE double newline
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || ""; // Keep the incomplete chunk in the buffer
          
          for (const part of parts) {
            if (part.startsWith("data: ")) {
              const dataStr = part.slice(6);
              try {
                const data = JSON.parse(dataStr);
                
                if (data.status) {
                  setLogs(prev => [...prev, `> ${data.status}`]);
                }
                
                if (data.result) {
                  setLogs(prev => [...prev, `> Generation complete! Parsing payload...`]);
                  setIsDone(true);
                  onComplete(data.result);
                }
              } catch (e) {
                console.error("Failed to parse SSE JSON:", e, dataStr);
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name === "AbortError") {
          console.log("Stream aborted");
        } else {
          setLogs(prev => [...prev, `> CONNECTION ERROR: ${err.message}`]);
          setIsDone(true);
        }
      }
    };

    startStreaming();

    return () => {
      abortController.abort();
    };
  }, [streamUrl]);

  useEffect(() => {
    // Auto scroll to bottom
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  return (
    <div className="w-full max-w-4xl mx-auto rounded-xl border border-white/10 bg-black/60 backdrop-blur-xl shadow-2xl overflow-hidden mt-8">
      <div className="flex items-center gap-2 px-4 py-3 bg-white/5 border-b border-white/10">
        <div className="w-3 h-3 rounded-full bg-red-500"></div>
        <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
        <div className="w-3 h-3 rounded-full bg-green-500"></div>
        <span className="ml-2 text-xs font-mono text-gray-400">agent-core-tty1</span>
      </div>
      <div className="p-6 font-mono text-sm h-64 overflow-y-auto">
        {logs.map((log, i) => (
          <div key={i} className={`${log.includes("ERROR") ? "text-red-400" : log.includes("complete") ? "text-orange-400" : "text-green-400"} mb-1`}>
            {log}
          </div>
        ))}
        {!isDone && (
          <div className="text-green-400 animate-pulse mt-2">_</div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
