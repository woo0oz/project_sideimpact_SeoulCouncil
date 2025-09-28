from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from . import models

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import tb_meta_info


async def get_districts(db: AsyncSession):
    result = await db.execute(select(models.District))
    return result.scalars().all()

async def get_categories(db: AsyncSession):
    result = await db.execute(select(models.Category))
    return result.scalars().all()

async def get_agendas(db: AsyncSession, skip=0, limit=10):
    result = await db.execute(select(models.Agenda).offset(skip).limit(limit))
    return result.scalars().all()

async def get_agenda_by_id(db: AsyncSession, agenda_id: str):
    result = await db.execute(select(models.Agenda).where(models.Agenda.id == agenda_id))
    return result.scalar_one_or_none()

async def create_user_preference(db: AsyncSession, district: str, interests: str):
    pref = models.UserPreference(district=district, interests=interests)
    db.add(pref)
    await db.commit()
    await db.refresh(pref)
    return pref

# tb_meta_info 관련 CRUD 함수
async def get_tb_meta_info_all(db: AsyncSession):
    result = await db.execute(select(tb_meta_info))
    return result.fetchall()

