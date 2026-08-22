require('dotenv').config({ path: '../.env' });
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');
const Groq = require('groq-sdk');
const { get5StoreRealTimeComparison, getDirectStoreUrl } = require('./live_scraper');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

const apiKey = process.env.GROQ_API_KEY || '';
const groq = apiKey ? new Groq({ apiKey }) : null;
const dataPath = path.join(__dirname, '../data');

// Helper to read legacy CSV if exists
const readCsv = (filename) => {
    return new Promise((resolve, reject) => {
        const results = [];
        const filepath = path.join(dataPath, filename);
        if (!fs.existsSync(filepath)) {
            resolve([]);
            return;
        }
        fs.createReadStream(filepath)
            .pipe(csv())
            .on('data', (data) => results.push(data))
            .on('end', () => resolve(results))
            .on('error', (err) => reject(err));
    });
};

/**
 * Universal Multi-Store Real-Time Search & AI Comparison Endpoint
 * Scrapes & Compares live prices across: Amazon India, Flipkart, Croma, Reliance Digital, Tata CLiQ
 */
app.post('/api/search', async (req, res) => {
    const { query, maxBudget } = req.body;
    if (!query || !query.trim()) {
        return res.status(400).json({ error: "Product search query is required." });
    }

    const cleanQuery = query.trim();
    console.log(`[+] Real-Time Multi-Store Search request for: "${cleanQuery}"`);

    try {
        const result = await get5StoreRealTimeComparison(cleanQuery, maxBudget);
        return res.json(result);
    } catch (err) {
        console.error("Search Error:", err.message);
        res.status(500).json({ error: "Failed to perform real-time comparison search." });
    }
});

/**
 * Live Single Review Sentiment Tester
 */
app.post('/api/analyze', async (req, res) => {
    try {
        const { review } = req.body;
        if (!review) return res.status(400).json({ error: "Review text is required" });

        if (groq) {
            const prompt = `You are an expert consumer insights analyst. Analyze the following product review:
"${review}"

Provide a JSON response strictly with:
- "sentiment_label": "Positive", "Neutral", or "Negative"
- "sentiment_score": float between -1.0 (extremely negative) to 1.0 (extremely positive)
- "key_themes": array of 1-3 short themes

Return ONLY valid JSON.`;

            const chatCompletion = await groq.chat.completions.create({
                messages: [{ role: 'user', content: prompt }],
                model: 'llama-3.1-8b-instant',
                temperature: 0,
                response_format: { type: 'json_object' }
            });

            const result = JSON.parse(chatCompletion.choices[0].message.content);
            return res.json(result);
        } else {
            return res.json({
                sentiment_label: "Positive",
                sentiment_score: 0.85,
                key_themes: ["Good Quality", "Fast Delivery", "Great Value"]
            });
        }
    } catch (err) {
        console.error("Groq Error:", err.message);
        res.status(500).json({ error: 'Failed to analyze review via Groq LLM' });
    }
});

// Legacy routes for backwards compatibility
app.get('/api/brands', async (req, res) => {
    try {
        const data = await readCsv('brand_summary.csv');
        const formatted = data.map(row => {
            const obj = {};
            for (let key in row) {
                obj[key] = isNaN(row[key]) || row[key] === "" ? row[key] : parseFloat(row[key]);
            }
            return obj;
        });
        res.json(formatted);
    } catch (err) {
        res.status(500).json({ error: 'Failed to load brand data' });
    }
});

app.get('/api/product-metrics', async (req, res) => {
    try {
        const data = await readCsv('products.csv');
        const metrics = {};
        
        data.forEach(row => {
            if (!row.brand) return;
            const brand = row.brand;
            if (!metrics[brand]) {
                metrics[brand] = { brand, count: 0, sum_price: 0, sum_discount: 0, sum_rating: 0 };
            }
            metrics[brand].count += 1;
            metrics[brand].sum_price += parseFloat(row.price || 0);
            metrics[brand].sum_discount += parseFloat(row.discount_pct || 0);
            metrics[brand].sum_rating += parseFloat(row.rating || 0);
        });

        const result = Object.values(metrics).map(m => ({
            brand: m.brand,
            avg_price: parseFloat((m.sum_price / m.count).toFixed(2)),
            avg_discount: parseFloat((m.sum_discount / m.count).toFixed(2)),
            avg_rating: parseFloat((m.sum_rating / m.count).toFixed(2)),
            product_count: m.count
        }));

        res.json(result);
    } catch (err) {
        res.status(500).json({ error: 'Failed to load product metrics' });
    }
});

app.get('/api/insights', (req, res) => {
    try {
        const filepath = path.join(dataPath, 'agent_insights.json');
        if (!fs.existsSync(filepath)) {
            res.json(["No insights generated yet. Run the LLM agent."]);
            return;
        }
        const data = fs.readFileSync(filepath, 'utf-8');
        res.json(JSON.parse(data));
    } catch (err) {
        res.status(500).json({ error: 'Failed to load insights' });
    }
});

app.listen(PORT, () => {
    console.log(`Universal Real-Time AI Product Intelligence API running on http://localhost:${PORT}`);
});
