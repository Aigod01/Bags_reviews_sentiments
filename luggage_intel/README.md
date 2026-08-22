# 🛒 SmartBuy AI — Universal Multi-Platform E-Commerce Product Finder & Recommender

**SmartBuy AI** transforms product shopping by letting you search for **ANY product** (electronics, luggage, appliances, fashion, furniture, etc.), automatically comparing options across India's **Top 5 E-Commerce Platforms** (Amazon India, Flipkart, Croma, Reliance Digital, and Tata CLiQ), and using an **LLM Multi-Criteria Decision Model (MCDM)** to crown the **#1 Overall Best Product & Store Deal to Buy**.

---

## 🌟 Key Features

1. **Universal Product Search:** Type any product name or category (e.g. *"Sony WH-1000XM4"*, *"Safari Thorium 65cm Luggage"*, *"OnePlus Nord CE 4"*, *"Air Fryer 4L"*).
2. **Top 5 E-Commerce Comparison:**
   - 🟠 **Amazon India**
   - 🔵 **Flipkart**
   - 🟢 **Croma**
   - 🔴 **Reliance Digital**
   - 🟣 **Tata CLiQ**
3. **🏆 #1 Best Choice Spotlight (Winner Verdict):**
   - Crowns the undisputed best product with the best store deal.
   - Shows lowest direct price, verified customer rating, positive sentiment %, and Value-for-Money Index (out of 100).
   - "Why You Should Buy This" comprehensive AI reasoning.
   - Key Strengths (Pros) & Watch-outs (Cons).
   - Direct "Buy Now" button opening the store deal.
4. **Alternative Category Picks:**
   - 🥈 *Best Budget Alternative* (for tight budgets).
   - ⭐ *Best Premium / Feature-Packed Pick* (for max durability & features).
5. **Side-by-Side 5-Store Comparison Matrix:**
   - Transparent tabular comparison of Price, Rating, Review Volume, Positive Sentiment %, Delivery Speed, and Store Links.
6. **Deep Visual Analytics & Charts:**
   - Multi-Store Price Comparison Bar Chart.
   - Positive Review Sentiment (%) Comparison.
   - Aspect-Level Quality Breakdown (Build, Value, Performance, Support, Design).
7. **Live Review Sentiment Tester:**
   - Paste any customer review to test real-time sentiment polarity and extract key themes.

---

## 🏗️ Project Architecture

```
luggage_intel/
├── backend/
│   ├── index.js              ← Node/Express API with Universal Groq LLM Search Engine
│   ├── package.json
├── frontend/
│   ├── src/
│   │   ├── App.jsx           ← Modern React UI with Winner Banner & Multi-Store Matrix
│   │   ├── index.css         ← Glassmorphism & Responsive Design
│   │   └── main.jsx
│   ├── package.json
├── src/
│   ├── multi_store_engine.py ← Python CLI for multi-store comparison
│   ├── scraper.py            ← Selenium scraper for Amazon India datasets
│   ├── sentiment.py          ← Batch LLM sentiment pipeline
│   └── llm_sentiment.py      ← LangGraph sentiment workflow
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Setup & How to Run

### 1. Environment Variables
Create a `.env` file in the root folder or `backend/` directory:
```env
GROQ_API_KEY="your_groq_api_key_here"
```
*(Note: If no API key is provided, the engine will automatically use resilient fallback simulation so all features work seamlessly).*

---

### 2. Start Backend API
```bash
cd backend
npm install
node index.js
```
Runs at `http://localhost:5000`

---

### 3. Start Frontend UI
```bash
cd frontend
npm install
npm run dev
```
Opens in your browser at `http://localhost:5173`

---

### 4. (Optional) Run CLI Comparison in Python
```bash
python src/multi_store_engine.py "Sony WH-1000XM4"
```
