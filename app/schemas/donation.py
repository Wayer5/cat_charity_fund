from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]


class DonationCreate(DonationBase):
    class Config:
        orm_mode = True


class DonationShort(DonationCreate):
    id: int
    create_date: datetime
    full_amount: PositiveInt
    comment: Optional[str]


class DonationDB(DonationShort):
    id: int
    create_date: datetime
    full_amount: PositiveInt
    user_id: int
    invested_amount: int = Field(0)
    fully_invested: bool
    close_date: Optional[datetime]
    comment: Optional[str]
