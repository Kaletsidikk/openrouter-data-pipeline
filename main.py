import asyncio
import os
import json
import logging
import aiohttp
from dotenv import load_dotenv

from src.scraper import AsyncScraper
from src.llm_client import OpenRouterClient

# Configure enterprise-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_url(url: str, scraper: AsyncScraper, llm_client: OpenRouterClient, session: aiohttp.ClientSession):
    """Orchestrates the pipeline for a single URL"""
    try:
        # Step 1: Ingestion
        cleaned_text = await scraper.fetch_html(session, url)
        
        # Step 2: Extraction & Validation
        validated_data = await llm_client.extract_entities(session, cleaned_text)
        
        if validated_data:
            return validated_data.model_dump()
        return None
        
    except Exception as e:
        logger.error(f"Pipeline failed for {url}: {e}")
        return None

async def main():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing from environment variables.")

    scraper = AsyncScraper()
    llm_client = OpenRouterClient(api_key)
    
    # We use a list of URLs to demonstrate the async capability
    target_urls = [
        "https://example.com/company-a",
        "https://example.com/company-b"
    ]
    
    logger.info(f"Starting pipeline for {len(target_urls)} URLs...")
    
    # Use a single session for connection pooling across all requests
    async with aiohttp.ClientSession() as session:
        tasks = [process_url(url, scraper, llm_client, session) for url in target_urls]
        results = await asyncio.gather(*tasks)
        
    # Filter out failed extractions
    successful_results = [r for r in results if r is not None]
    
    # Step 3: Persistence
    output_file = "normalized_database.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(successful_results, f, indent=4)
        
    logger.info(f"Pipeline complete. {len(successful_results)} records saved to {output_file}.")

if __name__ == "__main__":
    asyncio.run(main())
