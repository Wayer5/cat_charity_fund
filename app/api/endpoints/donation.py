from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationShort
from app.utils.invest import investing_process

router = APIRouter()


@router.post(
    '/',
    response_model=DonationShort,
    response_model_by_alias=True,
    dependencies=[Depends(current_user)],
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Сделать пожертвование."""
    new_donation = await donation_crud.create(donation, session, user)
    await investing_process(investment_object=new_donation, session=session)
    return new_donation


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_by_alias=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперпользователя. Возвращает список всех пожертвований."""
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.get(
    '/my',
    response_model=list[DonationShort],
    dependencies=[Depends(current_user)],
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Вернуть список пожертвований пользователя, выполняющего запрос."""
    donations = await donation_crud.get_donation_by_user(
        session=session, user=user
    )
    return donations