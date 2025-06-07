from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
