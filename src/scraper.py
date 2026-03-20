import aiohttp
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class AsyncScraper:
    def __init__(self):
        # We use a persistent session for connection pooling
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    async def fetch_html(self, session: aiohttp.ClientSession, url: str) -> str:
        """Asynchronously fetches and cleans HTML from a given URL."""
        logger.info(f"Fetching: {url}")
        try:
            async with session.get(url, headers=self.headers, timeout=15) as response:
                response.raise_for_status()
                html = await response.text()
                return self._clean_html(html)
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise

    def _clean_html(self, html: str) -> str:
        """Removes noise (scripts, styles, navs) to optimize LLM token usage."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove massive structural elements that rarely contain target entities
        for element in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
            element.decompose()
            
        # Get raw text with normalized whitespace
        text = soup.get_text(separator=' ', strip=True)
        return " ".join(text.split())
