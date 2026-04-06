from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.crud.meeting import (
    has_meeting_overlap,
    create_meeting,
    get_user_meetings,
    get_meeting_by_id,
    delete_meeting,
)

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post(
    "/",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_meeting(
    meeting_in: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeetingResponse:
    """
    Создать новую встречу.

    Перед созданием встречи выполняется проверка занятости всех участников,
    включая организатора. Если у хотя бы одного пользователя уже есть
    пересекающаяся по времени встреча, создание отменяется.

    :param meeting_in: Данные для создания встречи
    :param db: Сессия базы данных
    :param current_user: Текущий авторизованный пользователь
    :return: Созданная встреча
    """
    participant_ids: List[int] = list(
        set(meeting_in.participant_ids + [current_user.id])
    )

    for user_id in participant_ids:
        if has_meeting_overlap(
            db,
            user_id,
            meeting_in.start_time,
            meeting_in.end_time,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"У пользователя {user_id} уже есть встреча в это время",
            )

    meeting = create_meeting(
        db=db,
        title=meeting_in.title,
        description=meeting_in.description,
        start_time=meeting_in.start_time,
        end_time=meeting_in.end_time,
        organizer_id=current_user.id,
        participant_ids=participant_ids,
    )
    return meeting


@router.get("/my", response_model=list[MeetingResponse])
def get_my_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MeetingResponse]:
    """
    Получить список встреч текущего пользователя.

    Возвращает все встречи, в которых пользователь является
    организатором или участником.

    :param db: Сессия базы данных
    :param current_user: Текущий авторизованный пользователь
    :return: Список встреч пользователя
    """
    return get_user_meetings(db, current_user.id)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Отменить встречу по идентификатору.

    Удаление встречи доступно только ее организатору.
    Если встреча не найдена или пользователь не является организатором,
    возвращается соответствующая ошибка.

    :param meeting_id: Идентификатор встречи
    :param db: Сессия базы данных
    :param current_user: Текущий авторизованный пользователь
    :return: Пустой ответ со статусом 204 No Content
    """
    meeting = get_meeting_by_id(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Встреча не найдена",
        )

    if meeting.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только организатор может отменить встречу",
        )

    delete_meeting(db, meeting)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
