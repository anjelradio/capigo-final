from sqlmodel import Field, Index, text

from app.core.base_model import UUIDBaseModel


class Problem(UUIDBaseModel, table=True):
    __tablename__ = "problem"
    __table_args__ = (
        Index(
            "uq_problem_slug_active",
            "slug",
            unique=True,
            sqlite_where=text("state = 1"),
            postgresql_where=text("state = true"),
        ),
    )

    name: str = Field(min_length=3, max_length=120)
    slug: str = Field(min_length=3, max_length=140, index=True)
    description: str | None = Field(default=None, min_length=5, max_length=600)
