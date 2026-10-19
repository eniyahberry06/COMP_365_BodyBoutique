# The Body Boutique ✨

### A Multi-Attribute Recommendation Engine with Deterministic Clinical Safety Guardrails

**The Body Boutique** is an advanced, lightweight consumer health software platform designed to simplify personalized skincare selection. Developed for the IEEE International Conference on Consumer Electronics (ICCE), this system bridges the gap between complex chemical ingredient terminology and user-friendly digital application design.

---

## System Architecture

The Body Boutique utilizes a transparent, modular architecture split into two core components:

1. **Multi-Attribute Sub-Vector Engine:** Combines a synonym-expanded active ingredient sub-vector (weighted at **70%**) with a sensory texture sub-vector (weighted at **30%**) to rank candidate products from a catalog of $N = 1,138$ commercial items.
2. **Deterministic Clinical Safety Engine:** Grounded in American Academy of Dermatology (AAD) guidelines, this rule-based guardrail intercepts dangerous ingredient combinations (such as mixing retinoids with strong exfoliating acids) to protect user skin health.

---

## Dataset & Characteristics

The system is powered by a curated, structured commercial skincare corpus built specifically for vector search and clinical safety evaluation:

* **Corpus Size:** N = 1,138 commercial skincare products.
* **Metadata Schema:** Each item includes normalized fields for product title, brand, primary category/type, formulation texture (e.g., *gel, serum, cream, lotion*), full INCI ingredient list, and target skin concerns.
* **Synonym & Chemical Mapping:** Integrated mapping table connecting over 50+ casual consumer terms (e.g., *"Vitamin C"*, *"Retinol"*, *"BHA"*) to formal chemical equivalents (e.g., *ascorbic acid, hydroxypinacolone retinoate, salicylic acid*).
* **Clinical Safety Annotations:** Labeled active ingredient interaction flags derived from American Academy of Dermatology (AAD) guidelines for conflict rule validation.

---

## Evaluation & Performance Benchmarks

The system's retrieval performance was rigorously evaluated across an expanded suite of **32 diverse test queries**:

* **Mean nDCG@4:** Achieved **0.892**, significantly outperforming a raw TF-IDF baseline (0.612) and an ingredient-only system (0.814).
* **Statistical Significance:** Paired bootstrap analysis confirms an overall performance gain of +0.280 (95% CI: [+0.182, +0.378]).
* **Clinical Safety Reliability:** Achieved 100% precision and 100% recall across labeled conflict test cases, successfully triggering safety interventions when necessary.

---

## Tech Stack

* **Frontend:** React (Vite, Standard Inline CSS / State Management)
* **Backend:** FastAPI (Python 3.14, Uvicorn, RESTful API)
* **Retrieval & NLP:** Scikit-learn (TF-IDF Vectorization, Custom Synonym & Normalization Pipeline)

---

## Local Installation & Quick Start

### 1. Start the FastAPI Backend

Open a terminal, navigate to your backend directory, install dependencies, and launch Uvicorn:

cd body_boutique_backend
pip install python-dotenv fastapi uvicorn pandas numpy scikit-learn
uvicorn main:app --reload --port 8001

### 2. Start the React Frontend

Open a separate terminal tab, navigate to your frontend directory, install modules, and run the dev server:

cd body_boutique
npm install
npm run dev

Open your browser at `http://localhost:5174` to interact with the application.

---

## Troubleshooting & Common Startup Errors

### 1. `ModuleNotFoundError: No module named 'dotenv'`
* **Cause:** The backend environment is missing the `python-dotenv` package needed to load configuration parameters.
* **Fix:** Ensure your virtual environment is active and run:
  
  pip install python-dotenv

### 2. Port Conflicts (`[Errno 98] Address already in use`)
* **Cause:** Another process is already using port `8001` (backend) or `5174` (frontend).
* **Fix for Backend (Port 8001):**
  * Find and terminate the process holding port 8001:
    
    # macOS/Linux
    lsof -i :8001
    kill -9 <PID>
    
  * Or specify an alternative port when starting Uvicorn:
    
    uvicorn main:app --reload --port 8002
    
* **Fix for Frontend (Port 5174):**
  * Vite will automatically offer to run on the next available port (e.g., `5175`). If it does, ensure your frontend API fetch calls match the active backend port.

### 3. Backend Connection Errors (`Failed to Fetch` / CORS Issues)
* **Cause:** The React frontend is trying to query the API while the FastAPI server is stopped, running on a different port, or blocking CORS requests.
* **Fix:**
  1. Verify that the backend server is running and accessible by visiting `http://127.0.0.1:8001/docs` in your browser.
  2. Confirm that `CORSMiddleware` in `main.py` permits requests from your frontend client origin (`http://localhost:5174` or `http://localhost:5173`).
