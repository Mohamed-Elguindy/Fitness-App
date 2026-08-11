"use client";

import Link from "next/link";
import { SignInButton, UserButton, useAuth } from "@clerk/nextjs";

export default function Home() {
  const { isLoaded, userId } = useAuth();

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white selection:bg-orange-500/30">
      {/* Navbar */}
      <nav className="flex items-center justify-between p-6 max-w-7xl mx-auto border-b border-white/10">
        <div className="text-2xl font-bold tracking-tighter flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-orange-500 to-orange-700 flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>
          </div>
          AGENTIC<span className="text-orange-500">FIT</span>
        </div>
        
        <div className="flex gap-4 items-center">
          {isLoaded && !userId && (
            <>
              <SignInButton mode="modal">
                <button className="px-5 py-2 rounded-md font-medium transition-all hover:bg-white/10">Log in</button>
              </SignInButton>
              <SignInButton mode="modal">
                <button className="px-5 py-2 rounded-md font-medium bg-orange-600 hover:bg-orange-500 transition-all text-white shadow-[0_0_20px_rgba(2ea44f,0.4)] shadow-orange-500/20">
                  Get Started
                </button>
              </SignInButton>
            </>
          )}
          {isLoaded && userId && (
            <>
              <Link href="/dashboard" className="px-5 py-2 rounded-md font-medium bg-orange-600 hover:bg-orange-500 transition-all text-white shadow-lg shadow-orange-500/20 mr-4">
                Go to Dashboard
              </Link>
              <UserButton afterSignOutUrl="/" appearance={{ elements: { avatarBox: "w-10 h-10 border-2 border-orange-500/50" } }} />
            </>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-24 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 text-orange-500 border border-orange-500/20 text-sm font-medium mb-8">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
          </span>
          Agent Core v1.0 is Online
        </div>
        
        <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-6 leading-tight">
          Your Personal <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-orange-400 to-orange-600">
            Sports Scientist.
          </span>
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mb-12 leading-relaxed">
          Stop guessing. Our AI Agent streams real-time reasoning to build perfect hypertrophy programs and diet splits tailored to your anatomy and goals.
        </p>
        
        {isLoaded && !userId && (
          <SignInButton mode="modal">
            <button className="px-8 py-4 rounded-xl font-bold text-lg bg-white text-black hover:bg-gray-200 transition-all flex items-center gap-2">
              Generate Your Program
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
            </button>
          </SignInButton>
        )}
        
        {isLoaded && userId && (
          <Link href="/dashboard" className="px-8 py-4 rounded-xl font-bold text-lg bg-white text-black hover:bg-gray-200 transition-all flex items-center gap-2">
            Enter Dashboard
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
          </Link>
        )}

        {/* Glassmorphism Preview */}
        <div className="mt-24 w-full max-w-5xl rounded-2xl border border-white/10 bg-white/[0.02] backdrop-blur-3xl p-2 shadow-2xl overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-b from-orange-500/10 to-transparent pointer-events-none"></div>
          <img src="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=3270&auto=format&fit=crop" alt="Gym" className="w-full h-96 object-cover rounded-xl opacity-50" />
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
             <div className="p-6 rounded-xl bg-black/60 backdrop-blur-md border border-white/10 font-mono text-left text-sm text-green-400 shadow-2xl">
                <p>{">"} initializing coach core...</p>
                <p>{">"} calculating metabolic rate (TDEE)...</p>
                <p>{">"} querying sports science literature...</p>
                <p>{">"} generating macro split...</p>
                <p className="animate-pulse">_</p>
             </div>
          </div>
        </div>
      </main>
    </div>
  );
}
