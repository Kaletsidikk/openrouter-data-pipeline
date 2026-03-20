from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class CompanyData(BaseModel):
    """
    Pydantic schema to enforce strict typing and validation on the LLM's JSON output.
    This guarantees that downstream databases never receive malformed data.
    """
    company_name: str = Field(description="The official registered name of the company")
    industry: str = Field(description="The primary industry or sector the company operates in")
    contact_email: Optional[EmailStr] = Field(default=None, description="The primary contact email address, if available")
    key_technologies: List[str] = Field(default_factory=list, description="A list of technologies or software the company uses")
    confidence_score: float = Field(ge=0.0, le=1.0, description="The LLM's confidence in the extracted data (0.0 to 1.0)")
