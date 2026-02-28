from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.worker import Worker
from ..models.order import Order
from ..schemas.worker import WorkerCreate, WorkerUpdate, WorkerRead
from ..dependencies import get_current_user, role_required


router = APIRouter()


def _can_manage_worker(user, worker: Worker) -> bool:
    # Админ может управлять всеми, мастер — только в своей мастерской.
    role = user.role.name if user.role else None
    if role == "admin":
        return True
    if role == "master" and worker.workshop_id == user.workshop_id:
        return True
    return False


@router.get("/", response_model=list[WorkerRead])
def list_workers(
    db: Session = Depends(get_db),
    user=Depends(role_required("master", "admin")),
):
    """
    Список работников.
    - Мастер видит только работников своей мастерской.
    - Админ видит всех.
    Поле is_assigned вычисляется по наличию незавершённых заявок.
    """
    from ..models.user import User  # локальный импорт, чтобы избежать циклов

    q = db.query(Worker)
    role = user.role.name if user.role else None
    if role == "master":
        q = q.filter(Worker.workshop_id == user.workshop_id)

    workers = q.order_by(Worker.workshop_id, Worker.last_name, Worker.first_name).all()

    # Флаг "назначен" — есть хотя бы одна заявка в статусе не done
    assigned_map: dict[int, bool] = {
        wid: True
        for wid, in db.query(Worker.id)
        .join(Order, Order.worker_id == Worker.id)
        .filter(Order.status != "done")
        .distinct()
        .all()
    }

    result: list[WorkerRead] = []
    for w in workers:
        result.append(
            WorkerRead(
                id=w.id,
                first_name=w.first_name,
                last_name=w.last_name,
                position=w.position,
                workshop_id=w.workshop_id,
                is_active=w.is_active,
                is_assigned=assigned_map.get(w.id, False),
            )
        )
    return result


@router.post("/", response_model=WorkerRead)
def create_worker(
    data: WorkerCreate,
    db: Session = Depends(get_db),
    user=Depends(role_required("master", "admin")),
):
    """
    Создание работника.
    - Для мастера workshop_id всегда совпадает с его мастерской.
    - Админ может указать любую мастерскую.
    """
    role = user.role.name if user.role else None
    workshop_id = data.workshop_id
    if role == "master":
        workshop_id = user.workshop_id
    if workshop_id is None:
        raise HTTPException(400, "Укажите мастерскую для работника")

    worker = Worker(
        first_name=data.first_name,
        last_name=data.last_name,
        position=data.position,
        workshop_id=workshop_id,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)

    return WorkerRead(
        id=worker.id,
        first_name=worker.first_name,
        last_name=worker.last_name,
        position=worker.position,
        workshop_id=worker.workshop_id,
        is_active=worker.is_active,
        is_assigned=False,
    )


@router.patch("/{worker_id}", response_model=WorkerRead)
def update_worker(
    worker_id: int,
    data: WorkerUpdate,
    db: Session = Depends(get_db),
    user=Depends(role_required("master", "admin")),
):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(404, "Работник не найден")
    if not _can_manage_worker(user, worker):
        raise HTTPException(403, "Нет прав на изменение этого работника")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(worker, k, v)
    db.commit()
    db.refresh(worker)

    # пересчитываем флаг назначения
    assigned = (
        db.query(Order)
        .filter(Order.worker_id == worker.id, Order.status != "done")
        .first()
        is not None
    )

    return WorkerRead(
        id=worker.id,
        first_name=worker.first_name,
        last_name=worker.last_name,
        position=worker.position,
        workshop_id=worker.workshop_id,
        is_active=worker.is_active,
        is_assigned=assigned,
    )

