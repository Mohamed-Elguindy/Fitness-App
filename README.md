# ⚡ Agentic Fitness Coach

A premium, production-grade AI fitness and nutrition platform. This application combines a **Next.js** frontend with a **FastAPI** backend to deliver hyper-personalized training programs, diet plans, and intelligent conversational coaching using Google's Gemini models and advanced RAG (Retrieval-Augmented Generation).

---

## 🚀 Key Features

*   **Intelligent RAG Coach**: Ask fitness, nutrition, or mentality questions. The backend dynamically routes your question to the correct vector knowledge base (using HuggingFace embeddings) to provide scientifically accurate answers.
*   **Hyper-Personalized Diet Plans**: Generates exact, macro-perfect daily meal plans scaled precisely to your metabolic rate (TDEE), goals, and dietary restrictions.
*   **Dynamic Training Programs**: Builds structured weekly training regimes based on your available days, equipment, and injury history.
*   **Modern Auth & Database**: Uses **Clerk** for secure JWT authentication and **Neon (PostgreSQL)** for persisting your generated diets and programs.
*   **Beautiful UI**: A sleek, glassmorphic Next.js frontend built with React, Tailwind CSS, and Framer Motion.

---

## 🏗️ Architecture Stack

### Frontend (`/web`)
*   **Framework**: Next.js 16.3 (App Router, Turbopack)
*   **Styling**: Tailwind CSS + custom glassmorphic aesthetics
*   **Authentication**: Clerk (React SDK)
*   **Icons & Animation**: Lucide React, Framer Motion

### Backend (`/agentic-fitness-app`)
*   **Framework**: FastAPI
*   **Database**: Neon PostgreSQL + SQLAlchemy ORM
*   **AI/LLM**: Google Gemini (`models/gemini-1.5-flash` via `google-generativeai`)
*   **Structured Outputs**: `instructor` for strict JSON response parsing
*   **RAG Engine**: LlamaIndex + `sentence-transformers/all-MiniLM-L6-v2` (pure Python vector search, highly compatible)

---

## 💻 Local Setup Instructions

This project is built to run on almost any device. We have specifically stripped out legacy libraries that require complex C++ build tools to ensure a smooth setup across Windows, Mac, and Linux.

### 1. Backend Setup (FastAPI)

1. Open a terminal and navigate to the root directory.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install the dependencies (optimized for cross-platform compatibility):
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file in the `agentic-fitness-app/` directory with the following keys:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   DATABASE_URL=your_neon_postgres_url_here
   ```
5. Run the database migrations to set up your tables:
   ```bash
   cd agentic-fitness-app
   python reset_db_script.py
   ```
6. Start the FastAPI backend:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

### 2. Frontend Setup (Next.js)

1. Open a **second** terminal window and navigate to the frontend directory:
   ```bash
   cd web
   ```
2. Install the Node.js packages:
   ```bash
   npm install
   ```
3. Set up your `.env.local` file in the `web/` directory with your Clerk keys:
   ```env
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   CLERK_SECRET_KEY=your_clerk_secret_key
   ```
4. Start the frontend development server:
   ```bash
   npm run dev
   ```

### 3. Open the App
Visit [http://localhost:3000](http://localhost:3000) in your browser, log in with Clerk, and start building your ultimate physique!

---

## 🔒 Security Notes
The backend enforces secure data ownership. All history endpoints decode the Clerk JWT Bearer token to extract the user's secure `clerk_id`, ensuring that your diet plans and training programs are strictly private.
