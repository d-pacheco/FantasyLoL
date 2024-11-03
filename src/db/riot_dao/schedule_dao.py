from typing import Optional

from src.common.schemas.riot_data_schemas import Schedule
from src.db.models import ScheduleModel


def get_schedule(session, schedule_name: str) -> Optional[Schedule]:
    db_schedule: Optional[ScheduleModel] = session.query(ScheduleModel)\
        .filter(ScheduleModel.schedule_name == schedule_name)\
        .first()
    if db_schedule is None:
        return None
    else:
        return Schedule.model_validate(db_schedule)


def update_schedule(session, schedule: Schedule) -> None:
    db_schedule = ScheduleModel(**schedule.model_dump())
    session.merge(db_schedule)
    session.commit()
