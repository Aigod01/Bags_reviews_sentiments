# 🛒 SmartBuy AI — Universal Multi-Platform E-Commerce Product Finder

**SmartBuy AI** lets you search for **any product** and automatically compares real, live listings across Indian e-commerce retailers (Amazon India, Flipkart, Croma, Reliance Digital, Tata CLiQ, and others when they carry the product), picking a **#1 Best Match** using a transparent price + rating + review-volume score.

All comparison data (price, rating, review count, tags/badges, buy link) comes from a real product-data API (SerpApi's Google Shopping engine) — nothing is scraped, guessed, or simulated. If no API key is configured, the app is upfront about it and gives you direct search links to each retailer instead of fake numbers.

---

## 🌟 Key Features

1. **Universal Product Search:** type any product name (e.g. *"Sony WH-1000XM4"*, *"OnePlus Nord CE 4"*, *"Air Fryer 4L"*, *"Safari Trolley Bag"*).
2. **Real live retailer data**, not scraped/estimated — price, MRP/discount, star rating, review count, and badges/tags pulled fresh per search.
3. **🏆 Best Match Spotlight:** picks the strongest overall listing using a transparent composite score (price 45% / rating 35% / review volume 20%), with the "why" spelled out.
4. **Alternative picks:** cheapest other listing found, and highest-rated other listing found.
5. **Side-by-side comparison matrix** of every retailer listing found for that search — price, rating, reviews, tags, and a direct buy link. Listings with missing data are shown as "Unavailable", never filled in with a guess.
6. **Optional budget filter:** prefers listings at or under your budget when you set one.
7. **Live Review Sentiment Tester:** paste any customer review to test sentiment polarity (uses Groq if `GROQ_API_KEY` is set, otherwise a simple keyword heuristic).

---

## 🏗️ Project Architecture

```
luggage_intel/
├── backend/
│   ├── main.py      ← FastAPI API: builds the comparison/winner from real listings
│   └── scraper.py   ← Calls SerpApi's Google Shopping engine for real listings
├── frontend/
│   ├── src/
│   │   ├── App.jsx     ← React UI: search, winner card, comparison matrix, charts
│   │   ├── index.css
│   │   └── main.jsx
│   └── package.json
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Setup & How to Run

### 1. Environment variables
Create a `.env` file in this folder (`luggage_intel/.env`):
```env
# Required for real product data. Free tier: 250 searches/month, no card needed.
# Sign up at https://serpapi.com/users/sign_up, key at https://serpapi.com/manage-api-key
SERPAPI_KEY="your_serpapi_key_here"

# Optional -- used only by the Live Review Sentiment Tester. Without it, that
# feature falls back to a simple keyword-based heuristic instead of an LLM.
GROQ_API_KEY="your_groq_api_key_here"
```
Without `SERPAPI_KEY`, product search still works but returns direct "search this store yourself" links instead of live prices — it's upfront about this in the UI rather than showing fabricated numbers.

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the backend API
```bash
uvicorn main:app --app-dir backend --host 0.0.0.0 --port 5000
```
Runs at `http://localhost:5000`

### 4. Start the frontend
```bash
cd frontend
npm install
npm run dev
```
Opens at `http://localhost:5173`
