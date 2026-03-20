import os
import json
import logging
from typing import Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import aiohttp
from .models import CompanyData
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/Kaletsidikk/openrouter-data-pipeline",
            "Content-Type": "application/json"
        }

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((aiohttp.ClientError, TimeoutError)),
        before_sleep=lambda retry_state: logger.warning(f"Retrying LLM call... Attempt {retry_state.attempt_number}")
    )
    async def extract_entities(self, session: aiohttp.ClientSession, text_content: str) -> Optional[CompanyData]:
        """
        Calls OpenRouter with strict JSON schema instructions and validates the response using Pydantic.
        Implements exponential backoff for rate limits.
        """
        logger.info("Initializing LLM extraction pipeline...")
        
        # We explicitly inject the Pydantic schema into the prompt to guarantee structure
        schema_json = CompanyData.model_json_schema()
        
        prompt = f"""
        You are an elite data extraction agent. 
        Analyze the following scraped web text and extract the requested entities.
        
        CRITICAL RULES:
        1. You must respond ONLY with a raw JSON object. Do not wrap it in markdown block quotes.
        2. The JSON object MUST strictly adhere to this exact JSON Schema:
        {json.dumps(schema_json, indent=2)}
        
        Scraped Text (Truncated):
        {text_content[:4000]}
        """
        
        payload = {
            "model": "google/gemini-pro", # Can easily swap to "anthropic/claude-3-haiku" for complex reasoning
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        
        async with session.post(self.endpoint, headers=self.headers, json=payload) as response:
            response.raise_for_status()
            result = await response.json()
            
            raw_content = result['choices'][0]['message']['content']
            
            try:
                # 1. Parse JSON
                parsed_json = json.loads(raw_content)
                # 2. Validate against Pydantic model (throws ValidationError if LLM hallucinated keys)
                validated_data = CompanyData(**parsed_json)
                logger.info("Successfully validated LLM output against Pydantic schema.")
                return validated_data
                
            except json.JSONDecodeError as e:
                logger.error(f"LLM did not return valid JSON: {e}")
                return None
            except ValidationError as e:
                logger.error(f"LLM output failed strict schema validation: {e}")
                return None
