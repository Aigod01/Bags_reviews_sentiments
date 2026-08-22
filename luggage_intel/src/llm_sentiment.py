""""""

import pandas as pd
import json
import os
from typing import TypedDict, Annotated
from collections import Counter
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from langgraph.types import Command

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    raise ValueError("  GROQ_API_KEY environment variable not set. Please set it and try again.")

MODEL = "llama-3.3-70b-versatile"

class ReviewState(TypedDict):
    """"""
    review_text: str
    brand: str
    asin: str
    overall_sentiment: dict
    aspect_sentiments: dict
    sarcasm_detected: bool
    overall_failed: bool
    error: str | None

llm = ChatGroq(
    model=MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.3,
    timeout=30
)

def node_extract_overall_sentiment(state: ReviewState) -> Command[ReviewState]:
    """"""
    prompt = PromptTemplate.from_template("""""")
    
    try:
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "review_text": state["review_text"][:2000],
            "brand": state["brand"]
        })

        raw_score = result.get("sentiment_score", 0.0)
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0
        score = max(-1.0, min(1.0, score))

        raw_label = str(result.get("sentiment_label", "Neutral")).strip().lower()
        label_map = {
            "positive": "Positive",
            "negative": "Negative",
            "neutral": "Neutral",
        }
        label = label_map.get(raw_label)
        if label is None:
            if score >= 0.1:
                label = "Positive"
            elif score <= -0.1:
                label = "Negative"
            else:
                label = "Neutral"
        
        state["overall_sentiment"] = {
            "score": score,
            "label": label,
        }
        state["sarcasm_detected"] = result.get("sarcasm_detected", False)
        state["overall_failed"] = False
        
    except Exception as e:
        state["error"] = f"Overall sentiment extraction failed: {str(e)}"
        state["overall_sentiment"] = {"score": 0.0, "label": "Neutral"}
        state["sarcasm_detected"] = False
        state["overall_failed"] = True
    
    return state

def node_extract_aspect_sentiments(state: ReviewState) -> Command[ReviewState]:
    """"""
    aspects = ["wheels", "handle", "material", "zipper", "size", "durability", "price", "looks"]
    
    prompt = PromptTemplate.from_template("""""")
    
    try:
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({"review_text": state["review_text"][:2000]})
        
        aspect_scores = result.get("aspects", {})

        state["aspect_sentiments"] = {
            k: round(v, 3) if v is not None else None 
            for k, v in aspect_scores.items()
        }
        
    except Exception as e:
        existing_error = state.get("error")
        aspect_error = f"Aspect extraction failed: {str(e)}"
        state["error"] = f"{existing_error} | {aspect_error}" if existing_error else aspect_error
        state["aspect_sentiments"] = {aspect: None for aspect in aspects}
    
    return state

def build_sentiment_graph():
    """"""
    graph = StateGraph(ReviewState)

    graph.add_node("extract_overall", node_extract_overall_sentiment)
    graph.add_node("extract_aspects", node_extract_aspect_sentiments)

    graph.add_edge("extract_overall", "extract_aspects")
    graph.add_edge("extract_aspects", END)

    graph.set_entry_point("extract_overall")
    
    return graph.compile()

def analyze_reviews():
    """"""
    
    print(" Loading reviews...")
    df = pd.read_csv("data/reviews.csv")
    df["body"] = df["body"].fillna("")
    
    print(f" Loaded {len(df)} reviews")
    print(" Building sentiment analysis graph...")
    
    sentiment_graph = build_sentiment_graph()

    df["sentiment_score"] = 0.0
    df["sentiment_label"] = "Neutral"
    df["sarcasm_detected"] = False
    
    aspect_cols = ["wheels", "handle", "material", "zipper", "size", "durability", "price", "looks"]
    for aspect in aspect_cols:
        df[f"aspect_{aspect}"] = None

    print("\n Processing reviews by brand...")
    total_processed = 0
    overall_failures = 0
    sample_errors = []

    for brand, group_df in df.groupby("brand"):
        print(f"\n  Processing brand: {brand} ({len(group_df)} reviews)")
        
        for idx, row in group_df.iterrows():
            review_text = str(row["body"]) if pd.notna(row["body"]) else ""

            if not review_text.strip():
                continue

            state = ReviewState(
                review_text=review_text,
                brand=brand,
                asin=row.get("asin", ""),
                overall_sentiment={},
                aspect_sentiments={},
                sarcasm_detected=False,
                overall_failed=False,
                error=None
            )

            result = sentiment_graph.invoke(state)

            df.at[idx, "sentiment_score"] = round(result["overall_sentiment"].get("score", 0.0), 4)
            df.at[idx, "sentiment_label"] = result["overall_sentiment"].get("label", "Neutral")
            df.at[idx, "sarcasm_detected"] = result.get("sarcasm_detected", False)

            total_processed += 1
            if result.get("overall_failed"):
                overall_failures += 1
                if result.get("error") and len(sample_errors) < 3:
                    sample_errors.append(result["error"])

            for aspect in aspect_cols:
                aspect_score = result["aspect_sentiments"].get(aspect)
                df.at[idx, f"aspect_{aspect}"] = aspect_score

            if (group_df.index.tolist().index(idx) + 1) % 10 == 0:
                print(f"    Processed {group_df.index.tolist().index(idx) + 1}/{len(group_df)} reviews")

    if total_processed > 0 and overall_failures == total_processed:
        error_preview = "\n".join(sample_errors) if sample_errors else "No error details captured."
        raise RuntimeError(
            "All overall sentiment API calls failed, so results would be all Neutral/0. "
            "Please check GROQ_MODEL/API availability. Sample errors:\n" + error_preview
        )

    print("\n Saving enriched reviews...")
    df.to_csv("data/reviews_sentiment.csv", index=False)
    print(" Saved  data/reviews_sentiment.csv")

    print("\n Building brand summary...")
    summaries = []
    
    for brand, group in df.groupby("brand"):
        texts = group["body"].tolist()
        
        avg_sentiment = round(group["sentiment_score"].mean(), 3)
        pos_pct = round((group["sentiment_label"] == "Positive").mean() * 100, 1)
        neg_pct = round((group["sentiment_label"] == "Negative").mean() * 100, 1)
        sarcasm_pct = round((group["sarcasm_detected"] == True).mean() * 100, 1)

        positive_reviews = group[group["sentiment_label"] == "Positive"]["body"].tolist()
        negative_reviews = group[group["sentiment_label"] == "Negative"]["body"].tolist()
        
        top_praises = extract_themes_llm(positive_reviews[:20], "positive") if positive_reviews else "N/A"
        top_complaints = extract_themes_llm(negative_reviews[:20], "negative") if negative_reviews else "N/A"

        aspect_avgs = {}
        for aspect in aspect_cols:
            col = f"aspect_{aspect}"
            aspect_avgs[aspect] = round(group[col].dropna().mean(), 3) if col in group.columns else None
        
        summaries.append({
            "brand": brand,
            "total_reviews": len(group),
            "avg_sentiment": avg_sentiment,
            "positive_pct": pos_pct,
            "negative_pct": neg_pct,
            "sarcasm_detected_pct": sarcasm_pct,
            "top_praises": top_praises,
            "top_complaints": top_complaints,
            **{f"aspect_{k}": v for k, v in aspect_avgs.items()},
        })
    
    df_summary = pd.DataFrame(summaries)
    df_summary.to_csv("data/brand_summary.csv", index=False)
    print(" Saved  data/brand_summary.csv")

    print("\n Brand Sentiment Summary (LLM-Powered) ")
    print(df_summary[["brand", "avg_sentiment", "positive_pct", "negative_pct", "sarcasm_detected_pct"]].to_string(index=False))
    print("\n Done! Run dashboard.py next.")

def extract_themes_llm(review_texts, sentiment_type):
    """"""
    if not review_texts:
        return "N/A"
    
    combined_text = " ".join(review_texts[:20])[:3000]
    
    prompt = PromptTemplate.from_template("""""")
    
    try:
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "reviews": combined_text,
            "sentiment_type": sentiment_type
        })
        themes = result.get("themes", [])
        return ", ".join(themes[:5]) if themes else "N/A"
    except Exception as e:
        return f"Error: {str(e)[:50]}"

if __name__ == "__main__":
    print("=" * 60)
    print("LLM-Powered Sentiment Analysis with Groq & LangGraph")
    print("=" * 60)
    analyze_reviews()
