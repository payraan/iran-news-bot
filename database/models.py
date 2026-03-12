from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func

from database.connection import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    content = Column(Text)

    source = Column(String)

    url = Column(String, unique=True)

    published_at = Column(DateTime)

    embedding = Column(Text)

    summary = Column(Text)

    sentiment = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
