import os
import requests
import time
from google.genai import errors
from google import genai
from dotenv import load_dotenv
import sender 

load_dotenv()

# 1. FETCH: Get the news with Links
def get_ai_news():
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q=artificial-intelligence&sortBy=publishedAt&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=10).json()
        if response.get('status') != 'ok':
            print(f"Error fetching news: {response.get('message')}")
            return []
            
        articles = response.get('articles', [])[:3]
        return [f"{a['title']} - Read more: {a['url']}" for a in articles]
        
    except Exception as e:
        print(f"Network error while fetching news: {e}")
        return []

# 2. THINK: Ask Gemini to summarize with prioritized model logic
def generate_summary(titles):
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    prompt = f"""
    You are a professional tech social media curator.
    Headlines to cover: {titles}.
    
    STRICT RULES:
    1. Hook: Start immediately with one punchy, provocative sentence.
    2. Body: Exactly 3 bullet points. Each bullet must be concise (max 15 words) and include the link provided.
    3. Ending: One short, engaging question to drive comments.
    4. NO INTRO, NO OUTRO, NO filler phrases like "Here is a post".
    """
    
    # Priority: Stick with the best model, use others as emergency fallbacks
    model_priority = ['gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-2.5-flash']
    
    for model in model_priority:
        max_retries = 5 
        wait_time = 5 
        
        for attempt in range(max_retries):
            try:
                print(f"Trying {model} (Attempt {attempt + 1}/{max_retries})...")
                response = client.models.generate_content(model=model, contents=prompt)
                
                # --- The Zero-Tolerance Filter ---
                forbidden = ["here is", "sure", "i have", "the post", "viral-style", "catchy", "social media", "hello"]
                clean_lines = [
                    line for line in response.text.split('\n')
                    if not any(f in line.lower() for f in forbidden) and line.strip() != ""
                ]
                
                return "\n".join(clean_lines).strip()
            
            except errors.ServerError:
                wait_time *= 2 # Exponential backoff
                print(f"Model busy, backing off for {wait_time}s...")
                time.sleep(wait_time)
                continue
            except Exception as e:
                print(f"Unexpected error with {model}: {e}")
                break
                
    raise Exception("Critical: All models exhausted.")

# 3. RUN: Execution logic
def main():
    print("Fetching news...")
    news_titles = get_ai_news()
    if not news_titles:
        return

    print("Generating post...")
    post_text = generate_summary(news_titles)
    
    print("Posting to social media...")
    sender.send_telegram(post_text) 
    sender.send_discord(post_text)
    print("Success!")
    
if __name__ == "__main__":
    main()