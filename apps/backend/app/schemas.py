from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel
from typing import Optional
from datetime import date



class District(BaseModel):
    id: str
    name: str
    full_name: str
    council_url: str
    is_supported: bool

    class Config:
        # orm_mode = True
         from_attributes = True

class Category(BaseModel):
    id: str
    name: str
    emoji: Optional[str]
    description: Optional[str]
    color: Optional[str]
    agenda_count: int

    class Config:
        # orm_mode = True
         from_attributes = True

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
    original_url: Optional[str]  # 원문 URL 필드 추가

    class Config:
        # orm_mode = True
         from_attributes = True

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



    class TbMetaInfoSchema(BaseModel):  # tb_meta_info 테이블에 대한 Pydantic 스키마
    
        comm_id: str
        city: Optional[str]
        district: Optional[str]
        title: Optional[str]
        title_1: Optional[str]
        session: Optional[str]
        ordinal_no: Optional[str]
        sitting: Optional[str]
        date: Optional[date]
        url: Optional[str]

    class Config:
        from_attributes = True
