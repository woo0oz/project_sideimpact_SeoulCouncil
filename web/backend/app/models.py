from sqlalchemy import Table, Column, String, Date, JSON, PrimaryKeyConstraint, MetaData

metadata = MetaData()

tb_meta_info = Table(
    "tb_meta_info",
    metadata,
    Column("comm_id", String(1000), primary_key=True),
    Column("city", String(1000)),
    Column("district", String(1000)),
    Column("title", String(1000)),
    Column("title_1", String(1000)),
    Column("session", String(1000)),
    Column("ordinal_no", String(1000)),
    Column("sitting", String(1000)),
    Column("date", Date),
    Column("url", String(99999)),
    PrimaryKeyConstraint("comm_id", name="tb_meta_info_pkey")
)

tb_prep_content = Table(
    "tb_prep_content",
    metadata,
    Column("prep_content", JSON)
)

tb_raw_content = Table(
    "tb_raw_content",
    metadata,
    Column("raw_content", JSON)
)

#################################################################
# ORM 방식


# from typing import Optional
# import datetime

# from sqlalchemy import Column, String, Date, PrimaryKeyConstraint, JSON
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# class Base(DeclarativeBase):
#     pass

# class TbMetaInfo(Base):
#     __tablename__ = 'tb_meta_info'
#     __table_args__ = (
#         PrimaryKeyConstraint('comm_id', name='tb_meta_info_pkey'),
#     )

#     comm_id: Mapped[str] = mapped_column(String(1000), primary_key=True)
#     city: Mapped[Optional[str]] = mapped_column(String(1000))
#     district: Mapped[Optional[str]] = mapped_column(String(1000))
#     title: Mapped[Optional[str]] = mapped_column(String(1000))
#     title_1: Mapped[Optional[str]] = mapped_column(String(1000))
#     session: Mapped[Optional[str]] = mapped_column(String(1000))
#     ordinal_no: Mapped[Optional[str]] = mapped_column(String(1000))
#     sitting: Mapped[Optional[str]] = mapped_column(String(1000))
#     date: Mapped[Optional[datetime.date]] = mapped_column(Date)
#     url: Mapped[Optional[str]] = mapped_column(String(99999))

# class TbPrepContent(Base):
#     __tablename__ = 'tb_prep_content'
#     prep_content: Mapped[Optional[dict]] = mapped_column(JSON)

# class TbRawContent(Base):
#     __tablename__ = 'tb_raw_content'
#     raw_content: Mapped[Optional[dict]] = mapped_column(JSON)