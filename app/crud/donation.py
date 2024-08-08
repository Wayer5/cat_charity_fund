from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation
from app.models.user import User
from app.schemas.donation import DonationDB


class CRUDDonation(CRUDBase):

    async def get_donation_by_user(
            self,
            user: User,
            session: AsyncSession
    ) -> list[DonationDB]:
        donations = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)
