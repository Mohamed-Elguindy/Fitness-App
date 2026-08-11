"use client";

import { useAuth, UserButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Info, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const { isLoaded, userId, getToken } = useAuth();
  const router = useRouter();
  const [history, setHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState<any | null>(null);

  useEffect(() => {
    if (isLoaded && !userId) {
      router.push("/");
    } else if (isLoaded && userId) {
      const fetchHistory = async () => {
        try {
          const token = await getToken();
          const res = await fetch("http://localhost:8000/history", {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (res.ok) {
            const data = await res.json();
            setHistory(data.history);
          }
        } catch (e) {
          console.error("Failed to fetch history:", e);
        } finally {
          setLoadingHistory(false);
        }
      };
      fetchHistory();
    }
  }, [isLoaded, userId, router, getToken]);

  if (!isLoaded || !userId) {
    return <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center text-white">Authenticating...</div>;
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Navbar */}
      <nav className="flex items-center justify-between p-6 max-w-7xl mx-auto border-b border-white/10">
        <Link href="/" className="text-2xl font-bold tracking-tighter flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-orange-500 to-orange-700 flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>
          </div>
          AGENTIC<span className="text-orange-500">FIT</span>
        </Link>
        <div className="flex gap-4 items-center">
          <UserButton afterSignOutUrl="/" appearance={{ elements: { avatarBox: "w-10 h-10 border-2 border-orange-500/50" } }} />
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6 mt-8">
        <header className="mb-12">
          <h1 className="text-4xl font-bold mb-2">Welcome Back</h1>
          <p className="text-gray-400">Ready to build your ultimate physics engine?</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Training Card */}
          <Link href="/generate/training" className="group relative rounded-2xl border border-white/10 bg-white/[0.02] p-8 overflow-hidden hover:bg-white/[0.04] transition-all cursor-pointer">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="w-12 h-12 bg-orange-500/20 text-orange-500 rounded-xl flex items-center justify-center mb-6">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 18h12"></path><path d="M6 14h12"></path><rect width="18" height="20" x="3" y="2" rx="2"></rect></svg>
            </div>
            <h2 className="text-2xl font-bold mb-2">Generate Program</h2>
            <p className="text-gray-400 mb-6 text-sm">Spin up a highly-optimized hypertrophy block using real-time AI.</p>
            <div className="flex items-center text-orange-500 font-medium text-sm">
              Start Generation <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
            </div>
          </Link>

          {/* Diet Card */}
          <Link href="/generate/diet" className="group relative rounded-2xl border border-white/10 bg-white/[0.02] p-8 overflow-hidden hover:bg-white/[0.04] transition-all cursor-pointer">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="w-12 h-12 bg-green-500/20 text-green-500 rounded-xl flex items-center justify-center mb-6">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
            </div>
            <h2 className="text-2xl font-bold mb-2">Generate Diet</h2>
            <p className="text-gray-400 mb-6 text-sm">Calculate TDEE, macros, and get a tailored meal plan generated by AI.</p>
            <div className="flex items-center text-green-500 font-medium text-sm">
              Start Generation <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
            </div>
          </Link>

          {/* Ask Coach Card */}
          <Link href="/ask-coach" className="group relative rounded-2xl border border-white/10 bg-white/[0.02] p-8 overflow-hidden hover:bg-white/[0.04] transition-all cursor-pointer">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="w-12 h-12 bg-blue-500/20 text-blue-500 rounded-xl flex items-center justify-center mb-6">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            </div>
            <h2 className="text-2xl font-bold mb-2">Ask Coach</h2>
            <p className="text-gray-400 mb-6 text-sm">Chat with the Agentic AI to tweak your plans or ask sports science questions.</p>
            <div className="flex items-center text-blue-500 font-medium text-sm">
              Open Chat <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
            </div>
          </Link>
        </div>

        {/* Previous Generations Section */}
        <div className="mt-16">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            Recent Generations
          </h3>
          {loadingHistory ? (
            <div className="rounded-xl border border-white/10 bg-white/[0.01] p-12 text-center text-gray-500">
              Loading history...
            </div>
          ) : history.length === 0 ? (
            <div className="rounded-xl border border-white/10 bg-white/[0.01] p-12 text-center text-gray-500">
              No active programs yet. Generate your first plan above.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {history.map((item, i) => (
                <div key={i} className="rounded-xl border border-white/10 bg-white/[0.02] p-6 flex flex-col gap-2 relative group overflow-hidden">
                  <div className={`absolute top-0 left-0 w-1 h-full ${item.type === 'diet' ? 'bg-green-500' : 'bg-orange-500'}`}></div>
                  <div className="flex justify-between items-center mb-2">
                    <span className={`text-xs font-bold uppercase tracking-wider ${item.type === 'diet' ? 'text-green-500' : 'text-orange-500'}`}>
                      {item.type} Plan
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {item.type === 'diet' ? (
                    <>
                      <h4 className="font-bold text-lg mb-1">{item.data?.macros?.goal?.toUpperCase() || 'DIET PLAN'}</h4>
                      <div className="text-sm text-gray-400">
                        {item.data?.meal_plan?.daily_calories} kcal • {item.data?.meal_plan?.daily_protein}g Protein
                      </div>
                    </>
                  ) : (
                    <>
                      <h4 className="font-bold text-lg mb-1">{item.data?.program?.goal?.toUpperCase() || 'TRAINING PROGRAM'}</h4>
                      <div className="text-sm text-gray-400">
                        {item.data?.program?.sessions?.length || 0} Days/Week
                      </div>
                    </>
                  )}
                  <button 
                    onClick={() => setSelectedPlan(item)}
                    className="mt-4 px-4 py-2 bg-white/5 hover:bg-white/10 rounded border border-white/10 transition-colors text-sm font-medium w-full text-center">
                    View Details
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* MODAL */}
      {selectedPlan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#111] border border-white/10 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="sticky top-0 bg-[#111]/90 backdrop-blur border-b border-white/10 p-4 flex justify-between items-center z-10">
              <h2 className="text-xl font-bold uppercase tracking-widest text-white">
                {selectedPlan.type === 'diet' ? 'Diet Plan Details' : 'Training Program Details'}
              </h2>
              <button 
                onClick={() => setSelectedPlan(null)}
                className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6">
              {selectedPlan.type === 'diet' ? (
                <>
                  <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6 mb-8 flex items-start gap-4">
                    <Info className="w-6 h-6 text-green-500 shrink-0 mt-1" />
                    <div className="w-full">
                      <div className="flex justify-between items-center mb-1">
                        <h3 className="text-lg font-bold text-green-500">Target Macros</h3>
                        <div className="text-sm font-mono text-gray-400">Base TDEE: {selectedPlan.data.tdee} kcal</div>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                          <div className="text-xs text-blue-400 uppercase tracking-wider mb-1">Protein</div>
                          <div className="text-xl font-bold">{selectedPlan.data.meal_plan.daily_protein}g</div>
                        </div>
                        <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                          <div className="text-xs text-yellow-400 uppercase tracking-wider mb-1">Carbs</div>
                          <div className="text-xl font-bold">{selectedPlan.data.meal_plan.daily_carbs}g</div>
                        </div>
                        <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                          <div className="text-xs text-red-400 uppercase tracking-wider mb-1">Fat</div>
                          <div className="text-xl font-bold">{selectedPlan.data.meal_plan.daily_fat}g</div>
                        </div>
                        <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                          <div className="text-xs text-green-400 uppercase tracking-wider mb-1">Calories</div>
                          <div className="text-xl font-bold">{selectedPlan.data.meal_plan.daily_calories}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {selectedPlan.data.meal_plan.meals.map((meal: any, idx: number) => (
                      <div key={idx} className="bg-white/[0.02] border border-white/10 rounded-2xl p-6">
                        <div className="flex justify-between items-start mb-4 border-b border-white/10 pb-4">
                          <div>
                            <div className="text-xs text-green-500 font-mono mb-1">{meal.meal_time}</div>
                            <h3 className="text-xl font-bold capitalize">{meal.meal_name.replace(/_/g, ' ')}</h3>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold">{meal.total_calories} <span className="text-sm font-normal text-gray-500">kcal</span></div>
                          </div>
                        </div>
                        
                        <div className="mb-4">
                          <ul className="space-y-2">
                            {meal.foods.map((food: any, fIdx: number) => (
                              <li key={fIdx} className="flex justify-between text-sm">
                                <span className="text-gray-300">{food.food_name}</span>
                                <span className="text-gray-500 font-mono">{food.grams}g</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div className="flex justify-between text-xs font-mono bg-black/40 p-2 rounded border border-white/5">
                          <span className="text-blue-400">P: {meal.total_protein}g</span>
                          <span className="text-yellow-400">C: {meal.total_carbs}g</span>
                          <span className="text-red-400">F: {meal.total_fat}g</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-6 mb-8 flex items-start gap-4">
                    <Info className="w-6 h-6 text-orange-500 shrink-0 mt-1" />
                    <div className="w-full">
                      <div className="flex justify-between items-center mb-1">
                        <h3 className="text-lg font-bold text-orange-500">TRAINING PROGRAM</h3>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                          <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Sets / Exercise</div>
                          <div className="text-xl font-bold">{selectedPlan.data.volume_settings.sets_per_exercise}</div>
                        </div>
                        <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                          <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Rep Range</div>
                          <div className="text-xl font-bold">{selectedPlan.data.volume_settings.rep_range}</div>
                        </div>
                        <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                          <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Exercises / Session</div>
                          <div className="text-xl font-bold">{selectedPlan.data.volume_settings.exercises_per_session}</div>
                        </div>
                        <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                          <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Rest Time</div>
                          <div className="text-xl font-bold">{selectedPlan.data.volume_settings.rest_between_sets_seconds}s</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-8">
                    {selectedPlan.data.program.sessions.map((session: any, idx: number) => (
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
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
