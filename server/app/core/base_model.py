import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class UUIDBaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    state: bool = Field(default=True)

    created_date: datetime = Field(default_factory=datetime.utcnow)
    modified_date: datetime = Field(default_factory=datetime.utcnow)
    deleted_date: Optional[datetime] = None
