"""Medical citations using Exa search API."""

from typing import Optional
from pydantic import BaseModel
from functools import lru_cache
import httpx

from ..config import get_settings


class Citation(BaseModel):
  """A medical citation."""
  title: str
  url: str
  snippet: str
  source: str  # e.g., "AAP", "CDC", "UpToDate", "PubMed"
  relevance_score: float = 0.0


class CitationResult(BaseModel):
  """Result from a citation search."""
  query: str
  citations: list[Citation]
  summary: Optional[str] = None


class CitationSearch:
  """Search for medical citations using Exa."""

  # Trusted medical sources for pediatrics
  MEDICAL_DOMAINS = [
    "aap.org",           # American Academy of Pediatrics
    "cdc.gov",           # CDC
    "nih.gov",           # NIH
    "pubmed.ncbi.nlm.nih.gov",
    "uptodate.com",
    "aafp.org",          # American Academy of Family Physicians
    "who.int",           # World Health Organization
    "nejm.org",          # New England Journal of Medicine
    "jamanetwork.com",   # JAMA
    "pediatrics.org",    # Pediatrics journal
  ]

  def __init__(self, api_key: str = None):
    settings = get_settings()
    self.api_key = api_key or settings.exa_api_key
    self.base_url = "https://api.exa.ai"

  async def search(
    self,
    query: str,
    num_results: int = 5,
    use_trusted_sources: bool = True,
  ) -> CitationResult:
    """Search for medical citations.

    Args:
      query: The medical topic to search for
      num_results: Number of results to return
      use_trusted_sources: If True, restrict to trusted medical domains

    Returns:
      CitationResult with relevant citations
    """
    if not self.api_key:
      return CitationResult(
        query=query,
        citations=[],
        summary="Citations unavailable (Exa API key not configured)",
      )

    # Build the search query with pediatric context
    search_query = f"pediatric {query} clinical guidelines treatment"

    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json",
    }

    payload = {
      "query": search_query,
      "numResults": num_results,
      "type": "neural",
      "useAutoprompt": True,
      "contents": {
        "text": {"maxCharacters": 500},
      },
    }

    # Restrict to trusted sources if requested
    if use_trusted_sources:
      payload["includeDomains"] = self.MEDICAL_DOMAINS

    async with httpx.AsyncClient(timeout=10.0) as client:
      try:
        response = await client.post(
          f"{self.base_url}/search",
          headers=headers,
          json=payload,
        )
        response.raise_for_status()
        data = response.json()
      except Exception as e:
        return CitationResult(
          query=query,
          citations=[],
          summary=f"Citation search failed: {str(e)}",
        )

    # Parse results
    citations = []
    for result in data.get("results", []):
      url = result.get("url", "")
      source = self._extract_source(url)

      citations.append(Citation(
        title=result.get("title", ""),
        url=url,
        snippet=result.get("text", "")[:300],
        source=source,
        relevance_score=result.get("score", 0.0),
      ))

    return CitationResult(
      query=query,
      citations=citations,
    )

  def _extract_source(self, url: str) -> str:
    """Extract readable source name from URL."""
    source_map = {
      "aap.org": "AAP",
      "cdc.gov": "CDC",
      "nih.gov": "NIH",
      "pubmed": "PubMed",
      "uptodate": "UpToDate",
      "aafp.org": "AAFP",
      "who.int": "WHO",
      "nejm.org": "NEJM",
      "jama": "JAMA",
      "pediatrics.org": "Pediatrics",
    }

    for domain, name in source_map.items():
      if domain in url.lower():
        return name

    return "Medical Literature"


@lru_cache
def get_citation_search() -> CitationSearch:
  """Get cached citation search instance."""
  return CitationSearch()
