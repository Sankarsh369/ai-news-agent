import os
import requests
import time
from google.genai import errors
from google import genai
from dotenv import load_dotenv
import sender  # Imports send_telegram and send_discord

load_dotenv()

# 1. FETCH: Get the news
def get_ai_news():
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q=artificial-intelligence&sortBy=publishedAt&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=10).json()
        
        # 1. Check for API errors
        if response.get('status') != 'ok':
            print(f"Error fetching news: {response.get('message')}")
            return []
            
        # 2. Extract articles with error handling
        articles = response.get('articles', [])[:3]
        if not articles:
            return []
            
        # 3. Format with titles AND links
        return [f"{a['title']} - Read more: {a['url']}" for a in articles]
        
    except Exception as e:
        print(f"Network error while fetching news: {e}")
        return []
    
# 2. THINK: Ask Gemini to summarize
def generate_summary(titles):
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))    
    # We now strictly define the Output Format
    prompt = f"""
    You are an expert social media curator. 
    Take these headlines: {titles}.

    Write a high-engagement post.
    STRICT FORMATTING RULES:
    - START IMMEDIATELY with the Hook. DO NOT include "Here is a post", "Sure", or any introductory filler.
    - Hook: One punchy, provocative sentence.
    - Body: Exactly 3 bullet points. Max 15 words per bullet. Use emojis at the start of each bullet.
    - Ending: One short, engaging question.
    - Style: No 'AI-speak' like 'we have entered the era'. Use human, conversational language.
    """
    model_list = ['gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-2.5-flash']
        
    for model in model_list:
        max_retries = 3
        wait_time = 2 
        
        for attempt in range(max_retries):
            try:
                print(f"Trying model: {model} (Attempt {attempt + 1})...")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text 
            
            except errors.ServerError:
                wait_time *= 2 
                print(f"Model {model} busy, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue 
            except Exception as e:
                print(f"Unexpected error with {model}: {e}")
                break 
                
    raise Exception("All models exhausted after multiple retries.")
            
# 3. RUN: Put it all together
def main():
    print("Fetching news automatically...")
    news_titles = get_ai_news() 
    
    if not news_titles:
        print("No news found today.")
        return

    print("Generating post...")
    post_text = generate_summary(news_titles)
    
    print("Posting to social media...")
    # Using sender. to access the functions from your sender.py file
    sender.send_telegram(post_text) 
    sender.send_discord(post_text)
    print("Done!")
    
if __name__ == "__main__":
    main()