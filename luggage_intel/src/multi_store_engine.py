"""
Universal Multi-Store E-Commerce Comparison & Recommendation Engine
Powered by Groq LLM (Llama 3)
Compares products across: Amazon India, Flipkart, Croma, Reliance Digital, Tata CLiQ
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()
load_dotenv(dotenv_path="../.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def get_llm():
    if not GROQ_API_KEY:
        print("[!] Warning: GROQ_API_KEY not found in environment. Please set it in .env file.")
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=GROQ_API_KEY,
        temperature=0.2,
        max_retries=2
    )

COMPARISON_PROMPT = """
You are an expert consumer shopping advisor and product comparison intelligence agent.
You specialize in Indian e-commerce platforms: Amazon India, Flipkart, Croma, Reliance Digital, and Tata CLiQ.

A user is searching for: "{query}"

Analyze the market options available for this search across the top 5 platforms:
1. Amazon India
2. Flipkart
3. Croma
4. Reliance Digital
5. Tata CLiQ

Perform a comprehensive multi-criteria evaluation:
- Real-world price & discount advantage (find which platform has the absolute best deal)
- Customer review sentiment (analyzing real feedback, reliability, defect rates, build quality)
- Rating volume and consistency
- Value-for-money score (0-100)

Return a STRICT JSON response adhering to this format:
{{
  "query": "{query}",
  "winner": {{
    "title": "Exact Full Name of the #1 Best Product",
    "brand": "Brand Name",
    "best_platform": "Name of Store with Best Deal (Amazon / Flipkart / Croma / Reliance Digital / Tata CLiQ)",
    "best_price": 4999,
    "mrp": 8999,
    "discount_pct": 44,
    "rating": 4.4,
    "review_count": "15,200+",
    "sentiment_score": 0.88,
    "sentiment_label": "Very Positive",
    "value_score": 96,
    "buy_url": "https://www.amazon.in/s?k=...",
    "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500&auto=format&fit=crop&q=60",
    "verdict_headline": "The Undisputed Best All-Rounder in its Class",
    "why_buy": "Detailed reasoning explaining why this product + store combination beats all other alternatives in price, customer satisfaction, and build quality.",
    "pros": ["Key strength 1", "Key strength 2", "Key strength 3"],
    "cons": ["Minor drawback or thing to know"],
    "warranty_delivery": "1 Year Brand Warranty | Free 1-Day Delivery"
  }},
  "runner_ups": [
    {{
      "category": "Best Budget Alternative",
      "title": "Product Title",
      "brand": "Brand",
      "platform": "Flipkart",
      "price": 2999,
      "mrp": 5999,
      "rating": 4.2,
      "value_score": 91,
      "buy_url": "https://www.flipkart.com/search?q=...",
      "highlight": "Lowest price with decent reliability for tight budgets"
    }},
    {{
      "category": "Best Premium / Feature-Packed",
      "title": "Product Title",
      "brand": "Brand",
      "platform": "Croma",
      "price": 8499,
      "mrp": 12999,
      "rating": 4.6,
      "value_score": 93,
      "buy_url": "https://www.croma.com/searchB?q=...",
      "highlight": "Top-tier premium materials and longest durability"
    }}
  ],
  "platform_comparison": [
    {{
      "platform": "Amazon India",
      "product_name": "Product Name on Amazon",
      "price": 4999,
      "mrp": 8999,
      "discount_pct": 44,
      "rating": 4.4,
      "review_count": "15,200",
      "sentiment_score": 0.88,
      "positive_sentiment_pct": 86,
      "delivery_speed": "Prime 1-day",
      "store_rating": 4.7,
      "best_deal_here": true,
      "product_url": "https://www.amazon.in/s?k={query}"
    }},
    {{
      "platform": "Flipkart",
      "product_name": "Product Name on Flipkart",
      "price": 5199,
      "mrp": 8999,
      "discount_pct": 42,
      "rating": 4.3,
      "review_count": "11,800",
      "sentiment_score": 0.82,
      "positive_sentiment_pct": 81,
      "delivery_speed": "2-3 days",
      "store_rating": 4.5,
      "best_deal_here": false,
      "product_url": "https://www.flipkart.com/search?q={query}"
    }},
    {{
      "platform": "Croma",
      "product_name": "Product Name on Croma",
      "price": 5490,
      "mrp": 8999,
      "discount_pct": 39,
      "rating": 4.5,
      "review_count": "3,400",
      "sentiment_score": 0.89,
      "positive_sentiment_pct": 88,
      "delivery_speed": "Express store pickup / 2 days",
      "store_rating": 4.6,
      "best_deal_here": false,
      "product_url": "https://www.croma.com/searchB?q={query}"
    }},
    {{
      "platform": "Reliance Digital",
      "product_name": "Product Name on Reliance Digital",
      "price": 5299,
      "mrp": 8999,
      "discount_pct": 41,
      "rating": 4.2,
      "review_count": "2,100",
      "sentiment_score": 0.80,
      "positive_sentiment_pct": 79,
      "delivery_speed": "2-4 days",
      "store_rating": 4.4,
      "best_deal_here": false,
      "product_url": "https://www.reliancedigital.in/search?q={query}"
    }},
    {{
      "platform": "Tata CLiQ",
      "product_name": "Product Name on Tata CLiQ",
      "price": 5350,
      "mrp": 8999,
      "discount_pct": 40,
      "rating": 4.3,
      "review_count": "1,900",
      "sentiment_score": 0.84,
      "positive_sentiment_pct": 82,
      "delivery_speed": "3-5 days",
      "store_rating": 4.5,
      "best_deal_here": false,
      "product_url": "https://www.tatacliq.com/search/?searchCategory=all&text={query}"
    }}
  ],
  "aspect_ratings": [
    {{"aspect": "Build & Durability", "score": 88, "benchmark": 75}},
    {{"aspect": "Value For Money", "score": 95, "benchmark": 78}},
    {{"aspect": "Performance / Functionality", "score": 90, "benchmark": 80}},
    {{"aspect": "Customer Support & Warranty", "score": 84, "benchmark": 72}},
    {{"aspect": "Design & Aesthetics", "score": 89, "benchmark": 76}}
  ],
  "strategic_insights": [
    "Insight 1 explaining specific pricing trends or discount cycles for this product category.",
    "Insight 2 explaining common customer feedback pitfalls to avoid.",
    "Insight 3 comparing warranty or bank offer advantages between platforms."
  ]
}}

Ensure all prices are realistic current INR figures, links are valid search/product URLs, and comparison is rigorous.
Return ONLY valid JSON.
"""

def compare_product(query: str):
    print(f"\n[+] Searching top 5 e-commerce platforms for: '{query}'")
    print("[+] Querying Groq LLM (Llama 3.3 70B) for deep sentiment & multi-criteria evaluation...")
    
    llm = get_llm()
    prompt = PromptTemplate(
        template=COMPARISON_PROMPT,
        input_variables=["query"]
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({"query": query})
        return result
    except Exception as e:
        print(f"[!] Error during comparison: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Universal AI Multi-Store E-Commerce Comparison")
    parser.add_argument("query", nargs="?", default="Sony WH-1000XM4", help="Product to search and compare")
    args = parser.parse_args()

    data = compare_product(args.query)
    if not data:
        print("[!] Failed to obtain comparison data.")
        return

    winner = data.get("winner", {})
    print("\n" + "="*70)
    print(f"🏆 #1 BEST OVERALL PRODUCT TO BUY: {winner.get('title')}")
    print(f"🏪 Best Store to Buy From: {winner.get('best_platform')}")
    print(f"💰 Best Price: ₹{winner.get('best_price')} (MRP: ₹{winner.get('mrp')}, {winner.get('discount_pct')}% Off)")
    print(f"⭐ Rating: {winner.get('rating')} | Sentiment: {winner.get('sentiment_label')} ({winner.get('sentiment_score')})")
    print(f"🎯 Value Score: {winner.get('value_score')}/100")
    print(f"📝 Verdict: {winner.get('verdict_headline')}")
    print(f"💡 Why Buy: {winner.get('why_buy')}")
    print(f"🔗 Buy Link: {winner.get('buy_url')}")
    print("="*70)

    print("\n📊 Multi-Platform Pricing & Sentiment Comparison:")
    for p in data.get("platform_comparison", []):
        deal_tag = "🌟 BEST DEAL" if p.get("best_deal_here") else ""
        print(f"  • {p.get('platform'):<18}: ₹{p.get('price'):<7} | Rating: {p.get('rating')} | Positive: {p.get('positive_sentiment_pct')}% {deal_tag}")

    print("\n💡 AI Strategic Insights:")
    for idx, ins in enumerate(data.get("strategic_insights", []), 1):
        print(f"  {idx}. {ins}")

if __name__ == "__main__":
    main()
