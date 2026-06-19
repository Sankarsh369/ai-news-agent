import os
import requests
import time
from google.genai import errors
from google import genai
from dotenv import load_dotenv
import sender 

load_dotenv()

# 1. FETCH: Get structured news items
def get_ai_news():
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        print("Configuration Error: NEWS_API_KEY is missing from .env")
        return []
        
    url = f"https://newsapi.org/v2/everything?q=artificial-intelligence&sortBy=publishedAt&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'ok':
            print(f"Error fetching news: {data.get('message')}")
            return []
            
        articles = data.get('articles', [])[:3]
        # Return structured data instead of mashed strings
        return [{"title": a['title'], "link": a['url']} for a in articles if a.get('title') and a.get('url')]
        
    except Exception as e:
        print(f"Network error while fetching news: {e}")
        return []

# 2. THINK: Request optimization with model tiering fallbacks
def generate_summary(article):
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        raise ValueError("Configuration Error: GEMINI_API_KEY is missing from .env")
        
    client = genai.Client(api_key=gemini_key)
    
    prompt = f"""
    Role: You are an expert tech content marketer. Write a highly engaging, scroll-stopping social media post (LinkedIn/X style) based on this article:
    - Title: {article['title']}
    - Link: {article['link']}

    Strictly follow this layout. Do not include any introductory greetings, meta-commentary, or conversational filler. Output only the post.

    [LAYOUT]
    1. Hook: One punchy, high-impact sentence (under 15 words) that hooks the reader or states a bold truth.
    2. [Blank Line]
    3. Core Value: One concise paragraph (strictly under 30 words) explaining *why* this matters to the tech community. Keep it insightful and fluff-free.
    4. [Blank Line]
    5. CTA: Must be exactly "Read more: {article['link']}"

    [STYLE GUIDELINES]
    - Tone: Professional, authoritative, yet forward-looking.
    - Visuals: Use 1–2 relevant tech emojis max to make it scannable, but do not overdo it.
    - No generic hashtags. 
    """

    model_priority = ['gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-2.5-flash']
    
    for model in model_priority:
        max_retries = 5 
        wait_time = 5 
        
        for attempt in range(max_retries):
            try:
                print(f"Trying {model} (Attempt {attempt + 1}/{max_retries})...")
                response = client.models.generate_content(model=model, contents=prompt)
                
                if not response.text:
                    continue
                    
                # --- Guardrail Filter ---
                # We strip out conversational fluff but preserve necessary structural blank lines
                forbidden = ["here is", "sure", "i have", "the post", "viral-style", "catchy", "social media", "hello"]
                lines = response.text.split('\n')
                clean_lines = [line for line in lines if not any(f in line.lower() for f in forbidden)]
                
                final_post = "\n".join(clean_lines).strip()
                if final_post:
                    return final_post
            
            except errors.ServerError:
                print(f"Model busy, backing off for {wait_time}s...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
                continue
            except Exception as e:
                print(f"Unexpected variance with {model}: {e}")
                break  # Shift over to the next tier fallback model
                
    raise Exception("Critical Failure: All AI models exhausted or rate-limited.")

# 3. RUN: Process batch sequences
def main():
    print("Fetching top AI headlines...")
    articles = get_ai_news()
    if not articles:
        print("No articles retrieved. Exiting pipeline.")
        return

    # Loop through each article individually 
    for idx, article in enumerate(articles, 1):
        print(f"\n--- Processing Article [{idx}/{len(articles)}] ---")
        print(f"Target: {article['title']}")
        
        try:
            post_text = generate_summary(article)
            print("Forwarding generated content to channels...")
            
            tg_status = sender.send_telegram(post_text)
            dc_status = sender.send_discord(post_text)
            
            if tg_status and dc_status:
                print("Successfully distributed everywhere!")
            else:
                print(f"Partial Distribution -> Telegram Success: {tg_status} | Discord Success: {dc_status}")
                
        except Exception as e:
            print(f"Execution failed for current node item: {e}")
            
        # Standard safety delay between dispatch calls
        time.sleep(2)
    
if __name__ == "__main__":
    main()