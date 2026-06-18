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
    # Load key from .env, NOT hardcoded
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q=artificial-intelligence&apiKey={api_key}"
    response = requests.get(url).json()
    
    # Check if API returned an error
    if response.get('status') != 'ok':
        print(f"Error fetching news: {response.get('message')}")
        return []
        
    articles = response.get('articles', [])[:5]
    return [a['title'] for a in articles]

# 2. THINK: Ask Gemini to summarize
def generate_summary(titles):
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    prompt = f"Read these AI news headlines and write one catchy, viral-style social media post: {titles}"
    
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