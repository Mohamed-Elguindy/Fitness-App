"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Dumbbell, Clock, Calendar, Activity, Info } from "lucide-react";
import AgentTerminal from "@/components/AgentTerminal";

export default function TrainingGenerator() {
  const { isLoaded, userId, getToken } = useAuth();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    if (isLoaded && !userId) {
      router.push("/");
    } else if (isLoaded && userId) {
      getToken().then(setToken);
    }
  }, [isLoaded, userId, router, getToken]);

  const [step, setStep] = useState<"form" | "generating" | "result">("form");
  const [formData, setFormData] = useState({
    goal: "hypertrophy",
    experience_level: "intermediate",
    days_per_week: 4,
    available_minutes: 60,
    equipment: "full gym",
    injuries: "none"
  });
  
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStep("generating");
  };

  const handleComplete = (data: any) => {
    setResult(data);
    setStep("result");
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <nav className="p-6 border-b border-white/10 max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Dashboard
        </Link>
        <div className="text-xl font-bold flex items-center gap-2">
          <Dumbbell className="text-orange-500 w-6 h-6" />
          Training Generator
        </div>
      </nav>

      <main className="max-w-4xl mx-auto p-6 mt-8">
        {step === "form" && (
          <form onSubmit={handleSubmit} className="space-y-8 bg-white/[0.02] border border-white/10 rounded-2xl p-8">
            <div>
              <h2 className="text-2xl font-bold mb-2">Configure Parameters</h2>
              <p className="text-gray-400 text-sm">Our AI will use these parameters to build a scientifically optimal volume matrix before selecting exercises.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Activity className="w-4 h-4 text-orange-500" />
                  Primary Goal
                </label>
                <select 
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-orange-500 transition-colors"
                  value={formData.goal}
                  onChange={e => setFormData({...formData, goal: e.target.value})}
                >
                  <option value="hypertrophy">Hypertrophy (Muscle Growth)</option>
                  <option value="strength">Maximum Strength</option>
                  <option value="endurance">Muscular Endurance</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-orange-500" />
                  Training Days Per Week
                </label>
                <input 
                  type="number" 
                  min="2" max="6"
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-orange-500 transition-colors"
                  value={formData.days_per_week}
                  onChange={e => setFormData({...formData, days_per_week: parseInt(e.target.value)})}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Clock className="w-4 h-4 text-orange-500" />
                  Available Minutes Per Session
                </label>
                <input 
                  type="number" 
                  min="30" max="120" step="15"
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-orange-500 transition-colors"
                  value={formData.available_minutes}
                  onChange={e => setFormData({...formData, available_minutes: parseInt(e.target.value)})}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Info className="w-4 h-4 text-orange-500" />
                  Existing Injuries / Limitations
                </label>
                <input 
                  type="text" 
                  placeholder="e.g. lower back pain, bad left knee"
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-orange-500 transition-colors"
                  value={formData.injuries}
                  onChange={e => setFormData({...formData, injuries: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Dumbbell className="w-4 h-4 text-orange-500" />
                  Available Equipment
                </label>
                <select 
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-orange-500 transition-colors"
                  value={formData.equipment}
                  onChange={e => setFormData({...formData, equipment: e.target.value})}
                >
                  <option value="full gym">Full Gym (Machines, Cables, Free Weights)</option>
                  <option value="barbell and dumbbell">Barbell & Dumbbells</option>
                  <option value="dumbbell only">Dumbbells Only</option>
                  <option value="kettlebell only">Kettlebells Only</option>
                  <option value="bodyweight">Bodyweight Only (No Equipment)</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Activity className="w-4 h-4 text-orange-500" />
                  Experience Level
                </label>
                <select 
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-orange-500 transition-colors"
                  value={formData.experience_level}
                  onChange={e => setFormData({...formData, experience_level: e.target.value})}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
            </div>

            <button type="submit" className="w-full py-4 rounded-xl font-bold bg-orange-600 hover:bg-orange-500 transition-all text-white shadow-[0_0_20px_rgba(234,88,12,0.4)] shadow-orange-500/20 text-lg">
              Initialize AI Generation
            </button>
          </form>
        )}

        {step === "generating" && (
          <div className="mt-12 text-center animate-in fade-in zoom-in duration-500">
            <h2 className="text-3xl font-bold mb-4">Synthesizing Program</h2>
            <p className="text-gray-400 mb-8">Agent is consulting the literature and building your volume parameters.</p>
            <AgentTerminal 
              streamUrl="http://localhost:8000/stream-training-program"
              requestBody={formData}
              onComplete={handleComplete}
              token={token}
            />
          </div>
        )}

        {step === "result" && result && (
          <div className="animate-in slide-in-from-bottom-8 duration-700">
            <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-6 mb-8 flex items-start gap-4">
              <Info className="w-6 h-6 text-orange-500 shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-bold text-orange-500 mb-1">Optimal Volume Architecture</h3>
                <p className="text-gray-300 text-sm mb-4">Based on your {formData.available_minutes} minute timeframe and {formData.goal} goal, the AI has calculated the mathematically optimal volume targets.</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Sets / Exercise</div>
                    <div className="text-xl font-bold">{result.volume_settings.sets_per_exercise}</div>
                  </div>
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Rep Range</div>
                    <div className="text-xl font-bold">{result.volume_settings.rep_range}</div>
                  </div>
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Exercises / Session</div>
                    <div className="text-xl font-bold">{result.volume_settings.exercises_per_session}</div>
                  </div>
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Rest Time</div>
                    <div className="text-xl font-bold">{result.volume_settings.rest_between_sets_seconds}s</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-8">
              {result.program.sessions.map((session: any, idx: number) => (
                <div key={idx} className="bg-white/[0.02] border border-white/10 rounded-2xl overflow-hidden">
                  <div className="bg-white/5 px-6 py-4 border-b border-white/10 flex justify-between items-center">
                    <h3 className="text-xl font-bold">Day {idx + 1}: <span className="text-orange-500">{session.day_name}</span></h3>
                    <div className="flex gap-2 text-xs font-mono text-gray-500">
                      {session.focus_muscles.map((m: string) => (
                        <span key={m} className="px-2 py-1 rounded bg-black/40 border border-white/10">{m}</span>
                      ))}
                    </div>
                  </div>
                  <div className="p-6">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-white/10">
                          <th className="pb-3 font-medium">Exercise</th>
                          <th className="pb-3 font-medium">Sets × Reps</th>
                          <th className="pb-3 font-medium">AI Coaching Note</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {session.exercises.map((ex: any, eIdx: number) => (
                          <tr key={eIdx}>
                            <td className="py-4 pr-4 font-medium text-white">{ex.exercise_name}</td>
                            <td className="py-4 pr-4 text-orange-400 font-mono whitespace-nowrap">{ex.sets} × {ex.reps}</td>
                            <td className="py-4 text-sm text-gray-400 leading-relaxed italic border-l border-white/5 pl-4">{ex.notes}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>

            <button 
              onClick={() => setStep("form")}
              className="mt-12 w-full py-4 rounded-xl font-bold border border-white/20 hover:bg-white/5 transition-all text-white text-lg"
            >
              Generate Another Plan
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
