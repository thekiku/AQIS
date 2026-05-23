from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from src.config.scoring import ADMIN_KEY
from src.controllers.queue_handlers import add_user, get_next_user, get_queue, remove_user, update_user
from src.db.db import get_db
from src.models.schemas import CreateUserRequest, QueueResponse, UpdateUserRequest, UserView

router = APIRouter(tags=["AQIS"])


def require_admin_key(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")) -> None:
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key")


@router.post(
    "/user",
    response_model=UserView,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_key)],
)
def create_user(payload: CreateUserRequest, db: Session = Depends(get_db)) -> UserView:
    return add_user(db, payload)


@router.put("/user/{user_id}", response_model=UserView, dependencies=[Depends(require_admin_key)])
def modify_user(user_id: str, payload: UpdateUserRequest, db: Session = Depends(get_db)) -> UserView:
    return update_user(db, user_id, payload)


@router.get("/queue", response_model=QueueResponse)
def read_queue(db: Session = Depends(get_db)) -> QueueResponse:
    return get_queue(db)


@router.get("/next", response_model=UserView, dependencies=[Depends(require_admin_key)])
def read_next(db: Session = Depends(get_db)) -> UserView:
    return get_next_user(db)


@router.post("/done/{user_id}", response_model=UserView, dependencies=[Depends(require_admin_key)])
def mark_done(user_id: str, db: Session = Depends(get_db)) -> UserView:
    return remove_user(db, user_id)
