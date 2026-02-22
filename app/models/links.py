from sqlalchemy import Column, String

from .constants import MAX_URL_LENGTH, SHORT_URL_LENGTH
from database import Base


class LinkModel(Base):
    __tablename__ = "links"

    short_url = Column(String(SHORT_URL_LENGTH), primary_key=True, index=True)
    original_url = Column(String(MAX_URL_LENGTH), nullable=False)
