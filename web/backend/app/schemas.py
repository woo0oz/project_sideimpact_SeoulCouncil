from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any

class District(BaseModel):
    id: str
    name: str
    full_name: str
    council_url: str
    is_supported: bool

    class Config:
        orm_mode = True

class Category(BaseModel):
    id: str
    name: str
    emoji: Optional[str]
    description: Optional[str]
    color: Optional[str]
    agenda_count: int

    class Config:
        orm_mode = True

class Agenda(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    impact: Optional[Literal["high", "medium", "low"]]
    impact_description: Optional[str]
    district: str
    date: Optional[str]
    category: Optional[str]
    full_content: Optional[str]
    budget: Optional[str]
    implementation_date: Optional[str]
    related_department: Optional[str]
    view_count: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

class AgendaDetail(Agenda):
    attachments: Optional[List[Dict[str, Any]]] = []
    relatedAgendas: Optional[List[Dict[str, Any]]] = []
    timeline: Optional[List[Dict[str, Any]]] = []
    comments: Optional[Dict[str, Any]] = {}

class UserPreferences(BaseModel):
    district: str
    interests: List[str]

class UserPreferencesOut(BaseModel):
    preferencesId: str
    savedAt: str

class AgendasResponse(BaseModel):
    agendas: List[Agenda]
    message: Optional[str] = None
    total: int

class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int
    hasNext: bool
    hasPrev: bool