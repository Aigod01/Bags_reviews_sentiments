

import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant", max_retries=3)

prompt_template = PromptTemplate(
    template=,
    input_variables="review_text",
)

chain = prompt_template | llm | JsonOutputParser()

def analyze_review_with_llm(text):
    if pd.isna(text) or not isinstance(text, str) or not text.strip():
        return {"sentiment_label": "Neutral", "sentiment_score": 0.0, "key_themes": , "aspects": {}}
    
    try:
        result = chain.invoke({"review_text": text})
        return result
    except Exception as e:
        print(f"Error analyzing review: {e}")
        return {"sentiment_label": "Neutral", "sentiment_score": 0.0, "key_themes": , "aspects": {}}

def generate_agent_insights(df_summary):

    summary_json = df_summary.to_json(orient="records")
    insight_prompt = PromptTemplate(
        template=,
        input_variables="data",
    )
    insight_chain = insight_prompt | llm | JsonOutputParser()
    try:
        insights = insight_chain.invoke({"data": summary_json})
        return insights
    except Exception as e:
        print(f"Error generating insights: {e}")
        return "Failed to generate insights due to an error."

def analyze_reviews():
    print(" Loading reviews...")
    try:
        df = pd.read_csv("data/reviews.csv")
    except FileNotFoundError:
        print("Error: data/reviews.csv not found. Please run the scraper first.")
        return

    df"body" = df"body".fillna("")

    print(f" Analyzing {len(df)} reviews using Groq LLM (This may take a moment)...")
    
    results = 
    for idx, row in df.iterrows():
        print(f"  - Processing review {idx1}/{len(df)}")
        analysis = analyze_review_with_llm(row"body")

        row_data = row.to_dict()
        row_data"sentiment_label" = analysis.get("sentiment_label", "Neutral")
        row_data"sentiment_score" = analysis.get("sentiment_score", 0.0)
        
        themes = analysis.get("key_themes", )
        row_data"key_themes" = ", ".join(themes) if isinstance(themes, list) else str(themes)
        
        aspects = analysis.get("aspects", {})
        for aspect in "wheels", "handle", "material", "zipper", "size", "durability", "price", "looks":
            row_dataf"aspect_{aspect}" = aspects.get(aspect) if isinstance(aspects, dict) else None
            
        results.append(row_data)
        time.sleep(0.5)

    df_sentiment = pd.DataFrame(results)
    os.makedirs("data", exist_ok=True)
    df_sentiment.to_csv("data/reviews_sentiment.csv", index=False)
    print("Saved  data/reviews_sentiment.csv")

    print(" Building brand summary...")
    summaries = 
    for brand, group in df_sentiment.groupby("brand"):
        avg_sentiment = round(group"sentiment_score".mean(), 3)
        pos_pct = round((group"sentiment_label" == "Positive").mean() * 100, 1)
        neg_pct = round((group"sentiment_label" == "Negative").mean() * 100, 1)
        
        aspect_avgs = {}
        for aspect in "wheels", "handle", "material", "zipper", "size", "durability", "price", "looks":
            col = f"aspect_{aspect}"
            if col in group and not groupcol.dropna().empty:
                aspect_avgsaspect = round(groupcol.dropna().mean(), 3)
            else:
                aspect_avgsaspect = None

        summaries.append({
            "brand": brand,
            "total_reviews": len(group),
            "avg_sentiment": avg_sentiment,
            "positive_pct": pos_pct,
            "negative_pct": neg_pct,
            **{f"aspect_{k}": v for k, v in aspect_avgs.items()},
        })

    df_summary = pd.DataFrame(summaries)
    df_summary.to_csv("data/brand_summary.csv", index=False)
    print("Saved  data/brand_summary.csv")
    
    print("\n Brand Sentiment Summary ")
    print(df_summary"brand","avg_sentiment","positive_pct","negative_pct".to_string(index=False))

    print("\n Generating GenAI Agent Insights...")
    insights = generate_agent_insights(df_summary)
    with open("data/agent_insights.json", "w") as f:
        json.dump(insights, f, indent=4)
    print("Saved  data/agent_insights.json")
    
    print("\n Agent Insights:")
    for i, ins in enumerate(insights, 1):
        print(f"{i}. {ins}")

if __name__ == "__main__":
    analyze_reviews()
    print("\n Done!")
