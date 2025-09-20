from fastapi import FastAPI, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Literal
from . import schemas, crud, database, models
from datetime import datetime
import json

app = FastAPI(
    title="가지농장 (Gaji Farm) API",
    version="v1.0.0"
)

@app.on_event("startup")
async def startup():
    # # DB 테이블 자동 생성 (개발용, 필요없음)
    # async with database.engine.begin() as conn:
    #     await conn.run_sync(models.Base.metadata.create_all)
    return

@app.get("/api/v1/districts", response_model=dict)
async def get_districts(db: AsyncSession = Depends(database.get_db)):
    districts = await crud.get_districts(db)
    return {"success": True, "data": {"districts": districts}}

@app.get("/api/v1/categories", response_model=dict)
async def get_categories(db: AsyncSession = Depends(database.get_db)):
    categories = await crud.get_categories(db)
    return {"success": True, "data": {"categories": categories}}

@app.get("/api/v1/agendas", response_model=dict)
async def get_agendas(
    district: Optional[str] = None,
    category: Optional[str] = None,
    impact: Optional[str] = None,
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
    keyword: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sortBy: Optional[str] = "date",
    sortOrder: Optional[str] = "desc",
    db: AsyncSession = Depends(database.get_db)
):
    skip = (page - 1) * limit
    agendas = await crud.get_agendas(db, skip=skip, limit=limit)
    # 실제 필터링/정렬/검색 로직은 추가 구현 필요
    return {
        "success": True,
        "data": {
            "agendas": agendas,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(agendas),
                "totalPages": 1,
                "hasNext": False,
                "hasPrev": False
            }
        }
    }

@app.get("/api/v1/agendas/{agenda_id}", response_model=dict)
async def get_agenda_detail(agenda_id: str, db: AsyncSession = Depends(database.get_db)):
    agenda = await crud.get_agenda_by_id(db, agenda_id)
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
    # 첨부파일, 관련안건, 타임라인, 댓글 등은 상세 구현 필요
    return {"success": True, "data": {"agenda": agenda}}

@app.post("/api/v1/agendas/personalized", response_model=dict)
async def get_personalized_agendas(
    req: schemas.UserPreferences = Body(...),
    limit: int = 10,
    page: int = 1,
    sortBy: Optional[str] = "relevance",
    sortOrder: Optional[str] = "desc",
    db: AsyncSession = Depends(database.get_db)
):
    # 실제 개인화 로직은 추가 구현 필요
    skip = (page - 1) * limit
    agendas = await crud.get_agendas(db, skip=skip, limit=limit)
    return {
        "success": True,
        "data": {
            "agendas": agendas,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(agendas),
                "totalPages": 1,
                "hasNext": False,
                "hasPrev": False
            }
        },
        "message": "개인화된 안건을 성공적으로 조회했습니다"
    }

@app.post("/api/v1/user/preferences", response_model=dict)
async def save_user_preferences(
    prefs: schemas.UserPreferences,
    db: AsyncSession = Depends(database.get_db)
):
    pref = await crud.create_user_preference(db, prefs.district, json.dumps(prefs.interests))
    return {
        "success": True,
        "data": {
            "preferencesId": str(pref.id),
            "savedAt": datetime.utcnow().isoformat() + "Z"
        },
        "message": "사용자 선호도가 저장되었습니다"
    }