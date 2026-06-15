"""Typed contract shapes crossing the Activist OS boundary.

``UserConcern`` is what a citizen submits. The canonical field is ``concern``;
``text`` and ``message`` are accepted aliases so older callers and the contract
tests keep working.
"""
from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class UserConcern(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    concern: str = Field(
        validation_alias=AliasChoices("concern", "text", "message"),
        min_length=1,
    )
    location: str | None = None
    category: str | None = None
