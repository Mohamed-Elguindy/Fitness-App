"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, MessageSquare, Send, Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function AskCoach() {
  const { isLoaded, userId } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && !userId) {
      router.push("/");
    }
  }, [isLoaded, userId, router]);

  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<{role: "user" | "coach", content: string}[]>([
    { role: "coach", content: "Hello! I am your Agentic AI Coach. How can I help you adjust your training program or diet today?" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMessage = query.trim();
    setQuery("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/coach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: userMessage,
          user_context: "User wants to optimize their plan."
        })
      });

      const data = await response.json();
      setMessages(prev => [...prev, { role: "coach", content: data.response }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: "coach", content: "⚠️ Could not connect to the backend. Make sure the FastAPI server is running on port 8000." }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isLoaded || !userId) return null;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col">
      <nav className="p-6 border-b border-white/10 max-w-7xl mx-auto w-full flex items-center justify-between shrink-0">
        <Link href="/dashboard" className="flex items-center text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Dashboard
        </Link>
        <div className="text-xl font-bold flex items-center gap-2">
          <MessageSquare className="text-blue-500 w-6 h-6" />
          Agentic Coach
        </div>
      </nav>

      <main className="max-w-4xl mx-auto p-6 w-full flex-1 flex flex-col mt-4 min-h-0">
        <div className="flex-1 overflow-y-auto space-y-6 pr-4 mb-6 custom-scrollbar">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'coach' && (
                <div className="w-10 h-10 rounded-full bg-blue-500/20 text-blue-500 flex items-center justify-center shrink-0">
                  <Bot className="w-6 h-6" />
                </div>
              )}
              
              <div className={`max-w-[80%] rounded-2xl p-5 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-sm' 
                  : 'bg-white/[0.04] border border-white/10 text-gray-300 rounded-tl-sm'
              }`}>
                {msg.role === 'user' ? (
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                ) : (
                  <div className="prose prose-invert prose-sm md:prose-base prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10 prose-headings:text-white max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-10 h-10 rounded-full bg-white/10 text-white flex items-center justify-center shrink-0">
                  <User className="w-6 h-6" />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4 justify-start">
              <div className="w-10 h-10 rounded-full bg-blue-500/20 text-blue-500 flex items-center justify-center shrink-0">
                <Bot className="w-6 h-6" />
              </div>
              <div className="bg-white/[0.04] border border-white/10 text-gray-300 rounded-2xl rounded-tl-sm p-5 flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="shrink-0 relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about exercises, macros, or adjusting your plan..."
            className="w-full bg-white/5 border border-white/10 rounded-2xl p-5 pr-16 outline-none focus:border-blue-500 transition-colors text-white placeholder:text-gray-500"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={!query.trim() || isLoading}
            className="absolute right-3 top-3 bottom-3 aspect-square flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors text-white"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </main>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  );
}
