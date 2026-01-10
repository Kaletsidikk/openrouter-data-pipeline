# OpenRouter LLM Data Normalization Pipeline

An automated data extraction pipeline that bridges traditional web scraping (BeautifulSoup) with Large Language Models via the OpenRouter API.

## Architecture
1. **Ingestion:** Uses `requests` and `BeautifulSoup` to fetch and sanitize raw HTML from unstructured web sources.
2. **LLM Parsing:** Feeds the cleaned text into OpenRouter's API using strict prompt engineering to force structured JSON outputs.
3. **Validation & Normalization:** Ensures the extracted entities match the required database schema before saving to JSON.

## Tech Stack
- Python 3.10+
- BeautifulSoup4
- OpenRouter API (Gemini/Claude/GPT)
- JSON Schema Validation

## Usage
Add your `OPENROUTER_API_KEY` to `.env` and run:
```bash
pip install -r requirements.txt
python extractor.py
```
