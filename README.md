# SmartBuy AI — Universal Multi-Platform Product Finder

Search for any product and get a transparent, data-backed pick of the best real listing across Indian e-commerce retailers (Amazon India, Flipkart, Croma, Reliance Digital, Tata CLiQ, and more) — ranked by price, rating, and review volume, using **real live data**, never scraped guesses or fabricated numbers.

The actual project lives in [`luggage_intel/`](./luggage_intel) — see [`luggage_intel/README.md`](./luggage_intel/README.md) for full details: architecture, setup, environment variables, and how to run it locally.

## Stack

- **Backend:** FastAPI (Python) — fetches real listings via SerpApi's Google Shopping engine and computes a transparent composite score (price 45% / rating 35% / review volume 20%)
- **Frontend:** React + Vite — search UI, best-match spotlight, side-by-side comparison table, and charts

## Quick start

```bash
cd luggage_intel
pip install -r requirements.txt
uvicorn main:app --app-dir backend --host 0.0.0.0 --port 5000
```

```bash
cd luggage_intel/frontend
npm install
npm run dev
```

Full setup instructions (including the `SERPAPI_KEY` / `GROQ_API_KEY` environment variables) are in [`luggage_intel/README.md`](./luggage_intel/README.md).
