from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_project_crud
from app.crud.donation import donation_crud
from app.models import CharityProject, Donation


async def close_project_or_donation(
        obj_in: Union[CharityProject, Donation]
) -> Union[CharityProject, Donation]:
    """
    Закрывает проект или пожертвование, устанавливая сумму вложений
    равной полной сумме, устанавливает флаг полностью инвестированного
    и фиксирует дату закрытия.
    """
    obj_in.invested_amount = obj_in.full_amount
    obj_in.fully_invested = True
    obj_in.close_date = datetime.now()
    return obj_in


async def update_investment(
        project_in: CharityProject,
        donation_in: Donation,
        amount: int,
):
    """
    Обновляет суммы вложений как у получателя, так и у дающего.
    Закрывает проект или пожертвование, если сумма вложений достигает
    полной суммы.
    """
    project_in.invested_amount += amount
    donation_in.invested_amount += amount

    if project_in.invested_amount == project_in.full_amount:
        await close_project_or_donation(project_in)
    if donation_in.invested_amount == donation_in.full_amount:
        await close_project_or_donation(donation_in)


async def investing_money(
        project_in: CharityProject,
        donation_in: Donation,
) -> tuple[Donation, CharityProject]:
    """
    Инвестирует средства от пожертвования в благотворительный проект.
    Определяет, сколько средств можно инвестировать, и обновляет
    соответствующие суммы.
    """
    free_donation_amount = (
        donation_in.full_amount - donation_in.invested_amount
    )
    free_project_amount = project_in.full_amount - project_in.invested_amount

    if free_donation_amount > free_project_amount:
        await update_investment(project_in, donation_in, free_project_amount)
    else:
        await update_investment(project_in, donation_in, free_donation_amount)

    return donation_in, project_in


async def process_investments(
        investment_object: Union[CharityProject, Donation],
        related_objects: list[Union[CharityProject, Donation]],
        session: AsyncSession,
) -> None:
    """
    Обрабатывает инвестиции, распределяя средства между
    проектами и пожертвованиями до тех пор, пока все средства
    не будут распределены или пока все объекты
    не будут полностью инвестированы.
    """
    for related_object in related_objects:
        if investment_object.fully_invested:
            break
        investment_object, related_object = await investing_money(
            related_object, investment_object
        ) if isinstance(
            investment_object, Donation
        ) else await investing_money(
            investment_object, related_object)
        session.add(investment_object)
        session.add(related_object)


async def investing_process(
        investment_object: Union[CharityProject, Donation],
        session: AsyncSession,
) -> Union[Donation, CharityProject]:
    """
    Основной процесс, который выбирает соответствующие объекты
    для инвестирования и распределяет средства между ними.
    """
    if isinstance(investment_object, Donation):
        related_objects = (
            await charity_project_crud.
            get_all_objects_donation_or_charity_projects(
                session
            )
        )
    if isinstance(investment_object, CharityProject):
        related_objects = (
            await donation_crud.get_all_objects_donation_or_charity_projects(
                session
            )
        )

    await process_investments(investment_object, related_objects, session)

    await session.commit()
    await session.refresh(investment_object)
    return investment_object
