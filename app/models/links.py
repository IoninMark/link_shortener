import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .constants import MAX_URL_LENGTH, SHORT_URL_LENGTH
from app.database import Base


class LinkModel(Base):
    __tablename__ = "links"

    short_url = Column(String(SHORT_URL_LENGTH), primary_key=True, index=True)
    original_url = Column(String(MAX_URL_LENGTH), nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.timezone.utc)
    )
    clicks = Column(Integer, default=0)
