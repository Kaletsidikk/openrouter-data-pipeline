# Production-Grade LLM Data Normalization Pipeline

A highly scalable, asynchronous data extraction pipeline that bridges traditional web scraping (BeautifulSoup/aiohttp) with Large Language Models via the OpenRouter API.

## Architecture Highlights
* **Asynchronous Execution:** Built on `aiohttp` and `asyncio` to process thousands of URLs concurrently without thread blocking.
* **Strict Validation:** Uses `Pydantic` to enforce strict typing on the LLM's JSON outputs, guaranteeing that downstream databases never receive hallucinated or malformed schema keys.
* **Resiliency:** Integrates the `tenacity` library to provide automatic exponential backoff and retry logic against network timeouts or API rate limits.
* **Token Optimization:** Cleans and sanitizes DOM trees (removing scripts, SVGs, iframes) before sending payloads to the LLM to drastically reduce token costs and improve inference speed.

## Quick Start
```bash
pip install -r requirements.txt
```
Create a `.env` file and add your `OPENROUTER_API_KEY=...`

Run the pipeline:
```bash
python main.py
```

<!-- shark 1 -->
