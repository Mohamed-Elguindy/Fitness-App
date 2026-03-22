import streamlit as st
import requests

st.set_page_config(
    page_title="AI Fitness Coach",
    page_icon="💪",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #0a0a0a; color: #f0f0f0; }
    
    .stApp { background-color: #0a0a0a; }
    
    h1, h2, h3 { 
        font-family: 'Bebas Neue', sans-serif !important;
        letter-spacing: 2px;
        color: #ff4500 !important;
    }
    
    .stButton > button {
        background-color: #ff4500;
        color: white;
        border: none;
        border-radius: 0px;
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
        font-size: 18px;
        padding: 12px 30px;
        width: 100%;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #cc3700;
        transform: translateY(-2px);
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background-color: #1a1a1a !important;
        color: #f0f0f0 !important;
        border: 1px solid #333 !important;
        border-radius: 0px !important;
    }
    
    .stSelectbox > div > div > div {
        color: #f0f0f0 !important;
    }

    div[data-testid="stSelectbox"] > div {
        background-color: #1a1a1a !important;
        border: 1px solid #333 !important;
    }
    
    .metric-card {
        background-color: #1a1a1a;
        border-left: 4px solid #ff4500;
        padding: 20px;
        margin: 10px 0;
    }
    
    .meal-card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-top: 3px solid #ff4500;
        padding: 20px;
        margin: 10px 0;
    }
    
    .exercise-card {
        background-color: #1a1a1a;
        border: 1px solid #222;
        padding: 15px;
        margin: 8px 0;
    }
    
    .day-header {
        background-color: #ff4500;
        color: white !important;
        padding: 10px 20px;
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
        font-size: 20px;
        margin: 20px 0 10px 0;
    }

    .chat-message-user {
        background-color: #1a1a1a;
        border-left: 4px solid #ff4500;
        padding: 15px;
        margin: 10px 0;
        color: #f0f0f0;
    }
    
    .chat-message-coach {
        background-color: #111;
        border-left: 4px solid #444;
        padding: 15px;
        margin: 10px 0;
        color: #f0f0f0;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #0a0a0a;
        border-bottom: 2px solid #ff4500;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
        font-size: 16px;
        color: #666 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #ff4500 !important;
        border-bottom: 2px solid #ff4500;
    }

    .stSlider > div > div > div {
        background-color: #ff4500 !important;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

st.markdown("# 💪 AI FITNESS COACH")
st.markdown("##### Your personalized strength, nutrition & mentality engine")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🧠  COACH", "🥗  DIET PLAN", "🏋️  TRAINING PROGRAM"])

# ─── TAB 1: COACH ───────────────────────────────────────────────
with tab1:
    st.markdown("### ASK YOUR COACH")
    st.markdown("Ask anything about fitness, nutrition, or mental toughness.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message-user">🙋 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-coach">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    query = st.text_input("Your question", placeholder="e.g. I feel like skipping the gym today...")

    if st.button("ASK COACH", key="coach_btn"):
        if query:
            with st.spinner("Coach is thinking..."):
                try:
                    response = requests.post(f"{API_URL}/coach", json={"query": query})
                    answer = response.json()["response"]
                    st.session_state.chat_history.append({"role": "user", "content": query})
                    st.session_state.chat_history.append({"role": "coach", "content": answer})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.button("CLEAR CHAT", key="clear_btn"):
        st.session_state.chat_history = []
        st.rerun()

# ─── TAB 2: DIET PLAN ───────────────────────────────────────────
with tab2:
    st.markdown("### BUILD YOUR DIET PLAN")

    col1, col2 = st.columns(2)

    with col1:
        weight = st.number_input("Weight (kg)", min_value=40, max_value=200, value=80)
        height = st.number_input("Height (cm)", min_value=140, max_value=220, value=175)
        age = st.number_input("Age", min_value=14, max_value=80, value=25)
        gender = st.selectbox("Gender", ["male", "female"])

    with col2:
        activity = st.selectbox("Activity Level", ["sedentary", "light", "moderate", "active", "very_active"])
        goal = st.selectbox("Goal", ["bulk", "cut", "maintain"])
        intensity = st.selectbox("Intensity", ["lean", "moderate", "aggressive"])
        meals = st.slider("Meals per day", min_value=2, max_value=6, value=3)
        budget = st.selectbox("Budget", ["low", "moderate", "high"])

    if st.button("GENERATE DIET PLAN", key="diet_btn"):
        with st.spinner("Building your personalized meal plan..."):
            try:
                payload = {
                    "weight_kg": weight,
                    "height_cm": height,
                    "age": age,
                    "gender": gender,
                    "activity_level": activity,
                    "goal": goal,
                    "intensity": intensity,
                    "meals_per_day": meals,
                    "budget": budget
                }
                response = requests.post(f"{API_URL}/diet-plan", json=payload)
                data = response.json()

                st.markdown("### YOUR STATS")
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("TDEE", f"{data['tdee']} kcal")
                c2.metric("Calories", f"{data['macros']['daily_calories']} kcal")
                c3.metric("Protein", f"{data['macros']['protein_g']}g")
                c4.metric("Carbs", f"{data['macros']['carbs_g']}g")
                c5.metric("Fat", f"{data['macros']['fat_g']}g")

                st.markdown("### YOUR MEAL PLAN")
                for meal in data["meal_plan"]["meals"]:
                    st.markdown(f'<div class="day-header">{meal["meal_name"]} — {meal["timing"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="meal-card">', unsafe_allow_html=True)

                    for food in meal["foods"]:
                        st.markdown(f"**{food['food'].title()}** — {food['grams']}g | {food['calories']} kcal | P: {food['protein']}g | C: {food['carbs']}g | F: {food['fat']}g")

                    totals = meal["meal_totals"]
                    st.markdown(f"---")
                    st.markdown(f"**Meal Total** — {totals['calories']} kcal | P: {totals['protein']}g | C: {totals['carbs']}g | F: {totals['fat']}g")
                    st.markdown('</div>', unsafe_allow_html=True)

                daily = data["meal_plan"]["daily_totals"]
                st.markdown("### DAILY TOTALS")
                st.markdown(f'<div class="metric-card">Calories: {daily["calories"]} kcal | Protein: {daily["protein"]}g | Carbs: {daily["carbs"]}g | Fat: {daily["fat"]}g</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

# ─── TAB 3: TRAINING PROGRAM ────────────────────────────────────
with tab3:
    st.markdown("### BUILD YOUR TRAINING PROGRAM")

    col1, col2 = st.columns(2)

    with col1:
        minutes = st.slider("Available minutes per session", min_value=30, max_value=120, value=60, step=15)
        days = st.slider("Days per week", min_value=1, max_value=6, value=4)

    with col2:
        train_goal = st.selectbox("Training Goal", ["hypertrophy", "strength"])
        equipment = st.selectbox("Equipment", ["gym", "home"])

    if st.button("GENERATE TRAINING PROGRAM", key="program_btn"):
        with st.spinner("Building your training program..."):
            try:
                payload = {
                    "available_minutes": minutes,
                    "goal": train_goal,
                    "days_per_week": days,
                    "equipment": equipment
                }
                response = requests.post(f"{API_URL}/training-program", json=payload)
                data = response.json()

                program = data["program"]
                volume = data["volume_settings"]

                st.markdown(f"### {program['program_name'].upper()}")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Days/Week", volume["available_minutes"])
                c2.metric("Sets/Exercise", volume["sets_per_exercise"])
                c3.metric("Rep Range", volume["rep_range"])
                c4.metric("Rest", f"{volume['rest_between_sets_seconds']}s")

                for session in program["sessions"]:
                    st.markdown(f'<div class="day-header">{session["day"]} — {session["focus"].upper()}</div>', unsafe_allow_html=True)

                    for ex in session["exercises"]:
                        st.markdown(f'<div class="exercise-card"><strong>{ex["exercise"].upper()}</strong> — {ex["sets"]} sets × {ex["reps"]} reps | Rest: {ex["rest_seconds"]}s<br><small>{ex.get("notes", "")}</small></div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

