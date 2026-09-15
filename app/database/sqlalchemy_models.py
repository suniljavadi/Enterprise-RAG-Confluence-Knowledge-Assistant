from sqlalchemy import JSON, Date, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DocumentRecord(Base):
    __tablename__ = "documents"
    page_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    space: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    created_date: Mapped[object] = mapped_column(Date)
    updated_date: Mapped[object] = mapped_column(Date)
    url: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSON)
