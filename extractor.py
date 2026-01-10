import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def fetch_html(url: str) -> str:
    print(f"Fetching content from: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Clean up scripts and styles to save tokens
    for script in soup(["script", "style", "nav", "footer"]):
        script.extract()
    
    return soup.get_text(separator=' ', strip=True)

def extract_entities_with_llm(text_content: str):
    print("Calling OpenRouter LLM for entity extraction...")
    
    prompt = f"""
    You are an expert data extractor. Given the following text scraped from a website, 
    extract the company name, industry, and contact email. 
    You must respond ONLY with a valid JSON object matching this schema:
    {{
        "company_name": "string",
        "industry": "string",
        "contact_email": "string or null"
    }}
    
    Text to process:
    {text_content[:2000]}
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/Kaletsidikk/openrouter-data-pipeline",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "google/gemini-pro", 
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    result = response.json()
    
    try:
        content = result['choices'][0]['message']['content']
        structured_data = json.loads(content)
        return structured_data
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Failed to parse LLM response: {e}")
        return None

if __name__ == "__main__":
    test_url = "https://example.com"
    try:
        raw_text = fetch_html(test_url)
        data = extract_entities_with_llm(raw_text)
        
        with open("extracted_data.json", "w") as f:
            json.dump(data, f, indent=4)
            
        print("Data successfully extracted and saved to extracted_data.json")
    except Exception as e:
        print(f"Extraction failed: {e}")
