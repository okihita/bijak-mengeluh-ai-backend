from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Ministry:
    name: str
    score: float
    description: str

@dataclass
class SocialHandleInfo:
    handle: str
    status: str

@dataclass
class ComplaintResult:
    generated_text: str
    suggested_contacts: List[Dict]
    rationale: str
    social_handle_info: Dict[str, str]
