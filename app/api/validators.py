from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_project_crud
from app.models.charity_project import CharityProject
from app.schemas.charityproject import CharityProjectUpdate


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    """Проверка на уникальность названия проекта."""
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Проверка на существование проекта в базе данных."""
    project = await charity_project_crud.get_charity_project_by_id(
        project_id, session
    )
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!'
        )
    return project


async def check_charity_project_invested_amount(
        project: CharityProject,
        session: AsyncSession
) -> None:
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )


async def check_charity_project_closed(
        project: CharityProject,
        session: AsyncSession
) -> None:
    """Проверка состояния активности проекта."""
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )


async def check_charity_project_before_edit(
        project: CharityProject,
        obj_in: CharityProjectUpdate,
        session: AsyncSession
) -> CharityProject:
    """Проверка проекта перед редактированием сумм.ß"""
    if obj_in.full_amount is not None:
        if obj_in.full_amount < project.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Нельзя установить значение full_amount'
                'меньше уже вложенной суммы.'
            )
        if obj_in.full_amount == project.invested_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
    return project
