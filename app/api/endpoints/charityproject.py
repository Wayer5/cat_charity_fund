from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_before_edit,
    check_charity_project_closed,
    check_charity_project_exists,
    check_charity_project_invested_amount,
    check_name_duplicate,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_project_crud
from app.schemas.charityproject import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.utils.invest import investing_process

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_by_alias=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперпользователя. Создаёт благотворительный проект."""
    await check_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(
        obj_in=charity_project,
        session=session,
    )
    await investing_process(
        investment_object=new_project,
        session=session,
    )
    return new_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_by_alias=True,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
) -> CharityProjectDB:
    """
    Только для суперпользователя. Удаляет проект.
    Нельзя удалить проект, в который уже были инвестированы средства,
    его можно только закрыть.
    """
    charity_project = await check_charity_project_exists(
        project_id=project_id,
        session=session
    )
    await check_charity_project_invested_amount(
        project=charity_project,
        session=session
    )
    await check_charity_project_closed(
        project=charity_project,
        session=session
    )
    return await charity_project_crud.remove(
        db_obj=charity_project,
        session=session
    )


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_by_alias=True,
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session)
) -> list[CharityProjectDB]:
    """Возвращает список всех проектов."""
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_by_alias=True,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Только для суперпользователя. Закрытый проект нельзя редактировать,
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    charity_project = await check_charity_project_exists(
        project_id=project_id,
        session=session
    )

    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    await check_charity_project_closed(
        project=charity_project,
        session=session
    )

    await check_charity_project_before_edit(
        project=charity_project,
        obj_in=obj_in,
        session=session
    )

    return await charity_project_crud.update(
        charity_project,
        obj_in,
        session
    )
