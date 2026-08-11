"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Utensils, Activity, User, Scale, ActivitySquare, Info } from "lucide-react";
import AgentTerminal from "@/components/AgentTerminal";

export default function DietGenerator() {
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
    age: 25,
    weight_kg: 80,
    height_cm: 180,
    gender: "male",
    activity_level: "moderate",
    goal: "hypertrophy",
    intensity: "moderate",
    meals_per_day: 4,
    budget: "medium",
    allergies: "none"
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
          <Utensils className="text-green-500 w-6 h-6" />
          Nutrition Generator
        </div>
      </nav>

      <main className="max-w-4xl mx-auto p-6 mt-8">
        {step === "form" && (
          <form onSubmit={handleSubmit} className="space-y-8 bg-white/[0.02] border border-white/10 rounded-2xl p-8">
            <div>
              <h2 className="text-2xl font-bold mb-2">Configure Biometrics</h2>
              <p className="text-gray-400 text-sm">Our AI will calculate your precise TDEE and build a macro matrix before generating meals.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <User className="w-4 h-4 text-green-500" />
                  Age & Gender
                </label>
                <div className="flex gap-2">
                  <input 
                    type="number" 
                    min="14" max="100"
                    placeholder="Age"
                    className="w-1/2 bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                    value={formData.age}
                    onChange={e => setFormData({...formData, age: parseInt(e.target.value)})}
                  />
                  <select 
                    className="w-1/2 bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                    value={formData.gender}
                    onChange={e => setFormData({...formData, gender: e.target.value})}
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Scale className="w-4 h-4 text-green-500" />
                  Weight (kg) & Height (cm)
                </label>
                <div className="flex gap-2">
                  <input 
                    type="number" 
                    min="40" max="200"
                    placeholder="Weight"
                    className="w-1/2 bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                    value={formData.weight_kg}
                    onChange={e => setFormData({...formData, weight_kg: parseInt(e.target.value)})}
                  />
                  <input 
                    type="number" 
                    min="140" max="250"
                    placeholder="Height"
                    className="w-1/2 bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                    value={formData.height_cm}
                    onChange={e => setFormData({...formData, height_cm: parseInt(e.target.value)})}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Activity className="w-4 h-4 text-green-500" />
                  Primary Goal
                </label>
                <select 
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                  value={formData.goal}
                  onChange={e => setFormData({...formData, goal: e.target.value})}
                >
                  <option value="hypertrophy">Muscle Gain (Surplus)</option>
                  <option value="fat_loss">Fat Loss (Deficit)</option>
                  <option value="maintenance">Maintenance</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <ActivitySquare className="w-4 h-4 text-green-500" />
                  Activity Level
                </label>
                <select 
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                  value={formData.activity_level}
                  onChange={e => setFormData({...formData, activity_level: e.target.value})}
                >
                  <option value="sedentary">Sedentary (Little to no exercise)</option>
                  <option value="light">Light (1-3 days/week)</option>
                  <option value="moderate">Moderate (3-5 days/week)</option>
                  <option value="heavy">Heavy (6-7 days/week)</option>
                  <option value="athlete">Athlete (2x training/day)</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <ActivitySquare className="w-4 h-4 text-green-500" />
                  Goal Intensity
                </label>
                <select 
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                  value={formData.intensity}
                  onChange={e => setFormData({...formData, intensity: e.target.value})}
                >
                  <option value="lean">Lean / Slight (e.g. 250 kcal surplus/deficit)</option>
                  <option value="moderate">Moderate (e.g. 500 kcal surplus/deficit)</option>
                  <option value="aggressive">Aggressive (e.g. 750-1000 kcal surplus/deficit)</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Utensils className="w-4 h-4 text-green-500" />
                  Meal Budget
                </label>
                <select 
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                  value={formData.budget}
                  onChange={e => setFormData({...formData, budget: e.target.value})}
                >
                  <option value="low">Low Budget</option>
                  <option value="medium">Medium Budget</option>
                  <option value="high">High Budget</option>
                </select>
              </div>

              <div className="space-y-2 col-span-1 md:col-span-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Utensils className="w-4 h-4 text-green-500" />
                  Allergies / Dietary Restrictions
                </label>
                <input 
                  type="text" 
                  placeholder="e.g. Peanut allergy, lactose intolerant, vegan"
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-green-500 transition-colors"
                  value={formData.allergies}
                  onChange={e => setFormData({...formData, allergies: e.target.value})}
                />
              </div>
            </div>

            <button type="submit" className="w-full py-4 rounded-xl font-bold bg-green-600 hover:bg-green-500 transition-all text-white shadow-[0_0_20px_rgba(22,163,74,0.4)] shadow-green-500/20 text-lg">
              Initialize AI Nutritionist
            </button>
          </form>
        )}

        {step === "generating" && (
          <div className="mt-12 text-center animate-in fade-in zoom-in duration-500">
            <h2 className="text-3xl font-bold mb-4">Synthesizing Meal Plan</h2>
            <p className="text-gray-400 mb-8">Agent is querying nutrition databases and scaling macros to your TDEE.</p>
            <AgentTerminal 
              streamUrl="http://localhost:8000/stream-diet-plan"
              requestBody={formData}
              onComplete={handleComplete}
              token={token}
            />
          </div>
        )}

        {step === "result" && result && (
          <div className="animate-in slide-in-from-bottom-8 duration-700">
            <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6 mb-8 flex items-start gap-4">
              <Info className="w-6 h-6 text-green-500 shrink-0 mt-1" />
              <div className="w-full">
                <div className="flex justify-between items-center mb-1">
                  <h3 className="text-lg font-bold text-green-500">Calculated Metabolic Profile</h3>
                  <div className="text-sm font-mono text-gray-400">Base TDEE: {result.tdee} kcal</div>
                </div>
                <p className="text-gray-300 text-sm mb-4">The AI calculated a daily target of {result.macros.daily_calories} kcal based on your {formData.goal} goal. Here is the perfect macro split:</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-blue-500/5 origin-left scale-x-0 group-hover:scale-x-100 transition-transform"></div>
                    <div className="text-xs text-blue-400 uppercase tracking-wider mb-1">Protein</div>
                    <div className="text-xl font-bold">{result.meal_plan.daily_protein}g</div>
                  </div>
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-yellow-500/5 origin-left scale-x-0 group-hover:scale-x-100 transition-transform"></div>
                    <div className="text-xs text-yellow-400 uppercase tracking-wider mb-1">Carbs</div>
                    <div className="text-xl font-bold">{result.meal_plan.daily_carbs}g</div>
                  </div>
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-red-500/5 origin-left scale-x-0 group-hover:scale-x-100 transition-transform"></div>
                    <div className="text-xs text-red-400 uppercase tracking-wider mb-1">Fat</div>
                    <div className="text-xl font-bold">{result.meal_plan.daily_fat}g</div>
                  </div>
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-green-500/5 origin-left scale-x-0 group-hover:scale-x-100 transition-transform"></div>
                    <div className="text-xs text-green-400 uppercase tracking-wider mb-1">Total Calories</div>
                    <div className="text-xl font-bold">{result.meal_plan.daily_calories}</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {result.meal_plan.meals.map((meal: any, idx: number) => (
                <div key={idx} className="bg-white/[0.02] border border-white/10 rounded-2xl p-6 hover:bg-white/[0.04] transition-colors">
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
                    <h4 className="text-xs uppercase text-gray-500 mb-2 font-bold tracking-wider">Ingredients (Scaled)</h4>
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
