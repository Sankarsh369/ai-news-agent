# AI News Agent 🤖
An automated, resilient AI pipeline that curates AI news and delivers it to Telegram and Discord.

## Features
- **Automated Curation:** Fetches real-time AI news using NewsAPI.
- **AI-Powered Insights:** Uses Google Gemini 3.5 Flash for high-quality summarization.
- **Resilient Pipeline:** Implements exponential backoff for API reliability.
- **Cloud-Native:** Deployed via GitHub Actions for 24/7 automation.

## Tech Stack
- **Languages:** Python
- **APIs:** NewsAPI, Google Gemini API
- **Infrastructure:** GitHub Actions (CI/CD)

## How it works
1. **Fetch:** Retrieves latest headlines.
2. **Transform:** Gemini generates human-like, punchy social media hooks.
3. **Delivery:** Sends content via Webhooks/Bots to Telegram/Discord.