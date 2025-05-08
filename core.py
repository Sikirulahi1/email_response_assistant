from pydantic import BaseModel, Field
from typing import Dict, TypedDict, List, Annotated
from .llms import google_llm

model = google_llm

class EmailMessage(BaseModel):
    """Message representing an email"""
    content: str
    sender: str
    timestamp: str
    subject: str

class ResponseMessage(BaseModel):
    """Message representing a response"""
    content: str
    category: str
    timestamp: str


class EmailState(TypedDict):
    """State for the email response assistant."""
    email: EmailMessage
    email_category: str
    response_draft: str
    final_response: ResponseMessage
    messages: List[Dict]